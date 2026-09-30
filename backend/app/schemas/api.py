"""API 입력과 작업·자산 조회 응답."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class CollectRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(min_length=1, max_length=2048)


class JobAccepted(BaseModel):
    job_id: UUID


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    kind: str
    status: str
    result: dict[str, JsonValue]
    created_at: datetime
    started_at: datetime | None
    finished_at: datetime | None


class AssetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    product_id: UUID
    listing_id: UUID | None
    kind: str
    status: str
    mode: str
    width: int | None
    height: int | None
    error: str | None


class AppStatus(BaseModel):
    source_mode: Literal["live", "mock"]
    ai_mode: Literal["live", "mock"]
    sources: list[str]
    domeggook_key_configured: bool
    ai_key_configured: bool
    ai_text_model: str
    ai_image_model: str
    registration_enabled: bool = False


class SettingsRead(BaseModel):
    values: dict[str, JsonValue]
    status: AppStatus


class SettingsPatch(BaseModel):
    values: dict[str, JsonValue]


class ResolveCallRequest(BaseModel):
    actual_cost_krw: str
    evidence: str = Field(min_length=1, max_length=2000)
