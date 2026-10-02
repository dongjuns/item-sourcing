"""상품 본문 텍스트와 수량별 가격 정보. 기존 원본·이력은 보존한다."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "98e6afa86b39"
down_revision: str | None = "b73c2a2d90f8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    json_type = sa.JSON(none_as_null=True).with_variant(
        postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
    )
    op.add_column(
        "products",
        sa.Column("price_tiers", json_type, nullable=False, server_default=sa.text("'[]'")),
    )
    op.add_column(
        "products",
        sa.Column(
            "purchase_unit",
            sa.Integer(),
            sa.CheckConstraint("purchase_unit IS NULL OR purchase_unit >= 1"),
            nullable=True,
        ),
    )
    op.add_column(
        "products",
        sa.Column(
            "maximum_order_quantity",
            sa.Integer(),
            sa.CheckConstraint("maximum_order_quantity IS NULL OR maximum_order_quantity >= 1"),
            nullable=True,
        ),
    )
    op.add_column("products", sa.Column("detail_text", sa.Text(), nullable=True))


def downgrade() -> None:
    for column in ("detail_text", "maximum_order_quantity", "purchase_unit", "price_tiers"):
        op.drop_column("products", column)
