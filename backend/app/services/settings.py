"""일반 설정만 편집하고 비밀은 env로 관리한다."""

from decimal import Decimal, InvalidOperation

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AICall, Setting
from app.schemas.api import ResolveCallRequest
from app.services.budget import pricing_for
from app.services.listings import ReviewError

EDITABLE_KEYS = {
    "daily_ai_limit",
    "monthly_ai_limit",
    "ai_pricing",
    "default_tone",
    "channel_fees",
    "shipping_costs",
}


def finite_money(value: JsonValue) -> Decimal:
    try:
        number = Decimal(str(value))
        if not number.is_finite() or number < 0:
            raise ValueError
    except (ValueError, InvalidOperation):
        raise ReviewError("금액은 0 이상의 유한한 숫자여야 합니다.") from None
    return number


def update_settings(session: Session, values: dict[str, JsonValue]) -> None:
    if set(values) - EDITABLE_KEYS:
        raise ReviewError("수정할 수 없는 설정 키입니다.")
    session.execute(
        select(Setting).where(Setting.key == "ai_budget_lock").with_for_update()
    ).scalar_one()
    for key, value in values.items():
        if key in {"daily_ai_limit", "monthly_ai_limit"} and value is not None:
            value = str(finite_money(value))
        if key == "default_tone" and (not isinstance(value, str) or len(value) > 200):
            raise ReviewError("톤은 200자 이하 문자열이어야 합니다.")
        row = session.get(Setting, key)
        if row is not None:
            row.value = value
    session.flush()
    if values.get("ai_pricing") is not None:
        pricing_for(session, "text")
        pricing_for(session, "image")
    session.commit()


def resolve_call(session: Session, call: AICall, request: ResolveCallRequest) -> None:
    if call.status != "unknown":
        raise ReviewError("과금 확인이 필요한 호출만 정산할 수 있습니다.")
    actual = finite_money(request.actual_cost_krw)
    call.status, call.actual_cost_krw = "settled", actual
    call.resolution = {"evidence": request.evidence, "actual_cost_krw": str(actual)}
    if actual > call.reserved_cost_krw:
        row = session.get(Setting, "ai_budget_blocked")
        if row is not None:
            row.value = True
    session.commit()
