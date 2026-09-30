"""검토 콘텐츠 버전과 사람 확정 상태."""

from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import JSON_DATA, Base, IdentityMixin, utc_now


class Listing(IdentityMixin, Base):
    __tablename__ = "listings"
    __table_args__ = (
        UniqueConstraint("product_id", "channel", name="uq_listing_product_channel"),
        CheckConstraint("channel IN ('coupang','smartstore')"),
        CheckConstraint("content_mode IN ('live','mock','mixed')"),
        CheckConstraint("status IN ('draft','confirmed','registered')"),
        CheckConstraint("content_version >= 1"),
        CheckConstraint("sale_price IS NULL OR sale_price >= 0"),
        CheckConstraint(
            "(status = 'draft' AND confirmed_version IS NULL AND confirmed_at IS NULL) OR "
            "(status IN ('confirmed','registered') AND confirmed_version IS NOT NULL AND "
            "confirmed_version = content_version AND confirmed_at IS NOT NULL)",
            name="ck_listing_confirmation",
        ),
    )
    product_id: Mapped[UUID] = mapped_column(ForeignKey("products.id", ondelete="RESTRICT"))
    channel: Mapped[str] = mapped_column(String)
    content_mode: Mapped[str] = mapped_column(String, default="mock")
    title: Mapped[str | None] = mapped_column(Text)
    detail_html: Mapped[str | None] = mapped_column(Text)
    thumbnail_ids: Mapped[list[str]] = mapped_column(JSON_DATA, default=list)
    selected_thumbnail_id: Mapped[UUID | None] = mapped_column(
        ForeignKey("assets.id", name="fk_listing_thumbnail", use_alter=True, ondelete="RESTRICT")
    )
    sale_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    currency: Mapped[str | None] = mapped_column(String)
    category_code: Mapped[str | None] = mapped_column(String)
    options: Mapped[list[JsonValue]] = mapped_column(JSON_DATA, default=list)
    shipping: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA, default=dict)
    notices: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA, default=dict)
    channel_fields: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA, default=dict)
    status: Mapped[str] = mapped_column(String, default="draft")
    content_version: Mapped[int] = mapped_column(default=1)
    confirmed_version: Mapped[int | None]
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
