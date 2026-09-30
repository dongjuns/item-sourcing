"""모델과 환경설정으로 Alembic을 실행한다."""

from alembic import context

from app.core.config import get_config
from app.db.session import build_engine
from app.models import Base


def run_offline() -> None:
    context.configure(
        url=get_config().database_url.get_secret_value(),
        target_metadata=Base.metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_online() -> None:
    engine = build_engine(get_config().database_url.get_secret_value())
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=Base.metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()
    engine.dispose()


if context.is_offline_mode():
    run_offline()
else:
    run_online()
