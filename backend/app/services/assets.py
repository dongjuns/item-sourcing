"""이미지 파일 저장은 상품 원본과 분리해 실패를 보존한다."""

import hashlib
from io import BytesIO
from pathlib import Path
from uuid import UUID, uuid4

from PIL import Image
from sqlalchemy.orm import Session

from app.adapters.http import SourceHTTP
from app.core.config import Config
from app.models import Asset, Product
from app.schemas.product import Issue

MAX_PIXELS = 40_000_000
Image.MAX_IMAGE_PIXELS = MAX_PIXELS


def save_image(data: bytes, root: Path) -> tuple[str, int, int, str]:
    with Image.open(BytesIO(data)) as image:
        image.load()
        if image.width * image.height > MAX_PIXELS:
            raise ValueError("이미지 픽셀 제한 초과")
        path = f"images/{uuid4()}.png"
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        image.convert("RGB").save(target, format="PNG")
        checksum = hashlib.sha256(target.read_bytes()).hexdigest()
        return path, image.width, image.height, checksum


async def download_images(
    product: Product,
    session: Session,
    http: SourceHTTP,
    config: Config,
) -> None:
    issues = list(product.issues)
    images = product.images or []
    for item in images[: config.max_source_images]:
        if not isinstance(item, dict) or not isinstance(item.get("source_url"), str):
            continue
        url = item["source_url"]
        asset = Asset(
            product_id=product.id, kind="source", mode=product.acquisition_mode, source_url=url
        )
        try:
            path, width, height, checksum = save_image(await http.download(url), config.assets_dir)
            asset.path, asset.width, asset.height, asset.checksum = path, width, height, checksum
            asset.mime_type, asset.status = "image/png", "ready"
        except Exception:
            asset.status, asset.error = (
                "failed",
                "이미지 다운로드 실패: 호스트·파일·네트워크를 확인하세요.",
            )
            issues.append(
                Issue(code="image_download", field="images", message=asset.error).model_dump(
                    mode="json"
                )
            )
        session.add(asset)
        session.commit()
    if len(images) > config.max_source_images:
        issues.append(
            Issue(
                code="image_limit",
                field="images",
                message="일부 이미지가 내부 수집 한도에 걸렸습니다.",
            ).model_dump(mode="json")
        )
    product.issues = issues
    if issues and product.collection_status != "failed":
        product.collection_status = "partial"
    session.commit()


def asset_path(root: Path, relative_path: str) -> Path:
    path = (root / relative_path).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file():
        raise ValueError("이미지 파일을 찾을 수 없습니다.")
    return path


def list_assets(session: Session, product_id: UUID) -> list[Asset]:
    from sqlalchemy import select

    return list(
        session.scalars(
            select(Asset).where(Asset.product_id == product_id).order_by(Asset.created_at)
        )
    )
