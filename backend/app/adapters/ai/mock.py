"""유료 AI를 호출하지 않는 검토 흐름 예시. 생성 AI 결과로 표시하지 않는다."""

from uuid import uuid4

from PIL import Image, ImageDraw

from app.core.config import Config
from app.schemas.product import ProductData
from app.schemas.results import DetailContent, DetailResult, GeneratedImage, ImageResult, Usage

MOCK_SIZE = 640


class MockText:
    async def generate_detail(self, product: ProductData, channel: str, tone: str) -> DetailResult:
        return DetailResult(
            content=DetailContent(
                title=f"[연습] {product.name}",
                sections=[
                    {
                        "heading": "연습 콘텐츠",
                        "body": "실제 AI 생성 결과가 아닙니다. 편집·확정 흐름을 확인하세요.",
                    }
                ],
            ),
            usage=Usage(actual_cost_krw=0, billing_status="verified"),
        )


class MockImage:
    def __init__(self, config: Config) -> None:
        self.config = config

    async def generate_thumbnails(self, product: ProductData, n: int = 3) -> ImageResult:
        images = []
        for index in range(n):
            path = f"images/{uuid4()}.png"
            target = self.config.assets_dir / path
            target.parent.mkdir(parents=True, exist_ok=True)
            image = Image.new("RGB", (MOCK_SIZE, MOCK_SIZE), (235 - index * 10, 241, 248))
            ImageDraw.Draw(image).text((40, 40), f"MOCK PREVIEW {index + 1}", fill=(20, 50, 90))
            image.save(target)
            images.append(
                GeneratedImage(
                    path=path,
                    mime_type="image/png",
                    width=MOCK_SIZE,
                    height=MOCK_SIZE,
                    prompt="연습용 이미지",
                )
            )
        return ImageResult(
            images=images, usage=Usage(actual_cost_krw=0, image_count=n, billing_status="verified")
        )
