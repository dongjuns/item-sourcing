"""원본을 바꾸지 않는 공통 파싱 도우미."""

from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from urllib.parse import urljoin

from pydantic import JsonValue

from app.schemas.product import PriceTier


def object_value(value: JsonValue | None) -> dict[str, JsonValue]:
    return value if isinstance(value, dict) else {}


def text_value(value: JsonValue | None) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def money_value(value: JsonValue | None) -> Decimal | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        number = Decimal(str(value))
        return number if number.is_finite() and number >= 0 else None
    except InvalidOperation:
        return None


def integer_value(value: JsonValue | None) -> int | None:
    number = money_value(value)
    return int(number) if number is not None and number == number.to_integral_value() else None


def boolean_value(value: JsonValue | None) -> bool | None:
    if isinstance(value, bool):
        return value
    if isinstance(value, str) and value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return None


class ImageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__()
        self.base_url = base_url
        self.urls: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "img":
            return
        fields = dict(attrs)
        value = fields.get("src") or fields.get("data-src")
        if value:
            self.urls.append(urljoin(self.base_url, value))


class TextParser(HTMLParser):
    """본문의 실제 텍스트만 추출하며 스크립트·스타일·이미지 OCR은 제외한다."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "noscript", "template"}:
            self.hidden += 1
        if not self.hidden and tag in {"br", "p", "div", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "noscript", "template"} and self.hidden:
            self.hidden -= 1
        if not self.hidden and tag in {"p", "div", "li", "tr", "h1", "h2", "h3"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


def description_text(content: str | None) -> str | None:
    parser = TextParser()
    parser.feed(content or "")
    lines = [" ".join(line.split()) for line in "".join(parser.parts).splitlines()]
    return "\n".join(line for line in lines if line) or None


# [CHANNEL-SPEC] 도매꾹 4.6 수량+단가|수량+단가 규칙
def quantity_tiers(value: JsonValue | None) -> list[PriceTier]:
    if not isinstance(value, str) or "+" not in value:
        return []
    tiers = []
    for row in value.split("|"):
        pair = row.split("+")
        if len(pair) != 2:
            return []
        quantity, price = integer_value(pair[0]), money_value(pair[1])
        if quantity is None or quantity < 1 or price is None:
            return []
        tiers.append(PriceTier(minimum_quantity=quantity, unit_price=price))
    quantities = [tier.minimum_quantity for tier in tiers]
    return (
        sorted(tiers, key=lambda tier: tier.minimum_quantity)
        if len(set(quantities)) == len(tiers)
        else []
    )
