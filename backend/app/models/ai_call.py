"""유료 호출 전에 예약을 남기고 불명확한 과금은 보수적으로 유지한다."""

from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import JsonValue
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import JSON_DATA, Base, IdentityMixin


class AICall(IdentityMixin, Base):
    __tablename__ = "ai_calls"
    __table_args__ = (
        CheckConstraint("status IN ('reserved','running','settled','released','unknown')"),
        CheckConstraint("mode IN ('live','mock')"),
        CheckConstraint("reserved_cost_krw >= 0"),
        CheckConstraint("actual_cost_krw IS NULL OR actual_cost_krw >= 0"),
        CheckConstraint("status != 'settled' OR actual_cost_krw IS NOT NULL"),
    )
    job_id: Mapped[UUID] = mapped_column(ForeignKey("jobs.id", ondelete="RESTRICT"))
    provider: Mapped[str] = mapped_column(String)
    model: Mapped[str] = mapped_column(String)
    kind: Mapped[str] = mapped_column(String)
    mode: Mapped[str] = mapped_column(String)
    budget_day: Mapped[date]
    budget_month: Mapped[date]
    status: Mapped[str] = mapped_column(String)
    reserved_cost_krw: Mapped[Decimal] = mapped_column(Numeric(18, 4))
    actual_cost_krw: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    input_tokens: Mapped[int | None]
    output_tokens: Mapped[int | None]
    image_count: Mapped[int | None]
    pricing_snapshot: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA, default=dict)
    usage: Mapped[dict[str, JsonValue] | None] = mapped_column(JSON_DATA)
    error: Mapped[str | None] = mapped_column(Text)
    resolution: Mapped[dict[str, JsonValue] | None] = mapped_column(JSON_DATA)
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
