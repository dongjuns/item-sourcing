"""실수집과 구분되는 내부 흐름 검증용 소싱처."""

from datetime import UTC, datetime

from app.schemas.product import FetchResult, NormalizeResult, ProductData, RawProduct


class MockSource:
    name = "mock"

    def matches(self, url: str) -> bool:
        return url == "https://example.test/product/demo"

    async def fetch(self, url: str) -> FetchResult:
        return FetchResult(
            raw=RawProduct(
                source=self.name,
                source_url=url,
                fetched_at=datetime.now(UTC),
                acquisition_mode="mock",
                payload={"name": "검토 흐름 예시 상품", "fixture_status": "mock"},
            )
        )

    def normalize(self, raw: RawProduct) -> NormalizeResult:
        return NormalizeResult(
            product=ProductData(
                source=self.name,
                source_url=raw.source_url,
                fetched_at=raw.fetched_at,
                acquisition_mode="mock",
                collection_status="complete",
                name="검토 흐름 예시 상품",
                currency="KRW",
                wholesale_price=5000,
                options=[],
                images=[],
                detail_html="<p>연습 상품입니다.</p>",
                image_usage_allowed=True,
                raw=raw.payload,
            )
        )
