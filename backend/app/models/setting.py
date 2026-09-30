"""현재 비밀은 env로 관리하며 암호화 저장 컬럼은 후속 구현용이다."""

from datetime import datetime

from pydantic import JsonValue
from sqlalchemy import CheckConstraint, DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import JSON_DATA, Base, utc_now


class Setting(Base):
    __tablename__ = "settings"
    __table_args__ = (CheckConstraint("value IS NULL OR encrypted_value IS NULL"),)
    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[JsonValue | None] = mapped_column(JSON_DATA)
    encrypted_value: Mapped[str | None] = mapped_column(Text)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utc_now, onupdate=utc_now
    )
