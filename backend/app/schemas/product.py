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


class PriceTier(BaseModel):
    minimum_quantity: int = Field(ge=1)
    unit_price: Decimal = Field(ge=0)


class Shipping(BaseModel):
    method: str | None = None
    fee: Decimal | None = Field(default=None, ge=0)
    fee_type: str | None = None
    fee_table: str | None = None
    payment_method: str | None = None
    fee_calculation: Literal["fixed", "quantity_tiers", "unknown"] = "unknown"
    quantity_fee_tiers: list[PriceTier] = Field(default_factory=list)
    free_shipping_threshold: Decimal | None = None
    remote_area_fee: Decimal | None = None
    jeju_fee: Decimal | None = None
    dispatch_days: int | None = None
    bundle_shipping: Literal["allowed", "not_allowed", "conditional", "unknown"] = "unknown"
    bundle_threshold: Decimal | None = Field(default=None, ge=0)
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
    price_tiers: list[PriceTier] = Field(default_factory=list)
    minimum_order_quantity: int | None = Field(default=None, ge=0)
    purchase_unit: int | None = Field(default=None, ge=1)
    maximum_order_quantity: int | None = Field(default=None, ge=1)
    stock_quantity: int | None = Field(default=None, ge=0)
    options: list[ProductOption] | None = None
    images: list[ImageRef] | None = None
    shipping: Shipping | None = None
    detail_html: str | None = None
    detail_text: str | None = None
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


class ProductQuote(BaseModel):
    quantity: int
    currency: str | None
    unit_price: Decimal | None = None
    product_amount: Decimal | None = None
    shipping_fee: Decimal | None = None
    total_amount: Decimal | None = None
    issues: list[Issue] = Field(default_factory=list)
