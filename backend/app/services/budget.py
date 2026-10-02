"""DB 잠금으로 비용 예약을 직렬화한다."""

from datetime import datetime
from decimal import Decimal, InvalidOperation
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import JsonValue
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AICall, Setting
from app.models.base import utc_now
from app.schemas.results import Usage


class BudgetError(ValueError):
    pass


def setting_value(session: Session, key: str) -> JsonValue:
    row = session.get(Setting, key)
    return row.value if row is not None else None


def charged_amount(call: AICall) -> Decimal:
    if call.status == "released" or call.mode == "mock":
        return Decimal(0)
    if call.status == "settled" and call.actual_cost_krw is not None:
        return call.actual_cost_krw
    return call.reserved_cost_krw


def pricing_for(session: Session, kind: str, model: str | None = None) -> dict[str, JsonValue]:
    pricing = setting_value(session, "ai_pricing")
    item = pricing.get(kind) if isinstance(pricing, dict) else None
    if not isinstance(item, dict) or not item.get("verified_at") or not item.get("source_url"):
        raise BudgetError("확인 근거가 있는 호출별 비용 상한을 설정하세요.")
    value = item.get("call_limit_krw")
    if isinstance(value, bool) or not isinstance(value, (str, int, float)):
        raise BudgetError("호출별 비용 상한을 설정하세요.")
    try:
        limit = Decimal(str(value))
    except InvalidOperation:
        raise BudgetError("호출별 비용 상한은 숫자여야 합니다.") from None
    if not limit.is_finite() or limit <= 0:
        raise BudgetError("호출별 비용 상한은 양수여야 합니다.")
    if model is not None and item.get("model") != model:
        raise BudgetError("설정된 모델과 가격 확인 근거의 모델이 다릅니다.")
    return item


def check_available_budget(session: Session, amount: Decimal) -> None:
    if setting_value(session, "ai_budget_blocked"):
        raise BudgetError("과금 확인이 필요한 초과 호출이 있습니다.")
    day = datetime.now(ZoneInfo("Asia/Seoul")).date()
    for key, column, period in (
        ("daily_ai_limit", AICall.budget_day, day),
        ("monthly_ai_limit", AICall.budget_month, day.replace(day=1)),
    ):
        value = setting_value(session, key)
        if value is None:
            raise BudgetError("일일·월간 AI 비용 한도를 먼저 설정하세요.")
        limit = Decimal(str(value))
        calls = session.scalars(select(AICall).where(column == period))
        used = sum((charged_amount(call) for call in calls), Decimal(0))
        if used + amount > limit:
            raise BudgetError(f"AI 비용 한도 초과: 남은 금액 {max(limit - used, Decimal(0))}원")


def reserve_call(session: Session, job_id: UUID, kind: str, mode: str, model: str) -> AICall:
    session.execute(
        select(Setting).where(Setting.key == "ai_budget_lock").with_for_update()
    ).scalar_one()
    day = datetime.now(ZoneInfo("Asia/Seoul")).date()
    pricing = {} if mode == "mock" else pricing_for(session, kind, model)
    amount = Decimal(0) if mode == "mock" else Decimal(str(pricing["call_limit_krw"]))
    if mode == "live":
        check_available_budget(session, amount)
    call = AICall(
        job_id=job_id,
        provider="openai" if mode == "live" else "mock",
        model=model,
        kind=kind,
        mode=mode,
        budget_day=day,
        budget_month=day.replace(day=1),
        status="reserved",
        reserved_cost_krw=amount,
        pricing_snapshot=pricing,
    )
    session.add(call)
    session.commit()
    return call


def settle_call(session: Session, call: AICall, usage: Usage) -> None:
    call.input_tokens, call.output_tokens = usage.input_tokens, usage.output_tokens
    call.image_count, call.usage = usage.image_count, usage.provider_usage
    call.finished_at = utc_now()
    if usage.billing_status == "verified" and usage.actual_cost_krw is not None:
        call.status, call.actual_cost_krw = "settled", usage.actual_cost_krw
        if usage.actual_cost_krw > call.reserved_cost_krw:
            row = session.get(Setting, "ai_budget_blocked")
            if row is not None:
                row.value = True
    elif usage.billing_status == "unbilled":
        call.status = "released"
    else:
        call.status = "unknown"
    session.commit()
