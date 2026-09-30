"""텍스트·썸네일 생성 결과를 채널별 draft로 저장한다."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.ai.base import ImageGenerator, TextGenerator
from app.core.config import Config
from app.models import Asset, Job, Listing, Product
from app.schemas.listing import GenerateRequest
from app.schemas.product import ProductData, ProductRead
from app.services.assets import asset_path
from app.services.budget import BudgetError, reserve_call, setting_value, settle_call
from app.services.html import assemble_detail
from app.services.listings import reset_confirmation


def image_assets(session: Session, product: Product, kind: str) -> list[Asset]:
    return list(
        session.scalars(
            select(Asset)
            .where(
                Asset.product_id == product.id,
                Asset.kind == kind,
                Asset.status == "ready",
            )
            .order_by(Asset.created_at)
        )
    )


async def create_thumbnails(
    session: Session,
    job: Job,
    product: ProductData,
    provider: ImageGenerator,
    config: Config,
) -> tuple[list[Asset], list[str]]:
    call = reserve_call(session, job.id, "image", config.ai_mode, config.ai_image_model or "mock")
    call.status = "running"
    session.commit()
    result = await provider.generate_thumbnails(product, n=3)
    settle_call(session, call, result.usage)
    assets = []
    for generated in result.images:
        asset = Asset(
            product_id=UUID(str(job.payload["product_id"])),
            kind="thumb",
            status="ready",
            mode=config.ai_mode,
            path=generated.path,
            mime_type=generated.mime_type,
            width=generated.width,
            height=generated.height,
            prompt=generated.prompt,
        )
        session.add(asset)
        assets.append(asset)
    session.commit()
    return assets, [issue.message for issue in result.issues]


def load_listing(session: Session, product: Product, channel: str) -> tuple[Listing, bool]:
    listing = session.scalar(
        select(Listing).where(Listing.product_id == product.id, Listing.channel == channel)
    )
    if listing is not None:
        return listing, False
    listing = Listing(
        product_id=product.id,
        channel=channel,
        status="draft",
        content_mode="mock",
        currency=product.currency,
        options=product.options or [],
        shipping=product.shipping or {},
    )
    session.add(listing)
    session.flush()
    return listing, True


async def apply_channel(
    session: Session,
    job: Job,
    product: Product,
    data: ProductData,
    channel: str,
    request: GenerateRequest,
    thumbnails: list[Asset],
    text: TextGenerator,
    config: Config,
) -> tuple[UUID, list[str]]:
    listing, new = load_listing(session, product, channel)
    errors: list[str] = []
    changed = False
    if request.scope in {"all", "text"}:
        call = reserve_call(session, job.id, "text", config.ai_mode, config.ai_text_model or "mock")
        call.status = "running"
        session.commit()
        result = await text.generate_detail(
            data, channel, str(setting_value(session, "default_tone") or "")
        )
        settle_call(session, call, result.usage)
        errors.extend(issue.message for issue in result.issues)
        if result.content is not None:
            sources = (
                image_assets(session, product, "source")
                if product.image_usage_allowed is True or request.image_usage_confirmed
                else []
            )
            listing.title = result.content.title
            listing.detail_html = assemble_detail(
                result.content, [str(asset.id) for asset in sources]
            )
            changed = True
    if thumbnails:
        listing.thumbnail_ids = [str(asset.id) for asset in thumbnails]
        listing.selected_thumbnail_id = thumbnails[0].id
        changed = True
    if changed:
        if not new:
            reset_confirmation(listing)
        listing.content_mode = config.ai_mode if request.scope == "all" or new else "mixed"
    session.commit()
    return listing.id, errors


async def generate_product(
    job_id: UUID,
    session: Session,
    text: TextGenerator,
    image: ImageGenerator,
    config: Config,
) -> None:
    job = session.get(Job, job_id)
    if job is None:
        return
    product = session.get(Product, UUID(str(job.payload["product_id"])))
    if product is None:
        raise LookupError("상품을 찾을 수 없습니다.")
    request = GenerateRequest.model_validate(job.payload["request"])
    data = ProductRead.model_validate(product)
    data.reference_image_paths = [
        asset_path(config.assets_dir, asset.path)
        for asset in image_assets(session, product, "source")
        if asset.path
    ]
    thumbnails: list[Asset] = []
    errors: list[str] = []
    if request.scope in {"all", "thumbnails"}:
        try:
            thumbnails, errors = await create_thumbnails(session, job, data, image, config)
        except BudgetError as error:
            session.rollback()
            errors.append(str(error))
    listing_ids = []
    for channel in request.channels:
        try:
            listing_id, channel_errors = await apply_channel(
                session, job, product, data, channel, request, thumbnails, text, config
            )
            listing_ids.append(str(listing_id))
            errors.extend(channel_errors)
        except BudgetError as error:
            session.rollback()
            errors.append(str(error))
    job.result = {"listing_ids": listing_ids, "errors": errors}
    job.status = "partial" if errors and listing_ids else "failed" if errors else "succeeded"
    session.commit()
