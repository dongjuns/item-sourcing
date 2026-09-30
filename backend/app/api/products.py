"""상품 API는 입력 검증과 서비스 호출만 담당한다."""

from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, Query
from pydantic import JsonValue
from sqlalchemy import select

from app.api.dependencies import DB, Worker
from app.models import Job, Product
from app.schemas.api import AssetRead, CollectRequest, JobAccepted, JobRead
from app.schemas.listing import GenerateRequest, ListingRead
from app.schemas.product import ProductRead
from app.services.assets import list_assets
from app.services.jobs import prepare_collect, prepare_generation

router = APIRouter()


@router.post("/products/from-url", status_code=202)
def from_url(
    body: CollectRequest, background: BackgroundTasks, db: DB, worker: Worker
) -> JobAccepted:
    adapter = worker.registry.source_for(body.url.strip())
    job = prepare_collect(db, body.url.strip(), adapter)
    background.add_task(worker.run, job.id)
    return JobAccepted(job_id=job.id)


@router.get("/products")
def products(
    db: DB, page: int = Query(1, ge=1), source: str | None = None, status: str | None = None
) -> list[ProductRead]:
    query = select(Product).order_by(Product.created_at.desc()).offset((page - 1) * 20).limit(20)
    if source:
        query = query.where(Product.source == source)
    if status:
        query = query.where(Product.collection_status == status)
    return [ProductRead.model_validate(row) for row in db.scalars(query)]


@router.get("/products/{product_id}")
def product(product_id: UUID, db: DB) -> ProductRead:
    row = db.get(Product, product_id)
    if row is None:
        raise LookupError("상품을 찾을 수 없습니다.")
    return ProductRead.model_validate(row)


@router.get("/products/{product_id}/raw")
def raw(product_id: UUID, db: DB) -> dict[str, JsonValue]:
    return product(product_id, db).raw


@router.get("/products/{product_id}/assets")
def assets(product_id: UUID, db: DB) -> list[AssetRead]:
    product(product_id, db)
    return [AssetRead.model_validate(asset) for asset in list_assets(db, product_id)]


@router.get("/products/{product_id}/listings")
def listings(product_id: UUID, db: DB) -> list[ListingRead]:
    from app.models import Listing

    product(product_id, db)
    return [
        ListingRead.model_validate(row)
        for row in db.scalars(select(Listing).where(Listing.product_id == product_id))
    ]


@router.post("/products/{product_id}/generate", status_code=202)
def generate(
    product_id: UUID, body: GenerateRequest, background: BackgroundTasks, db: DB, worker: Worker
) -> JobAccepted:
    job = prepare_generation(db, product_id, body)
    background.add_task(worker.run, job.id)
    return JobAccepted(job_id=job.id)


@router.get("/jobs/{job_id}")
def job(job_id: UUID, db: DB) -> JobRead:
    row = db.get(Job, job_id)
    if row is None:
        raise LookupError("작업을 찾을 수 없습니다.")
    return JobRead.model_validate(row)
