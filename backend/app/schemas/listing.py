"""콘텐츠 편집과 확정은 판매 채널 등록에서 독립적이다."""

from datetime import datetime
from decimal import Decimal
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

Channel = Literal["coupang", "smartstore"]


class ListingRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    product_id: UUID
    channel: Channel
    content_mode: Literal["live", "mock", "mixed"]
    title: str | None
    detail_html: str | None
    thumbnail_ids: list[str]
    selected_thumbnail_id: UUID | None
    sale_price: Decimal | None
    currency: str | None
    category_code: str | None
    options: list[JsonValue]
    shipping: dict[str, JsonValue]
    notices: dict[str, JsonValue]
    channel_fields: dict[str, JsonValue]
    status: Literal["draft", "confirmed", "registered"]
    content_version: int
    confirmed_version: int | None
    confirmed_at: datetime | None
    updated_at: datetime


class ListingPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    expected_version: int = Field(ge=1)
    title: str | None = None
    detail_html: str | None = None
    selected_thumbnail_id: UUID | None = None
    sale_price: Decimal | None = Field(default=None, ge=0)
    category_code: str | None = None
    options: list[JsonValue] | None = None
    shipping: dict[str, JsonValue] | None = None
    notices: dict[str, JsonValue] | None = None
    channel_fields: dict[str, JsonValue] | None = None

    @model_validator(mode="after")
    def require_non_null_containers(self) -> "ListingPatch":
        for field in ("options", "shipping", "notices", "channel_fields"):
            if field in self.model_fields_set and getattr(self, field) is None:
                raise ValueError("목록과 객체 필드는 null로 저장할 수 없습니다.")
        return self


class ConfirmRequest(BaseModel):
    expected_version: int = Field(ge=1)


class GenerateRequest(BaseModel):
    channels: list[Channel] = Field(min_length=1, max_length=2)
    scope: Literal["all", "text", "thumbnails"] = "all"
    expected_versions: dict[Channel, int] = {}
    image_usage_confirmed: bool = False

    @model_validator(mode="after")
    def unique_channels(self) -> "GenerateRequest":
        if len(set(self.channels)) != len(self.channels):
            raise ValueError("채널을 중복 선택할 수 없습니다.")
        return self
