"""도매꾹 상품 URL에서 정보만 조회한다. 등록·주문 요청은 없다."""

import json
import re
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlsplit

from pydantic import JsonValue, ValidationError

from app.adapters.http import SourceHTTP
from app.adapters.sources.parsing import (
    ImageParser,
    boolean_value,
    description_text,
    integer_value,
    money_value,
    object_value,
    quantity_tiers,
    text_value,
)
from app.core.config import Config
from app.core.security import redact
from app.schemas.product import (
    FetchResult,
    ImageRef,
    Issue,
    NormalizeResult,
    ProductData,
    ProductOption,
    RawProduct,
    Shipping,
)

# [CHANNEL-SPEC] 도매꾹 상품상세정보 4.6 — endpoint와 응답 변경 시 이 파일 수정
API_ENDPOINT = "https://www.domeggook.com/ssl/api/"
API_VERSION = "4.6"
ALLOWED_HOSTS = {"domeggook.com", "www.domeggook.com", "mobile.domeggook.com"}
ITEM_PATH = re.compile(r"^/(\d+)/?$")
MOBILE_PATHS = {"/main/item/itemView.php", "/main/item/itemView", "/main/item/itemView.php/"}


def item_number(url: str) -> str | None:
    try:
        parsed = urlsplit(url)
        if parsed.scheme not in {"http", "https"} or parsed.hostname not in ALLOWED_HOSTS:
            return None
        if parsed.username or parsed.password or parsed.port not in {None, 80, 443}:
            return None
        match = ITEM_PATH.fullmatch(parsed.path)
        if match:
            return match.group(1)
        if parsed.path in MOBILE_PATHS:
            values = parse_qs(parsed.query).get("no", [])
            if len(values) == 1 and values[0].isascii() and values[0].isdigit():
                return values[0]
    except ValueError:
        return None
    return None


def collect_images(item: dict[str, JsonValue], url: str) -> list[ImageRef]:
    thumb = object_value(item.get("thumb"))
    representative = text_value(thumb.get("original")) or text_value(thumb.get("large"))
    contents = object_value(object_value(item.get("desc")).get("contents"))
    parser = ImageParser(url)
    parser.feed(text_value(contents.get("item")) or "")
    urls = ([representative] if representative else []) + parser.urls
    return [
        ImageRef(
            source_url=value,
            role="representative" if value == representative else "detail",
            sort_order=index,
        )
        for index, value in enumerate(dict.fromkeys(urls))
    ]


# [CHANNEL-SPEC] selectOpt의 옵션 금액 해석은 별도 명세 검증 전 null로 유지
def collect_options(value: JsonValue | None, issues: list[Issue]) -> list[ProductOption] | None:
    if value in (None, ""):
        return None
    try:
        decoded: JsonValue = json.loads(value) if isinstance(value, str) else value
    except (ValueError, TypeError):
        issues.append(
            Issue(code="option_format", field="options", message="옵션 형식을 확인하세요.")
        )
        return None
    choices = object_value(object_value(decoded).get("data"))
    if not choices:
        return None
    issues.append(
        Issue(code="option_price", field="options", message="옵션 단가 해석은 확인 필요입니다.")
    )
    return [
        ProductOption(
            source_option_id=key,
            label=text_value(object_value(row).get("name")),
            stock_quantity=integer_value(object_value(row).get("qty")),
        )
        for key, row in choices.items()
    ]


def build_product(raw: RawProduct) -> ProductData:
    item = object_value(raw.payload.get("domeggook")) or raw.payload
    basis, price, quantity = (object_value(item.get(key)) for key in ("basis", "price", "qty"))
    delivery = object_value(item.get("deli"))
    dome_delivery = object_value(delivery.get("dome"))
    description = object_value(item.get("desc"))
    allowed = object_value(description.get("license")).get("usable")
    detail_html = text_value(object_value(description.get("contents")).get("item"))
    issues: list[Issue] = []
    product = ProductData(
        source=raw.source,
        source_url=raw.source_url,
        fetched_at=raw.fetched_at,
        acquisition_mode=raw.acquisition_mode,
        raw=raw.payload,
        source_product_id=str(basis["no"]) if basis.get("no") is not None else None,
        name=text_value(basis.get("title")),
        currency="KRW",
        wholesale_price=money_value(price.get("dome")),
        price_tiers=quantity_tiers(price.get("dome")),
        minimum_order_quantity=integer_value(quantity.get("domeMoq")),
        purchase_unit=integer_value(quantity.get("domeUnit")),
        maximum_order_quantity=integer_value(quantity.get("domeLoq")),
        stock_quantity=integer_value(quantity.get("inventory")),
        options=collect_options(item.get("selectOpt"), issues),
        images=collect_images(item, raw.source_url),
        detail_html=detail_html,
        detail_text=description_text(detail_html),
        image_usage_allowed=boolean_value(allowed),
        shipping=Shipping(
            fee=money_value(dome_delivery.get("fee")),
            fee_type=text_value(dome_delivery.get("type")),
            fee_table=text_value(dome_delivery.get("tbl")),
            payment_method=text_value(delivery.get("pay")),
            fee_calculation=(
                "fixed"
                if dome_delivery.get("type") == "고정배송비"
                else "quantity_tiers"
                if dome_delivery.get("type") == "수량별차등"
                else "unknown"
            ),
            quantity_fee_tiers=quantity_tiers(dome_delivery.get("tbl")),
            dispatch_days=integer_value(delivery.get("periodDeli")),
            remote_area_fee=money_value(object_value(delivery.get("feeExtra")).get("islands")),
        ),
    )
    for field in ("name", "images", "detail_html"):
        if getattr(product, field) in (None, "", []):
            issues.append(
                Issue(code="missing_field", field=field, message=f"{field} 정보를 확인하세요.")
            )
    if product.wholesale_price is None and not product.price_tiers:
        issues.append(
            Issue(code="missing_price", field="wholesale_price", message="단가 확인 필요")
        )
    if product.detail_text is None and product.detail_html:
        issues.append(
            Issue(
                code="image_only_description",
                field="detail_text",
                message="본문 텍스트 없음. 이미지 OCR은 별도 단계입니다.",
            )
        )
    product.issues = issues
    product.collection_status = (
        "failed" if not product.name else "partial" if issues else "complete"
    )
    return product


class DomeggookAdapter:
    name = "domeggook"

    def __init__(self, config: Config, http: SourceHTTP) -> None:
        self.config, self.http = config, http

    def matches(self, url: str) -> bool:
        return item_number(url) is not None

    async def fetch(self, url: str) -> FetchResult:
        number = item_number(url)
        if number is None:
            return FetchResult(
                issues=[
                    Issue(
                        code="invalid_url",
                        message="상품 상세페이지 URL을 확인하세요.",
                        severity="error",
                    )
                ]
            )
        key = self.config.domeggook_api_key.get_secret_value()
        if not key:
            return FetchResult(
                issues=[
                    Issue(
                        code="key_missing", message="도매꾹 API 키를 설정하세요.", severity="error"
                    )
                ]
            )
        try:
            response = await self.http.get(
                API_ENDPOINT,
                {"ver": API_VERSION, "mode": "getItemView", "aid": key, "no": number, "om": "json"},
            )
            response.raise_for_status()
            payload = response.json()
            if not isinstance(payload, dict):
                raise ValueError("상품 응답 형식 오류")
            clean = redact(payload, (key,))
            if not isinstance(clean, dict):
                raise ValueError("상품 응답 형식 오류")
            raw = RawProduct(
                source=self.name,
                source_url=f"https://www.domeggook.com/{number}",
                fetched_at=datetime.now(UTC),
                payload=clean,
            )
            errors = clean.get("errors") or object_value(clean.get("domeggook")).get("errors")
            return FetchResult(
                raw=raw,
                issues=[
                    Issue(
                        code="source_rejected",
                        message="도매꾹 조회가 거부되었습니다. 원본 응답과 계정 권한을 확인하세요.",
                        severity="error",
                    )
                ]
                if errors
                else [],
            )
        except Exception:
            return FetchResult(
                issues=[
                    Issue(
                        code="source_request_failed",
                        message="도매꾹 조회 실패. 키·권한·상품 URL·네트워크를 확인하세요.",
                        severity="error",
                    )
                ]
            )

    def normalize(self, raw: RawProduct) -> NormalizeResult:
        try:
            product = build_product(raw)
            return NormalizeResult(product=product, issues=product.issues)
        except (ValidationError, ValueError, TypeError, KeyError):
            return NormalizeResult(
                issues=[
                    Issue(
                        code="normalize_failed",
                        message="상품 응답 구조를 확인하세요.",
                        severity="error",
                    )
                ]
            )
