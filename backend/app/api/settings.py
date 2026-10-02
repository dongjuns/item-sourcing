"""설정 조회에 키나 DB 접속 문자열을 포함하지 않는다."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import JsonValue
from sqlalchemy import select

from app.api.dependencies import DB, Worker
from app.core.config import Config, get_config
from app.models import AICall, Setting
from app.schemas.api import AppStatus, ResolveCallRequest, SettingsPatch, SettingsRead
from app.services.settings import EDITABLE_KEYS, resolve_call, update_settings

router = APIRouter()
ConfigDep = Annotated[Config, Depends(get_config)]


@router.get("/settings")
def settings(db: DB, worker: Worker, config: ConfigDep) -> SettingsRead:
    values = {
        row.key: row.value
        for row in db.scalars(
            select(Setting).where(Setting.key.in_(EDITABLE_KEYS | {"ai_budget_blocked"}))
        )
    }
    return SettingsRead(
        values=values,
        status=AppStatus(
            source_mode=config.source_mode,
            ai_mode=config.ai_mode,
            sources=[source.name for source in worker.registry.sources],
            domeggook_key_configured=bool(config.domeggook_api_key.get_secret_value()),
            ai_key_configured=bool(config.openai_api_key.get_secret_value()),
            ai_text_model=config.ai_text_model,
            ai_image_model=config.ai_image_model,
        ),
    )


@router.patch("/settings")
def patch(body: SettingsPatch, db: DB, worker: Worker, config: ConfigDep) -> SettingsRead:
    update_settings(db, body.values)
    return settings(db, worker, config)


@router.get("/ai-calls")
def calls(db: DB) -> list[dict[str, JsonValue]]:
    return [
        {
            "id": str(row.id),
            "kind": row.kind,
            "mode": row.mode,
            "status": row.status,
            "reserved_cost_krw": str(row.reserved_cost_krw),
            "actual_cost_krw": str(row.actual_cost_krw)
            if row.actual_cost_krw is not None
            else None,
            "created_at": row.created_at.isoformat(),
            "usage": row.usage,
        }
        for row in db.scalars(select(AICall).order_by(AICall.created_at.desc()).limit(100))
    ]


@router.post("/ai-calls/{call_id}/resolve")
def resolve(call_id: UUID, body: ResolveCallRequest, db: DB) -> dict[str, str]:
    call = db.execute(
        select(AICall).where(AICall.id == call_id).with_for_update()
    ).scalar_one_or_none()
    if call is None:
        raise LookupError("호출 기록을 찾을 수 없습니다.")
    resolve_call(db, call, body)
    return {"status": call.status}
