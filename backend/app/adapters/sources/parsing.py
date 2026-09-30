"""원본을 바꾸지 않는 공통 파싱 도우미."""

from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser
from urllib.parse import urljoin

from pydantic import JsonValue


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
