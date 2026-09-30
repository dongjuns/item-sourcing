"""URL 수집부터 사람 검토·확정까지 제공하는 앱."""

from collections.abc import AsyncIterator, Generator
from contextlib import asynccontextmanager

from fastapi import APIRouter, Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.registry import Registry
from app.api import assets, listings, products, settings
from app.core.config import Config, get_config
from app.core.logging import configure_logging
from app.core.security import require_auth
from app.db.seed import seed_settings
from app.db.session import build_engine, get_session
from app.services.budget import BudgetError
from app.services.listings import ReviewError
from app.workers.runner import Runner


def create_app(config: Config | None = None, engine: Engine | None = None) -> FastAPI:
    config = config or get_config()
    engine = engine or build_engine(config.database_url.get_secret_value())
    sessions = sessionmaker(engine, expire_on_commit=False)
    runner = Runner(sessions, Registry(config), config)

    @asynccontextmanager
    async def lifespan(_: FastAPI) -> AsyncIterator[None]:
        configure_logging()
        try:
            with sessions() as session:
                seed_settings(session)
            runner.recover()
        except Exception:
            raise RuntimeError("DB 준비 실패. make migrate와 DB 실행 상태를 확인하세요.") from None
        yield

    app = FastAPI(title="상품 소싱 검토", lifespan=lifespan, docs_url=None, redoc_url=None)
    app.state.runner = runner

    def db_session() -> Generator[Session, None, None]:
        with sessions() as session:
            yield session

    app.dependency_overrides[get_config] = lambda: config
    app.dependency_overrides[get_session] = db_session
    configure_routes(app, config)
    return app


def configure_routes(app: FastAPI, config: Config) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.cors_origins,
        allow_methods=["GET", "POST", "PATCH"],
        allow_headers=["Authorization", "Content-Type"],
    )
    api = APIRouter(prefix="/api", dependencies=[Depends(require_auth)])
    for router in (products.router, listings.router, settings.router, assets.router):
        api.include_router(router)
    app.include_router(api)

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(LookupError)
    async def missing(_: Request, error: LookupError) -> JSONResponse:
        return JSONResponse({"detail": str(error)}, status_code=404)

    @app.exception_handler(ReviewError)
    @app.exception_handler(BudgetError)
    async def conflict(_: Request, error: ValueError) -> JSONResponse:
        return JSONResponse({"detail": str(error)}, status_code=409)


app = create_app()
