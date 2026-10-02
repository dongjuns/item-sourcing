"""OpenAI 요청과 응답 처리를 녹화 형태의 fake 응답으로 검증한다."""

import json
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import httpx
from PIL import Image
from pydantic import SecretStr

from app.adapters.ai.image import OpenAIImage
from app.adapters.ai.text import OpenAIText
from app.core.config import Config
from app.schemas.product import ProductData

FIXTURES = Path(__file__).parents[1] / "fixtures" / "openai"


def fixture(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / f"{name}.json").read_text())


def product() -> ProductData:
    return ProductData(
        source="test",
        source_url="https://example.test/item",
        fetched_at=datetime.now(UTC),
        name="수집 상품",
        raw={"private": "do-not-send"},
        detail_html="<style>" + "x" * 40000 + "</style>",
        detail_text="실제 본문 설명",
    )


async def test_text_sends_valid_json_and_source_text(tmp_path: Path) -> None:
    config = Config(
        _env_file=None,
        openai_api_key=SecretStr("fixture-ai-key"),
        ai_text_model="test-model",
        assets_dir=tmp_path,
    )

    def handle(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST" and request.url.path == "/v1/responses"
        body = json.loads(request.content)
        facts = json.loads(body["input"])
        assert facts["product"]["detail_text"] == "실제 본문 설명"
        assert "raw" not in facts["product"] and "detail_html" not in facts["product"]
        assert "do-not-send" not in body["input"]
        assert body["store"] is False and body["text"]["format"]["strict"] is True
        return httpx.Response(200, json=fixture("text"))

    result = await OpenAIText(config, httpx.MockTransport(handle)).generate_detail(
        product(), "coupang", "담백하게"
    )
    assert result.content is not None and result.content.title == "검토할 제목"
    assert result.usage.input_tokens == 100 and result.usage.billing_status == "unknown"


async def test_image_upload_and_three_outputs(tmp_path: Path) -> None:
    config = Config(
        _env_file=None,
        openai_api_key=SecretStr("fixture-ai-key"),
        ai_image_model="test-image",
        assets_dir=tmp_path,
    )
    output = BytesIO()
    Image.new("RGB", (16, 16), "white").save(output, "PNG")
    reference = tmp_path / "reference.png"
    reference.write_bytes(output.getvalue())
    data = product()
    data.reference_image_paths = [reference]

    def handle(request: httpx.Request) -> httpx.Response:
        assert request.method == "POST" and request.url.path == "/v1/images/edits"
        assert "multipart/form-data" in request.headers["content-type"]
        assert b'name="image"' in request.content and b"reference.png" in request.content
        return httpx.Response(200, json=fixture("image"))

    result = await OpenAIImage(config, httpx.MockTransport(handle)).generate_thumbnails(data)
    assert len(result.images) == 3 and result.usage.image_count == 3
    assert all((tmp_path / row.path).is_file() for row in result.images)
    assert result.usage.billing_status == "unknown"


async def test_unconfigured_or_rejected_call_is_explicit() -> None:
    config = Config(_env_file=None, openai_api_key=SecretStr(""), ai_text_model="")
    result = await OpenAIText(config).generate_detail(product(), "coupang", "")
    assert result.content is None and result.usage.billing_status == "unbilled"
    config.openai_api_key = SecretStr("fixture-ai-key")
    config.ai_text_model = "test-model"
    result = await OpenAIText(
        config, httpx.MockTransport(lambda _: httpx.Response(429))
    ).generate_detail(product(), "coupang", "")
    assert result.content is None and result.issues[0].code == "ai_rejected"


async def test_oversized_input_is_rejected_before_paid_request() -> None:
    config = Config(
        _env_file=None,
        openai_api_key=SecretStr("fixture-ai-key"),
        ai_text_model="test-model",
    )
    data = product()
    data.name = "x" * 12001

    def reject_network(request: httpx.Request) -> httpx.Response:
        raise AssertionError("입력 초과 시 외부 호출하면 안 됩니다.")

    result = await OpenAIText(config, httpx.MockTransport(reject_network)).generate_detail(
        data, "coupang", ""
    )
    assert result.issues[0].code == "input_too_large"
    assert result.content is None and result.usage.billing_status == "unbilled"
