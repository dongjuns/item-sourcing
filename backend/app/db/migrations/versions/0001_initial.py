"""상품 수집과 검토 초기 스키마"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "b73c2a2d90f8"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 초기 테이블과 제약을 생성하거나 제거한다.
    op.create_table(
        "jobs",
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("target_key", sa.Text(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column(
            "payload",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "result",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "log",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("kind IN ('collect','generate','register')"),
        sa.CheckConstraint(
            "status IN ('queued','running','succeeded','partial','failed','interrupted')"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_job_active_target",
        "jobs",
        ["kind", "target_key"],
        unique=True,
        postgresql_where=sa.text("status IN ('queued','running')"),
        sqlite_where=sa.text("status IN ('queued','running')"),
    )
    op.create_table(
        "products",
        sa.Column("source", sa.String(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=False),
        sa.Column("source_product_id", sa.String(), nullable=True),
        sa.Column("fetched_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("acquisition_mode", sa.String(), nullable=False),
        sa.Column("collection_status", sa.String(), nullable=False),
        sa.Column("name", sa.Text(), nullable=True),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("wholesale_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("minimum_order_quantity", sa.Integer(), nullable=True),
        sa.Column("stock_quantity", sa.Integer(), nullable=True),
        sa.Column(
            "options",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column(
            "images",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column(
            "shipping",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column("detail_html", sa.Text(), nullable=True),
        sa.Column("image_usage_allowed", sa.Boolean(), nullable=True),
        sa.Column(
            "raw",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "issues",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("acquisition_mode IN ('live','mock')"),
        sa.CheckConstraint("collection_status IN ('complete','partial','failed')"),
        sa.CheckConstraint("minimum_order_quantity IS NULL OR minimum_order_quantity >= 0"),
        sa.CheckConstraint("stock_quantity IS NULL OR stock_quantity >= 0"),
        sa.CheckConstraint("wholesale_price IS NULL OR wholesale_price >= 0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_products_created_at", "products", ["created_at"], unique=False)
    op.create_index(
        "ix_products_source_item", "products", ["source", "source_product_id"], unique=False
    )
    op.create_index(
        "ix_products_source_status", "products", ["source", "collection_status"], unique=False
    )
    op.create_table(
        "settings",
        sa.Column("key", sa.String(), nullable=False),
        sa.Column(
            "value",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column("encrypted_value", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("value IS NULL OR encrypted_value IS NULL"),
        sa.PrimaryKeyConstraint("key"),
    )
    op.create_table(
        "ai_calls",
        sa.Column("job_id", sa.Uuid(), nullable=False),
        sa.Column("provider", sa.String(), nullable=False),
        sa.Column("model", sa.String(), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("budget_day", sa.Date(), nullable=False),
        sa.Column("budget_month", sa.Date(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("reserved_cost_krw", sa.Numeric(precision=18, scale=4), nullable=False),
        sa.Column("actual_cost_krw", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("input_tokens", sa.Integer(), nullable=True),
        sa.Column("output_tokens", sa.Integer(), nullable=True),
        sa.Column("image_count", sa.Integer(), nullable=True),
        sa.Column(
            "pricing_snapshot",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "usage",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column(
            "resolution",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("mode IN ('live','mock')"),
        sa.CheckConstraint("status != 'settled' OR actual_cost_krw IS NOT NULL"),
        sa.CheckConstraint("status IN ('reserved','running','settled','released','unknown')"),
        sa.CheckConstraint("actual_cost_krw IS NULL OR actual_cost_krw >= 0"),
        sa.CheckConstraint("reserved_cost_krw >= 0"),
        sa.ForeignKeyConstraint(["job_id"], ["jobs.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "listings",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("content_mode", sa.String(), nullable=False),
        sa.Column("title", sa.Text(), nullable=True),
        sa.Column("detail_html", sa.Text(), nullable=True),
        sa.Column(
            "thumbnail_ids",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column("selected_thumbnail_id", sa.Uuid(), nullable=True),
        sa.Column("sale_price", sa.Numeric(precision=18, scale=4), nullable=True),
        sa.Column("currency", sa.String(), nullable=True),
        sa.Column("category_code", sa.String(), nullable=True),
        sa.Column(
            "options",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "shipping",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "notices",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column(
            "channel_fields",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("content_version", sa.Integer(), nullable=False),
        sa.Column("confirmed_version", sa.Integer(), nullable=True),
        sa.Column("confirmed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "(status = 'draft' AND confirmed_version IS NULL AND confirmed_at IS NULL) "
            "OR (status IN ('confirmed','registered') AND confirmed_version IS NOT NULL "
            "AND confirmed_version = content_version AND confirmed_at IS NOT NULL)",
            name="ck_listing_confirmation",
        ),
        sa.CheckConstraint("channel IN ('coupang','smartstore')"),
        sa.CheckConstraint("content_mode IN ('live','mock','mixed')"),
        sa.CheckConstraint("status IN ('draft','confirmed','registered')"),
        sa.CheckConstraint("content_version >= 1"),
        sa.CheckConstraint("sale_price IS NULL OR sale_price >= 0"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(
            ["selected_thumbnail_id"],
            ["assets.id"],
            name="fk_listing_thumbnail",
            ondelete="RESTRICT",
            use_alter=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("product_id", "channel", name="uq_listing_product_channel"),
    )
    op.create_table(
        "assets",
        sa.Column("product_id", sa.Uuid(), nullable=False),
        sa.Column("listing_id", sa.Uuid(), nullable=True),
        sa.Column("parent_asset_id", sa.Uuid(), nullable=True),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("source_url", sa.Text(), nullable=True),
        sa.Column("path", sa.Text(), nullable=True),
        sa.Column("mime_type", sa.String(), nullable=True),
        sa.Column("width", sa.Integer(), nullable=True),
        sa.Column("height", sa.Integer(), nullable=True),
        sa.Column("checksum", sa.String(), nullable=True),
        sa.Column("prompt", sa.Text(), nullable=True),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("kind IN ('source','thumb','detail')"),
        sa.CheckConstraint("mode IN ('live','mock')"),
        sa.CheckConstraint("status != 'ready' OR path IS NOT NULL"),
        sa.CheckConstraint("status IN ('ready','failed')"),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["parent_asset_id"], ["assets.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "registrations",
        sa.Column("listing_id", sa.Uuid(), nullable=False),
        sa.Column("channel", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column("content_version", sa.Integer(), nullable=False),
        sa.Column(
            "listing_snapshot",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=False,
        ),
        sa.Column("status", sa.String(), nullable=False),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("external_url", sa.Text(), nullable=True),
        sa.Column(
            "request",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column(
            "response",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column("error_code", sa.String(), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "resolution",
            sa.JSON(none_as_null=True).with_variant(
                postgresql.JSONB(none_as_null=True, astext_type=sa.Text()), "postgresql"
            ),
            nullable=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("mode != 'mock' OR (external_id IS NULL AND external_url IS NULL)"),
        sa.CheckConstraint("mode IN ('live','mock')"),
        sa.CheckConstraint(
            "status IN ('pending','running','succeeded','failed','unknown','simulated')"
        ),
        sa.ForeignKeyConstraint(["listing_id"], ["listings.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "uq_registration_unresolved",
        "registrations",
        ["listing_id"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending','running','unknown')"),
        sqlite_where=sa.text("status IN ('pending','running','unknown')"),
    )
    if op.get_bind().dialect.name == "postgresql":
        op.create_foreign_key(
            "fk_listing_thumbnail",
            "listings",
            "assets",
            ["selected_thumbnail_id"],
            ["id"],
            ondelete="RESTRICT",
        )
    # 초기 스키마 처리 완료


def downgrade() -> None:
    # 초기 테이블과 제약을 생성하거나 제거한다.
    op.drop_index(
        "uq_registration_unresolved",
        table_name="registrations",
        postgresql_where=sa.text("status IN ('pending','running','unknown')"),
        sqlite_where=sa.text("status IN ('pending','running','unknown')"),
    )
    op.drop_table("registrations")
    if op.get_bind().dialect.name == "postgresql":
        op.drop_constraint("fk_listing_thumbnail", "listings", type_="foreignkey")
    op.drop_table("assets")
    op.drop_table("listings")
    op.drop_table("ai_calls")
    op.drop_table("settings")
    op.drop_index("ix_products_source_status", table_name="products")
    op.drop_index("ix_products_source_item", table_name="products")
    op.drop_index("ix_products_created_at", table_name="products")
    op.drop_table("products")
    op.drop_index(
        "uq_job_active_target",
        table_name="jobs",
        postgresql_where=sa.text("status IN ('queued','running')"),
        sqlite_where=sa.text("status IN ('queued','running')"),
    )
    op.drop_table("jobs")
    # 초기 스키마 처리 완료
