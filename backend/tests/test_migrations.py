"""마이그레이션의 기존 원본 보존과 PostgreSQL DDL을 검증한다."""

from io import StringIO
from pathlib import Path

import pytest
from alembic import command
from alembic.config import Config as AlembicConfig
from sqlalchemy import text

from app.core.config import get_config
from app.db.session import build_engine


def test_upgrade_preserves_existing_raw(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    url = f"sqlite+pysqlite:///{tmp_path / 'migration.sqlite3'}"
    monkeypatch.setenv("DATABASE_URL", url)
    get_config.cache_clear()
    config = AlembicConfig("alembic.ini")
    try:
        command.upgrade(config, "b73c2a2d90f8")
        engine = build_engine(url)
        with engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO products (id, created_at, fetched_at, source, source_url, "
                    "acquisition_mode, collection_status, raw, issues) VALUES "
                    "('00000000000000000000000000000001', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP, "
                    "'test', 'https://example.test/item', 'mock', 'partial', :raw, '[]')"
                ),
                {"raw": '{"kept":true}'},
            )
        command.upgrade(config, "head")
        command.check(config)
        with engine.connect() as connection:
            row = connection.execute(
                text("SELECT raw, price_tiers, detail_text FROM products")
            ).one()
        assert row[0] == '{"kept":true}' and row[1] == "[]" and row[2] is None
        engine.dispose()
    finally:
        get_config.cache_clear()


def test_postgresql_offline_sql_contains_thumbnail_fk(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "postgresql+psycopg://localhost/fixture")
    get_config.cache_clear()
    output = StringIO()
    config = AlembicConfig("alembic.ini", output_buffer=output)
    try:
        command.upgrade(config, "head", sql=True)
        sql = output.getvalue()
        assert "ADD CONSTRAINT fk_listing_thumbnail FOREIGN KEY(selected_thumbnail_id)" in sql
        assert "ALTER TABLE products ADD COLUMN detail_text" in sql
        assert "JSONB" in sql
    finally:
        get_config.cache_clear()
