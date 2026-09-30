"""프롬프트와 유료 API를 교체하는 경계."""

from typing import Protocol

from app.schemas.product import ProductData
from app.schemas.results import DetailResult, ImageResult


class TextGenerator(Protocol):
    async def generate_detail(
        self, product: ProductData, channel: str, tone: str
    ) -> DetailResult: ...


class ImageGenerator(Protocol):
    async def generate_thumbnails(self, product: ProductData, n: int = 3) -> ImageResult: ...
