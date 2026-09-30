"""후속 등록 이력 스키마만 예약한다. 등록 서비스와 API는 이번 범위에서 제외한다."""

from datetime import datetime
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import JSON_DATA, Base, IdentityMixin

UNRESOLVED = text("status IN ('pending','running','unknown')")


class Registration(IdentityMixin, Base):
    __tablename__ = "registrations"
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending','running','succeeded','failed','unknown','simulated')"
        ),
        CheckConstraint("mode IN ('live','mock')"),
        CheckConstraint("mode != 'mock' OR (external_id IS NULL AND external_url IS NULL)"),
        Index(
            "uq_registration_unresolved",
            "listing_id",
            unique=True,
            postgresql_where=UNRESOLVED,
            sqlite_where=UNRESOLVED,
        ),
    )
    listing_id: Mapped[UUID] = mapped_column(ForeignKey("listings.id", ondelete="RESTRICT"))
    channel: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    content_version: Mapped[int]
    listing_snapshot: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA)
    status: Mapped[str] = mapped_column(String)
    external_id: Mapped[str | None] = mapped_column(String)
    external_url: Mapped[str | None] = mapped_column(Text)
    request: Mapped[dict[str, JsonValue] | None] = mapped_column(JSON_DATA)
    response: Mapped[dict[str, JsonValue] | None] = mapped_column(JSON_DATA)
    error_code: Mapped[str | None] = mapped_column(String)
    error_message: Mapped[str | None] = mapped_column(Text)
    resolution: Mapped[dict[str, JsonValue] | None] = mapped_column(JSON_DATA)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
