"""내부 경로 대신 인증된 자산 ID로 파일을 제공한다."""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse

from app.api.dependencies import DB
from app.core.config import Config, get_config
from app.models import Asset
from app.services.assets import asset_path

router = APIRouter()


@router.get("/assets/{asset_id}")
def image(asset_id: UUID, db: DB, config: Annotated[Config, Depends(get_config)]) -> FileResponse:
    asset = db.get(Asset, asset_id)
    if asset is None or asset.status != "ready" or not asset.path:
        raise LookupError("이미지 파일을 찾을 수 없습니다.")
    try:
        path = asset_path(config.assets_dir, asset.path)
    except ValueError:
        raise LookupError("이미지 파일을 찾을 수 없습니다.") from None
    return FileResponse(path, media_type=asset.mime_type, headers={"Cache-Control": "no-store"})
