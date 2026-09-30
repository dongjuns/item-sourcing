"""비동기 작업 상태를 프로세스 밖에 보존한다."""

from datetime import datetime

from pydantic import JsonValue
from sqlalchemy import CheckConstraint, DateTime, Index, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import JSON_DATA, Base, IdentityMixin

ACTIVE_JOB = text("status IN ('queued','running')")


class Job(IdentityMixin, Base):
    __tablename__ = "jobs"
    __table_args__ = (
        CheckConstraint("kind IN ('collect','generate','register')"),
        CheckConstraint(
            "status IN ('queued','running','succeeded','partial','failed','interrupted')"
        ),
        Index(
            "uq_job_active_target",
            "kind",
            "target_key",
            unique=True,
            postgresql_where=ACTIVE_JOB,
            sqlite_where=ACTIVE_JOB,
        ),
    )
    kind: Mapped[str] = mapped_column(String)
    target_key: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String, default="queued")
    payload: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA, default=dict)
    result: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA, default=dict)
    log: Mapped[list[JsonValue]] = mapped_column(JSON_DATA, default=list)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    finished_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
