"""사람 검토와 확정. 판매 채널 등록 호출은 없다."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Asset, Job, Listing, Product
from app.models.base import utc_now
from app.schemas.listing import ListingPatch
from app.services.html import sanitize_html


class ReviewError(ValueError):
    pass


def lock_listing(session: Session, listing_id: UUID, version: int) -> Listing:
    initial = session.get(Listing, listing_id)
    if initial is None:
        raise LookupError("콘텐츠를 찾을 수 없습니다.")
    session.execute(
        select(Product).where(Product.id == initial.product_id).with_for_update()
    ).scalar_one()
    listing = session.execute(
        select(Listing).where(Listing.id == listing_id).with_for_update()
    ).scalar_one()
    if listing.content_version != version:
        raise ReviewError("다른 화면에서 변경되었습니다. 새로고침하세요.")
    if listing.status == "registered":
        raise ReviewError("등록된 콘텐츠는 읽기 전용입니다.")
    active = session.scalar(
        select(Job.id).where(
            Job.target_key == str(listing.product_id),
            Job.status.in_(["queued", "running"]),
        )
    )
    if active is not None:
        raise ReviewError("생성 작업이 진행 중입니다. 완료 후 다시 시도하세요.")
    return listing


def reset_confirmation(listing: Listing) -> None:
    listing.status = "draft"
    listing.confirmed_version, listing.confirmed_at = None, None
    listing.content_version += 1


def patch_listing(session: Session, listing_id: UUID, patch: ListingPatch) -> Listing:
    listing = lock_listing(session, listing_id, patch.expected_version)
    changes = patch.model_dump(exclude_unset=True, exclude={"expected_version"})
    if "selected_thumbnail_id" in changes and changes["selected_thumbnail_id"] is not None:
        asset = session.get(Asset, changes["selected_thumbnail_id"])
        if (
            asset is None
            or asset.product_id != listing.product_id
            or asset.status != "ready"
            or str(asset.id) not in listing.thumbnail_ids
        ):
            raise ReviewError("이 콘텐츠의 썸네일 후보를 선택하세요.")
    if changes.get("detail_html") is not None:
        changes["detail_html"] = sanitize_html(changes["detail_html"])
    for key, value in changes.items():
        setattr(listing, key, value)
    if changes:
        reset_confirmation(listing)
    session.commit()
    return listing


def confirm_listing(session: Session, listing_id: UUID, version: int) -> Listing:
    listing = lock_listing(session, listing_id, version)
    if not listing.title or not listing.title.strip() or not listing.detail_html:
        raise ReviewError("제목과 상세 콘텐츠를 검토한 뒤 확정하세요.")
    if listing.selected_thumbnail_id is None:
        raise ReviewError("썸네일을 선택하세요.")
    if listing.sale_price is None or listing.sale_price <= 0:
        raise ReviewError("판매가를 입력하세요.")
    listing.status, listing.confirmed_version, listing.confirmed_at = (
        "confirmed",
        listing.content_version,
        utc_now(),
    )
    session.commit()
    return listing
