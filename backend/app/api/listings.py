"""콘텐츠 저장과 확정만 제공한다."""

from uuid import UUID

from fastapi import APIRouter

from app.api.dependencies import DB
from app.schemas.listing import ConfirmRequest, ListingPatch, ListingRead
from app.services.listings import confirm_listing, patch_listing

router = APIRouter()


@router.patch("/listings/{listing_id}")
def update(listing_id: UUID, body: ListingPatch, db: DB) -> ListingRead:
    return ListingRead.model_validate(patch_listing(db, listing_id, body))


@router.post("/listings/{listing_id}/confirm")
def confirm(listing_id: UUID, body: ConfirmRequest, db: DB) -> ListingRead:
    return ListingRead.model_validate(confirm_listing(db, listing_id, body.expected_version))
