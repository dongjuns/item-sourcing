"""DB URL을 외부 응답이나 로그로 반환하지 않는다."""

from collections.abc import Generator
from functools import lru_cache

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_config


def build_engine(url: str) -> Engine:
    engine = create_engine(
        url,
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False} if url.startswith("sqlite") else {},
        hide_parameters=True,
    )
    if url.startswith("sqlite"):

        @event.listens_for(engine, "connect")
        def enable_foreign_keys(connection: object, _: object) -> None:
            connection.cursor().execute("PRAGMA foreign_keys=ON")  # type: ignore[attr-defined]

    return engine


@lru_cache
def get_engine() -> Engine:
    return build_engine(get_config().database_url.get_secret_value())


def session_factory() -> sessionmaker[Session]:
    return sessionmaker(get_engine(), expire_on_commit=False)


def get_session() -> Generator[Session, None, None]:
    with session_factory()() as session:
        yield session
