"""이미지 저장과 다운로드 실패도 기록한다."""

from uuid import UUID

from sqlalchemy import CheckConstraint, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IdentityMixin


class Asset(IdentityMixin, Base):
    __tablename__ = "assets"
    __table_args__ = (
        CheckConstraint("kind IN ('source','thumb','detail')"),
        CheckConstraint("status IN ('ready','failed')"),
        CheckConstraint("mode IN ('live','mock')"),
        CheckConstraint("status != 'ready' OR path IS NOT NULL"),
    )
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"))
    listing_id: Mapped[UUID | None] = mapped_column(ForeignKey("listings.id", ondelete="RESTRICT"))
    parent_asset_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT")
    )
    kind: Mapped[str] = mapped_column(String)
    status: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    source_url: Mapped[str | None] = mapped_column(Text)
    path: Mapped[str | None] = mapped_column(Text)
    mime_type: Mapped[str | None] = mapped_column(String)
    width: Mapped[int | None]
    height: Mapped[int | None]
    checksum: Mapped[str | None] = mapped_column(String)
    prompt: Mapped[str | None] = mapped_column(Text)
    error: Mapped[str | None] = mapped_column(Text)
