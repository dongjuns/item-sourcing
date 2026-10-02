"""명시적으로 지정한 상품 1건만 실제 조회한다. 키와 요청 URL은 출력하지 않는다."""

import argparse
import asyncio
import json

from app.adapters.registry import Registry
from app.core.config import Config
from app.core.logging import configure_logging


async def verify(url: str) -> int:
    config = Config(source_mode="live", ai_mode="mock")
    configure_logging()
    registry = Registry(config)
    adapter = registry.source_for(url)
    if adapter is None:
        print("지원 상품 URL이 아닙니다.")
        return 1
    result = await adapter.fetch(url)
    if result.raw is None:
        print(json.dumps([issue.model_dump() for issue in result.issues], ensure_ascii=False))
        return 2
    folder = config.assets_dir / "verification"
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "source-response.json").write_text(
        result.raw.model_dump_json(indent=2), encoding="utf-8"
    )
    normalized = adapter.normalize(result.raw)
    if normalized.product is None:
        print("원본 응답을 로컬에 보존했으나 상품 정규화에 실패했습니다.")
        return 3
    product = normalized.product
    summary = {
        "source_product_id": product.source_product_id,
        "name": product.name,
        "price": str(product.wholesale_price) if product.wholesale_price is not None else None,
        "minimum_order_quantity": product.minimum_order_quantity,
        "shipping": product.shipping.model_dump(mode="json") if product.shipping else None,
        "image_count": len(product.images or []),
        "detail_html_length": len(product.detail_html or ""),
        "image_usage_allowed": product.image_usage_allowed,
        "issues": [issue.model_dump() for issue in normalized.issues + result.issues],
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if product.name and not result.issues else 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="상품 1건 읽기 전용 수집 검증")
    parser.add_argument("url")
    raise SystemExit(asyncio.run(verify(parser.parse_args().url)))
