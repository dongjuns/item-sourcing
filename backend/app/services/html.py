"""원본 HTML은 보존하고 미리보기·편집 콘텐츠만 정제한다."""

import html
import re

import bleach

from app.schemas.results import DetailContent

TAGS = {
    "p",
    "h2",
    "h3",
    "ul",
    "ol",
    "li",
    "strong",
    "em",
    "br",
    "table",
    "tr",
    "td",
    "th",
    "tbody",
    "img",
}
ASSET_SOURCE = re.compile(r"^/api/assets/[0-9a-f-]{36}$")


def allowed_attribute(tag: str, name: str, value: str) -> bool:
    return tag == "img" and (
        (name == "src" and bool(ASSET_SOURCE.fullmatch(value))) or name == "alt"
    )


def sanitize_html(content: str) -> str:
    return bleach.clean(content, tags=TAGS, attributes=allowed_attribute, protocols=[], strip=True)


def assemble_detail(content: DetailContent, asset_ids: list[str]) -> str:
    sections = "".join(
        f"<h2>{html.escape(section.get('heading', ''))}</h2>"
        f"<p>{html.escape(section.get('body', ''))}</p>"
        for section in content.sections
    )
    images = "".join(f'<img src="/api/assets/{item}" alt="상품 이미지">' for item in asset_ids)
    return sanitize_html(f"<h2>{html.escape(content.title)}</h2>{sections}{images}")
