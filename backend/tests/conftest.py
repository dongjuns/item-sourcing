"""테스트는 임시 DB·이미지와 녹화 응답만 사용한다."""

from collections.abc import Iterator
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import httpx
import pytest
from fastapi.testclient import TestClient
from PIL import Image
from pydantic import SecretStr

from app.adapters.http import SourceHTTP
from app.adapters.sources.domeggook import DomeggookAdapter
from app.core.config import Config
from app.db.session import build_engine
from app.main import create_app
from app.models.base import Base
from app.schemas.product import FetchResult, NormalizeResult, RawProduct

FIXTURES = Path(__file__).parent / "fixtures" / "domeggook"
TEST_URL = "https://www.domeggook.com/63749955?from=lstGen"


@pytest.fixture(autouse=True)
def block_network(monkeypatch: pytest.MonkeyPatch) -> None:
    original = httpx.AsyncClient.send

    async def guarded(self: httpx.AsyncClient, *args: object, **kwargs: object) -> httpx.Response:
        if not isinstance(self._transport, (httpx.MockTransport, httpx.ASGITransport)):
            pytest.fail("테스트에서 실제 네트워크 호출을 금지합니다.")
        return await original(self, *args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(httpx.AsyncClient, "send", guarded)


class FixtureHTTP(SourceHTTP):
    async def download(self, url: str) -> bytes:
        self.last_request = 0
        return await super().download(url)


class FixtureSource:
    name = "domeggook"

    def __init__(self, config: Config, http: SourceHTTP) -> None:
        self.normalizer = DomeggookAdapter(config, http)

    def matches(self, url: str) -> bool:
        return self.normalizer.matches(url)

    async def fetch(self, url: str) -> FetchResult:
        import json

        return FetchResult(
            raw=RawProduct(
                source=self.name,
                source_url=url,
                fetched_at=datetime.now(UTC),
                acquisition_mode="mock",
                payload=json.loads((FIXTURES / "product_recorded.json").read_text()),
            )
        )

    def normalize(self, raw: RawProduct) -> NormalizeResult:
        return self.normalizer.normalize(raw)


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    config = Config(
        _env_file=None,
        basic_auth_password=SecretStr("test-password"),
        domeggook_api_key=SecretStr(""),
        openai_api_key=SecretStr(""),
        source_mode="mock",
        ai_mode="mock",
        assets_dir=tmp_path / "assets",
    )
    engine = build_engine(f"sqlite+pysqlite:///{tmp_path / 'test.sqlite3'}")
    Base.metadata.create_all(engine)
    app = create_app(config, engine)
    output = BytesIO()
    Image.new("RGB", (8, 8), "white").save(output, format="PNG")
    transport = httpx.MockTransport(lambda _: httpx.Response(200, content=output.getvalue()))
    http = FixtureHTTP(config, transport)
    app.state.runner.registry.sources = [FixtureSource(config, http)]
    app.state.runner.registry.http = http
    with TestClient(app) as test_client:
        test_client.auth = ("owner", "test-password")
        yield test_client
    engine.dispose()
