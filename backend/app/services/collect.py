"""수집 서비스는 소싱처 구체 클래스를 알지 않는다."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.adapters.http import SourceHTTP
from app.adapters.sources.base import SourceAdapter
from app.core.config import Config
from app.models import Job, Product
from app.schemas.product import Issue, ProductData
from app.services.assets import download_images

JSON_PRODUCT_FIELDS = {"raw", "options", "images", "shipping", "issues", "price_tiers"}


def product_record(data: ProductData) -> Product:
    scalar = data.model_dump(exclude=JSON_PRODUCT_FIELDS | {"reference_image_paths"})
    encoded = data.model_dump(mode="json")
    return Product(**scalar, **{key: encoded[key] for key in JSON_PRODUCT_FIELDS})


async def collect_product(
    job_id: UUID,
    session: Session,
    adapter: SourceAdapter,
    http: SourceHTTP,
    config: Config,
) -> None:
    job = session.get(Job, job_id)
    if job is None:
        return
    fetched = await adapter.fetch(str(job.payload["url"]))
    if fetched.raw is None:
        job.status = "failed"
        job.result = {"issues": [issue.model_dump(mode="json") for issue in fetched.issues]}
        session.commit()
        return
    normalized = adapter.normalize(fetched.raw)
    data = normalized.product
    if data is None or any(issue.severity == "error" for issue in fetched.issues):
        raw = fetched.raw
        data = ProductData(
            source=raw.source,
            source_url=raw.source_url,
            fetched_at=raw.fetched_at,
            acquisition_mode=raw.acquisition_mode,
            raw=raw.payload,
            collection_status="failed",
            issues=fetched.issues + normalized.issues,
        )
    product = product_record(data)
    session.add(product)
    session.commit()
    if product.collection_status != "failed":
        await download_images(product, session, http, config)
    job.status = {"complete": "succeeded", "partial": "partial", "failed": "failed"}[
        product.collection_status
    ]
    job.result = {"product_id": str(product.id), "issues": product.issues}
    session.commit()


def unsupported_source_issue() -> Issue:
    return Issue(
        code="unsupported_source",
        severity="error",
        message="지원 소싱처 URL이 아닙니다. 소싱처 추가는 인수인계 문서를 확인하세요.",
    )
