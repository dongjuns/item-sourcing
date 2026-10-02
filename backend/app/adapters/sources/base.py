"""소싱처마다 동일한 3함수만 구현한다."""

from typing import Protocol

from app.schemas.product import FetchResult, NormalizeResult, RawProduct


class SourceAdapter(Protocol):
    name: str

    def matches(self, url: str) -> bool: ...
    async def fetch(self, url: str) -> FetchResult: ...
    def normalize(self, raw: RawProduct) -> NormalizeResult: ...
