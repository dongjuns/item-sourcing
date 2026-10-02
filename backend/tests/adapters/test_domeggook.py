"""도매꾹 실제 녹화 필드의 정규화와 실패 격리 검증."""

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr

from app.adapters.http import SourceHTTP
from app.adapters.sources.domeggook import DomeggookAdapter, collect_shipping, item_number
from app.adapters.sources.parsing import boolean_value, description_text, quantity_tiers
from app.core.config import Config
from app.schemas.product import RawProduct
from app.services.quote import product_quote

FIXTURES = Path(__file__).parents[1] / "fixtures" / "domeggook"


def adapter(transport: httpx.MockTransport | None = None) -> DomeggookAdapter:
    config = Config(_env_file=None, domeggook_api_key=SecretStr("fixture-key"))
    return DomeggookAdapter(config, SourceHTTP(config, transport))


def test_recorded_normalize_snapshot() -> None:
    raw = RawProduct(
        source="domeggook",
        source_url="https://www.domeggook.com/63749955",
        fetched_at=datetime(2026, 9, 30, tzinfo=UTC),
        payload=json.loads((FIXTURES / "product_recorded.json").read_text()),
    )
    result = adapter().normalize(raw)
    assert result.product is not None
    expected = json.loads((FIXTURES / "product_recorded.expected.json").read_text())
    assert result.product.model_dump(mode="json") == expected
    assert result.product.wholesale_price == 35000
    assert result.product.shipping is not None and result.product.shipping.fee == 2750
    assert result.product.image_usage_allowed is True
    assert len(result.product.detail_text or "") == 569
    assert len(result.product.images or []) == 3


def test_free_shipping_dispatch_and_no_bundle() -> None:
    payload = json.loads((FIXTURES / "product_recorded.json").read_text())
    # 작성한 반례다. 실제 녹화본을 무료배송 상품으로 바꾸지 않는다.
    payload["domeggook"]["deli"].update(pay="무료배송", periodDeli="3", merge={"enable": "n"})
    raw = RawProduct(
        source="domeggook",
        source_url="https://www.domeggook.com/63749955",
        fetched_at=datetime(2026, 9, 30, tzinfo=UTC),
        payload=payload,
    )
    result = adapter().normalize(raw)
    assert result.product is not None and result.product.shipping is not None
    shipping = result.product.shipping
    assert shipping.method == "택배" and shipping.dispatch_days == 3
    assert shipping.bundle_shipping == "not_allowed" and shipping.bundle_threshold is None
    assert shipping.fee == 0
    assert product_quote(result.product, 2).total_amount == 70000
    assert raw.payload == payload
    assert payload["domeggook"]["deli"]["dome"]["fee"] == "2750"


@pytest.mark.parametrize(
    ("enable", "expected"),
    [
        ("y", "allowed"),
        ("n", "not_allowed"),
        ("c", "conditional"),
        ("unknown", "unknown"),
        (None, "unknown"),
    ],
)
def test_bundle_conditions_are_separate_from_free_shipping(
    enable: str | None, expected: str
) -> None:
    shipping = collect_shipping({"merge": {"enable": enable, "basePrice": "300000"}})
    assert shipping.bundle_shipping == expected
    assert shipping.bundle_threshold == (300000 if enable == "c" else None)
    assert shipping.free_shipping_threshold is None
    assert shipping.fee is None and shipping.dispatch_days is None


def test_missing_shipping_does_not_mean_free_or_no_bundle() -> None:
    shipping = collect_shipping({})
    assert shipping.fee is None and shipping.method is None
    assert shipping.bundle_shipping == "unknown"


@pytest.mark.parametrize(
    "url",
    [
        "https://domeggook.com.evil.test/63749955",
        "https://user:password@www.domeggook.com/63749955",
        "file:///63749955",
        "https://www.domeggook.com/63749955:80",
        "https://www.domeggook.com:8080/63749955",
        "https://www.domeggook.com/list",
    ],
)
def test_reject_other_urls(url: str) -> None:
    assert item_number(url) is None


def test_user_url_and_text_parser() -> None:
    assert item_number("https://www.domeggook.com/63749955?from=lstGen") == "63749955"
    assert (
        description_text(
            "<p>상품 <b>설명</b>&amp; 안내</p><script>제외</script><style>제외</style>"
        )
        == "상품 설명& 안내"
    )
    assert description_text('<img src="test.jpg">') is None
    assert boolean_value("false") is False
    assert boolean_value("true") is True
    assert boolean_value("unknown") is None
    assert [tier.unit_price for tier in quantity_tiers("1+3800|20+3500")] == [3800, 3500]
    assert quantity_tiers("1+3800|broken") == []


async def test_fetch_masks_key_and_uses_read_only_get() -> None:
    def handle(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert request.url.params["mode"] == "getItemView"
        assert request.url.params["no"] == "63749955"
        return httpx.Response(
            200, json={"aid": "fixture-key", "echo": "fixture-key", "basis": {"no": 63749955}}
        )

    result = await adapter(httpx.MockTransport(handle)).fetch("https://www.domeggook.com/63749955")
    assert result.raw is not None
    assert "fixture-key" not in result.raw.model_dump_json()
    assert result.raw.payload["aid"] == "[REDACTED_SECRET]"


async def test_failed_request_returns_result() -> None:
    result = await adapter(httpx.MockTransport(lambda _: httpx.Response(503))).fetch(
        "https://www.domeggook.com/63749955"
    )
    assert result.raw is None
    assert result.issues[0].code == "source_request_failed"
