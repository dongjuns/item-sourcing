"""생성 요청 전 계정·모델·참조 사진·전체 예약 비용을 확인한다."""

from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import Config
from app.models import Asset, Product, Setting
from app.schemas.api import GenerationPlan
from app.schemas.listing import GenerateRequest
from app.services.budget import check_available_budget, pricing_for
from app.services.listings import ReviewError


def generation_plan(
    session: Session, product: Product, request: GenerateRequest, config: Config
) -> GenerationPlan:
    text_calls = len(request.channels) if request.scope in {"all", "text"} else 0
    image_calls = 1 if request.scope in {"all", "thumbnails"} else 0
    plan = GenerationPlan(
        mode=config.ai_mode,
        text_calls=text_calls,
        image_calls=image_calls,
        image_count=3 if image_calls else 0,
        reserved_cost_krw=Decimal(0),
    )
    if config.ai_mode == "mock":
        return plan
    if not config.openai_api_key.get_secret_value():
        raise ReviewError("OPENAI_API_KEY를 서버 .env에 설정하세요.")
    session.execute(
        select(Setting).where(Setting.key == "ai_budget_lock").with_for_update()
    ).scalar_one()
    for kind, count, model in (
        ("text", text_calls, config.ai_text_model),
        ("image", image_calls, config.ai_image_model),
    ):
        if not count:
            continue
        if not model:
            raise ReviewError("사용할 AI 모델을 서버 .env에 설정하세요.")
        pricing = pricing_for(session, kind, model)
        plan.reserved_cost_krw += Decimal(str(pricing["call_limit_krw"])) * count
    if (
        image_calls
        and session.scalar(
            select(Asset.id)
            .where(
                Asset.product_id == product.id,
                Asset.kind == "source",
                Asset.status == "ready",
            )
            .limit(1)
        )
        is None
    ):
        raise ReviewError("썸네일 생성에 필요한 원본 사진이 없습니다.")
    check_available_budget(session, plan.reserved_cost_krw)
    return plan
