"""후속 등록 단계의 계약만 정의한다. 이번 범위에는 구현하지 않는다."""

from typing import Protocol

from app.schemas.listing import ListingRead
from app.schemas.product import Issue
from app.schemas.results import CategoryResult, RegisterResult


class ChannelAdapter(Protocol):
    name: str

    def validate(self, listing: ListingRead) -> list[Issue]: ...
    def build_payload(self, listing: ListingRead) -> dict[str, object]: ...
    async def register(self, payload: dict[str, object]) -> RegisterResult: ...
    async def categories(self, query: str) -> CategoryResult: ...
