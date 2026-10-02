"""수집한 참조 이미지로 썸네일 후보를 만든다."""

import base64

import httpx

from app.core.config import Config
from app.core.security import redact
from app.schemas.product import Issue, ProductData
from app.schemas.results import GeneratedImage, ImageResult, Usage
from app.services.assets import save_image

# [CHANNEL-SPEC] OpenAI Images Edits API — 모델·출력 규격 변경 시 이 파일 수정
EDITS_URL = "https://api.openai.com/v1/images/edits"
IMAGE_SIZE = "1024x1024"
IMAGE_QUALITY = "low"


class OpenAIImage:
    def __init__(self, config: Config, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.config, self.transport = config, transport

    async def generate_thumbnails(self, product: ProductData, n: int = 3) -> ImageResult:
        key = self.config.openai_api_key.get_secret_value()
        if not key or not self.config.ai_image_model or not product.reference_image_paths:
            return ImageResult(
                usage=Usage(billing_status="unbilled"),
                issues=[
                    Issue(
                        code="image_unconfigured",
                        message="AI 키·이미지 모델·수집 이미지를 확인하세요.",
                        severity="error",
                    )
                ],
            )
        images: list[GeneratedImage] = []
        try:
            prompt = (self.config.prompts_dir / "thumbnail.md").read_text()
            reference = product.reference_image_paths[0]
            async with httpx.AsyncClient(
                timeout=180, transport=self.transport, trust_env=False
            ) as client:
                response = await client.post(
                    EDITS_URL,
                    headers={"Authorization": f"Bearer {key}"},
                    data={
                        "model": self.config.ai_image_model,
                        "prompt": prompt,
                        "n": str(n),
                        "size": IMAGE_SIZE,
                        "quality": IMAGE_QUALITY,
                    },
                    files={"image": ("reference.png", reference.read_bytes(), "image/png")},
                )
            if response.status_code >= 400:
                return ImageResult(
                    issues=[
                        Issue(
                            code="image_rejected",
                            message="이미지 요청이 거부되었습니다. 모델·계정·한도를 확인하세요.",
                            severity="error",
                        )
                    ]
                )
            data = response.json()
            for image in data.get("data", []):
                path, width, height, _ = save_image(
                    base64.b64decode(image["b64_json"], validate=True), self.config.assets_dir
                )
                images.append(
                    GeneratedImage(
                        path=path, width=width, height=height, mime_type="image/png", prompt=prompt
                    )
                )
            usage = redact(data.get("usage", {}), (key,))
            return ImageResult(
                images=images,
                usage=Usage(
                    image_count=len(images), provider_usage=usage if isinstance(usage, dict) else {}
                ),
            )
        except Exception:
            return ImageResult(
                images=images,
                issues=[
                    Issue(
                        code="image_failed",
                        message="썸네일 생성 일부 또는 전체 실패. 과금 여부를 확인하세요.",
                        severity="error",
                    )
                ],
            )
