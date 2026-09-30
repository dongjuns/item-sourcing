"""요청 수락 시 작업을 먼저 저장한다."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adapters.sources.base import SourceAdapter
from app.models import Job, Listing, Product
from app.schemas.listing import GenerateRequest
from app.services.collect import unsupported_source_issue
from app.services.listings import ReviewError


def save_job(session: Session, job: Job) -> Job:
    session.add(job)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ReviewError("같은 대상의 작업이 이미 진행 중입니다.") from None
    return job


def prepare_collect(session: Session, url: str, adapter: SourceAdapter | None) -> Job:
    if adapter is None:
        raise ReviewError(unsupported_source_issue().message)
    return save_job(
        session, Job(kind="collect", target_key=url, payload={"url": url}, status="queued")
    )


def prepare_generation(session: Session, product_id: UUID, request: GenerateRequest) -> Job:
    product = session.execute(
        select(Product).where(Product.id == product_id).with_for_update()
    ).scalar_one_or_none()
    if product is None:
        raise LookupError("상품을 찾을 수 없습니다.")
    if product.collection_status == "failed" or not product.name:
        raise ReviewError("수집에 실패한 상품은 생성할 수 없습니다.")
    if request.scope in {"all", "thumbnails"} and product.image_usage_allowed is False:
        raise ReviewError("공급자가 이미지 재사용을 허용하지 않은 상품입니다.")
    if product.image_usage_allowed is None and not request.image_usage_confirmed:
        raise ReviewError("원본 이미지 사용 조건을 확인하고 체크하세요.")
    existing = session.scalars(select(Listing).where(Listing.product_id == product_id))
    for listing in existing:
        if listing.channel not in request.channels:
            continue
        if (
            listing.status == "registered"
            or request.expected_versions.get(listing.channel) != listing.content_version
        ):
            raise ReviewError("콘텐츠 상태·버전이 변경되었습니다. 새로고침하세요.")
    return save_job(
        session,
        Job(
            kind="generate",
            target_key=str(product_id),
            status="queued",
            payload={"product_id": str(product_id), "request": request.model_dump(mode="json")},
        ),
    )
