"""수집 1회당 상품 원본을 별도 보존한다."""

from datetime import datetime
from decimal import Decimal

from pydantic import JsonValue
from sqlalchemy import CheckConstraint, DateTime, Index, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import JSON_DATA, Base, IdentityMixin


class Product(IdentityMixin, Base):
    __tablename__ = "products"
    __table_args__ = (
        CheckConstraint("collection_status IN ('complete','partial','failed')"),
        CheckConstraint("acquisition_mode IN ('live','mock')"),
        CheckConstraint("wholesale_price IS NULL OR wholesale_price >= 0"),
        CheckConstraint("minimum_order_quantity IS NULL OR minimum_order_quantity >= 0"),
        CheckConstraint("stock_quantity IS NULL OR stock_quantity >= 0"),
        Index("ix_products_source_status", "source", "collection_status"),
        Index("ix_products_source_item", "source", "source_product_id"),
        Index("ix_products_created_at", "created_at"),
    )
    source: Mapped[str] = mapped_column(String)
    source_url: Mapped[str] = mapped_column(Text)
    source_product_id: Mapped[str | None] = mapped_column(String)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    acquisition_mode: Mapped[str] = mapped_column(String)
    collection_status: Mapped[str] = mapped_column(String)
    name: Mapped[str | None] = mapped_column(Text)
    currency: Mapped[str | None] = mapped_column(String)
    wholesale_price: Mapped[Decimal | None] = mapped_column(Numeric(18, 4))
    minimum_order_quantity: Mapped[int | None]
    stock_quantity: Mapped[int | None]
    options: Mapped[list[JsonValue] | None] = mapped_column(JSON_DATA)
    images: Mapped[list[JsonValue] | None] = mapped_column(JSON_DATA)
    shipping: Mapped[dict[str, JsonValue] | None] = mapped_column(JSON_DATA)
    detail_html: Mapped[str | None] = mapped_column(Text)
    image_usage_allowed: Mapped[bool | None]
    raw: Mapped[dict[str, JsonValue]] = mapped_column(JSON_DATA)
    issues: Mapped[list[JsonValue]] = mapped_column(JSON_DATA, default=list)
