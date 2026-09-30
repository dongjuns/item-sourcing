"""지정한 상품 1건을 실제 API 흐름으로 수집한다. AI·채널 등록은 호출하지 않는다."""

import argparse
import json

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.core.config import Config
from app.db.session import build_engine
from app.main import create_app


def verify(url: str) -> int:
    config = Config(
        source_mode="live",
        ai_mode="mock",
        basic_auth_password=SecretStr("verification-only-password"),
    )
    engine = build_engine(config.database_url.get_secret_value())
    app = create_app(config, engine)
    with TestClient(app) as client:
        client.auth = (config.basic_auth_username, "verification-only-password")
        response = client.post("/api/products/from-url", json={"url": url})
        if response.status_code != 202:
            print("수집 요청이 거부됐습니다. 설정과 URL을 확인하세요.")
            return 1
        job = client.get(f"/api/jobs/{response.json()['job_id']}").json()
        product_id = job.get("result", {}).get("product_id")
        if not product_id:
            print(json.dumps(job["result"], ensure_ascii=False))
            return 2
        product = client.get(f"/api/products/{product_id}").json()
        assets = client.get(f"/api/products/{product_id}/assets").json()
        quantity = max(product.get("minimum_order_quantity") or 1, 1)
        quote = client.get(f"/api/products/{product_id}/quote?quantity={quantity}").json()
        summary = {
            "product_id": product_id,
            "name": product["name"],
            "status": job["status"],
            "quote": quote,
            "detail_text_length": len(product.get("detail_text") or ""),
            "downloaded_images": sum(row["status"] == "ready" for row in assets),
            "failed_images": sum(row["status"] != "ready" for row in assets),
            "image_dimensions": [[row["width"], row["height"]] for row in assets],
            "issues": product["issues"],
        }
        folder = config.assets_dir / "verification"
        folder.mkdir(parents=True, exist_ok=True)
        (folder / "collection-result.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2)
        )
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    engine.dispose()
    return 0 if job["status"] == "succeeded" else 3


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="상품 1건 실제 수집·이미지 다운로드 검증")
    parser.add_argument("url")
    raise SystemExit(verify(parser.parse_args().url))
