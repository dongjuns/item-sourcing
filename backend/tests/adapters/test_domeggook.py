"""도매꾹 실제 녹화 필드의 정규화와 실패 격리 검증."""

import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
from pydantic import SecretStr

from app.adapters.http import SourceHTTP
from app.adapters.sources.domeggook import DomeggookAdapter, item_number
from app.adapters.sources.parsing import boolean_value, description_text, quantity_tiers
from app.core.config import Config
from app.schemas.product import RawProduct

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
