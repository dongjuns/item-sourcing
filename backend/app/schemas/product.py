"""소싱처가 공통으로 반환하는 상품 모델."""

from datetime import datetime
from decimal import Decimal
from pathlib import Path
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, JsonValue


class Issue(BaseModel):
    code: str
    message: str
    field: str | None = None
    severity: Literal["warning", "error"] = "warning"


class ProductOption(BaseModel):
    source_option_id: str | None = None
    label: str | None = None
    attributes: dict[str, str] | None = None
    wholesale_price: Decimal | None = Field(default=None, ge=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    available: bool | None = None


class ImageRef(BaseModel):
    source_url: str
    role: str = "source"
    sort_order: int = 0


class Shipping(BaseModel):
    fee: Decimal | None = Field(default=None, ge=0)
    fee_type: str | None = None
    free_shipping_threshold: Decimal | None = None
    remote_area_fee: Decimal | None = None
    dispatch_days: int | None = None
    origin: str | None = None


class ProductData(BaseModel):
    source: str
    source_url: str
    fetched_at: datetime
    source_product_id: str | None = None
    acquisition_mode: Literal["live", "mock"] = "live"
    collection_status: Literal["complete", "partial", "failed"] = "partial"
    name: str | None = None
    currency: str | None = None
    wholesale_price: Decimal | None = Field(default=None, ge=0)
    minimum_order_quantity: int | None = Field(default=None, ge=0)
    stock_quantity: int | None = Field(default=None, ge=0)
    options: list[ProductOption] | None = None
    images: list[ImageRef] | None = None
    shipping: Shipping | None = None
    detail_html: str | None = None
    image_usage_allowed: bool | None = None
    reference_image_paths: list[Path] = Field(default_factory=list, exclude=True)
    raw: dict[str, JsonValue]
    issues: list[Issue] = []


class ProductRead(ProductData):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime


class RawProduct(BaseModel):
    source: str
    source_url: str
    fetched_at: datetime
    payload: dict[str, JsonValue]
    acquisition_mode: Literal["live", "mock"] = "live"


class FetchResult(BaseModel):
    raw: RawProduct | None = None
    issues: list[Issue] = []


class NormalizeResult(BaseModel):
    product: ProductData | None = None
    issues: list[Issue] = []
