"""OpenAI 텍스트 호출과 프롬프트 읽기는 이 어댑터에만 둔다."""

import json

import httpx

from app.core.config import Config
from app.core.security import redact
from app.schemas.product import Issue, ProductData
from app.schemas.results import DetailContent, DetailResult, Usage

# [CHANNEL-SPEC] OpenAI Responses API — 요청·구조화 출력 규격 변경 시 이 파일 수정
RESPONSES_URL = "https://api.openai.com/v1/responses"
MAX_OUTPUT_TOKENS = 2000
MAX_PRODUCT_TEXT = 12_000
MAX_DESCRIPTION_TEXT = 6000
DETAIL_SCHEMA: dict[str, object] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["title", "sections"],
    "properties": {
        "title": {"type": "string"},
        "sections": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["heading", "body"],
                "properties": {"heading": {"type": "string"}, "body": {"type": "string"}},
            },
        },
    },
}


class OpenAIText:
    def __init__(self, config: Config, transport: httpx.AsyncBaseTransport | None = None) -> None:
        self.config, self.transport = config, transport

    async def generate_detail(self, product: ProductData, channel: str, tone: str) -> DetailResult:
        key = self.config.openai_api_key.get_secret_value()
        if not key or not self.config.ai_text_model:
            return DetailResult(
                usage=Usage(billing_status="unbilled"),
                issues=[
                    Issue(
                        code="ai_unconfigured",
                        message="개발용 AI 키와 텍스트 모델을 설정하세요.",
                        severity="error",
                    )
                ],
            )
        try:
            prompt = (self.config.prompts_dir / f"detail_{channel}.md").read_text()
            facts = product.model_dump(
                mode="json", exclude={"raw", "reference_image_paths", "detail_html", "images"}
            )
            facts["detail_text"] = (product.detail_text or "")[:MAX_DESCRIPTION_TEXT]
            user_input = json.dumps({"tone": tone, "product": facts}, ensure_ascii=False)
            if len(user_input) > MAX_PRODUCT_TEXT:
                return DetailResult(
                    usage=Usage(billing_status="unbilled"),
                    issues=[
                        Issue(
                            code="input_too_large",
                            message="상품 정보가 생성 입력 한도를 넘었습니다.",
                        )
                    ],
                )
            body = {
                "model": self.config.ai_text_model,
                "instructions": prompt,
                "input": user_input,
                "max_output_tokens": MAX_OUTPUT_TOKENS,
                "store": False,
                "text": {
                    "format": {
                        "type": "json_schema",
                        "name": "product_detail",
                        "strict": True,
                        "schema": DETAIL_SCHEMA,
                    }
                },
            }
            async with httpx.AsyncClient(
                timeout=90, transport=self.transport, trust_env=False
            ) as client:
                response = await client.post(
                    RESPONSES_URL, headers={"Authorization": f"Bearer {key}"}, json=body
                )
            if response.status_code >= 400:
                return DetailResult(
                    issues=[
                        Issue(
                            code="ai_rejected",
                            message="AI 요청이 거부되었습니다. 모델·계정·한도를 확인하세요.",
                            severity="error",
                        )
                    ]
                )
            data = response.json()
            text = "".join(
                part.get("text", "")
                for output in data.get("output", [])
                for part in output.get("content", [])
                if part.get("type") == "output_text"
            )
            content = DetailContent.model_validate_json(text)
            provider_usage = redact(data.get("usage", {}), (key,))
            usage = Usage(
                provider_usage=provider_usage if isinstance(provider_usage, dict) else {},
                input_tokens=data.get("usage", {}).get("input_tokens"),
                output_tokens=data.get("usage", {}).get("output_tokens"),
            )
            return DetailResult(content=content, usage=usage)
        except Exception:
            return DetailResult(
                issues=[
                    Issue(
                        code="ai_failed",
                        message="AI 텍스트 생성 실패. 과금 여부는 사용량에서 확인하세요.",
                        severity="error",
                    )
                ]
            )
