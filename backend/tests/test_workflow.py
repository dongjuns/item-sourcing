"""수집·금액·생성·검토 흐름을 외부 호출 없이 검증한다."""

from conftest import TEST_URL
from fastapi.testclient import TestClient
from pydantic import SecretStr
from sqlalchemy import func, select

from app.models import Job


def collect(client: TestClient) -> str:
    response = client.post("/api/products/from-url", json={"url": TEST_URL})
    assert response.status_code == 202
    job = client.get(f"/api/jobs/{response.json()['job_id']}").json()
    assert job["status"] == "succeeded", job
    return str(job["result"]["product_id"])


def test_collection_quote_and_assets(client: TestClient) -> None:
    product_id = collect(client)
    product = client.get(f"/api/products/{product_id}").json()
    assert product["name"] == "촉촉함과 생기를 더하는 남성 올인원 세럼세트 110ml"
    assert len(product["detail_text"]) == 569
    assert product["raw"]["domeggook"]["price"]["dome"] == "35000"
    assets = client.get(f"/api/products/{product_id}/assets").json()
    assert len(assets) == 3 and all(row["status"] == "ready" for row in assets)
    assert client.get(f"/api/assets/{assets[0]['id']}").headers["content-type"] == "image/png"
    for quantity, amount, total in [
        (1, "35000.0000", "37750.0000"),
        (2, "70000.0000", "72750.0000"),
    ]:
        quote = client.get(f"/api/products/{product_id}/quote?quantity={quantity}").json()
        assert quote["product_amount"] == amount
        assert quote["total_amount"] == total
    assert client.get(f"/api/products/{product_id}/quote?quantity=0").status_code == 422


def test_generate_edit_confirm_and_reconfirmation(client: TestClient) -> None:
    product_id = collect(client)
    generated = client.post(
        f"/api/products/{product_id}/generate", json={"channels": ["coupang", "smartstore"]}
    )
    assert generated.status_code == 202
    job = client.get(f"/api/jobs/{generated.json()['job_id']}").json()
    assert job["status"] == "succeeded", job
    listings = client.get(f"/api/products/{product_id}/listings").json()
    assert len(listings) == 2
    listing = listings[0]
    assert listing["status"] == "draft" and listing["content_mode"] == "mock"
    assert len(listing["thumbnail_ids"]) == 3
    endpoint = f"/api/listings/{listing['id']}"
    assert client.post(endpoint + "/confirm", json={"expected_version": 1}).status_code == 409
    unsafe_html = (
        '<p>검토한 설명</p><script>제거</script><img src="https://evil.test/x" onerror="alert(1)">'
    )
    changed = client.patch(
        endpoint,
        json={
            "expected_version": 1,
            "sale_price": "45000",
            "detail_html": unsafe_html,
        },
    ).json()
    assert "<script>" not in changed["detail_html"] and "onerror" not in changed["detail_html"]
    assert "evil.test" not in changed["detail_html"]
    assert changed["content_version"] == 2
    assert (
        client.patch(endpoint, json={"expected_version": 1, "title": "오래된 편집"}).status_code
        == 409
    )
    confirmed = client.post(endpoint + "/confirm", json={"expected_version": 2}).json()
    assert confirmed["status"] == "confirmed" and confirmed["confirmed_version"] == 2
    edited = client.patch(endpoint, json={"expected_version": 2, "title": "수정한 제목"}).json()
    assert edited["status"] == "draft" and edited["confirmed_version"] is None
    assert (
        client.post(
            f"/api/products/{product_id}/generate",
            json={"channels": [listing["channel"]], "expected_versions": {listing["channel"]: 2}},
        ).status_code
        == 409
    )
    assert client.post(endpoint + "/register", json={}).status_code == 404


def test_auth_and_unsupported_source(client: TestClient) -> None:
    assert client.get("/api/products", auth=("owner", "wrong-password")).status_code == 401
    assert (
        client.post("/api/products/from-url", json={"url": "https://evil.test/product"}).status_code
        == 409
    )
    assert client.get("/openapi.json").status_code == 404


def test_unconfigured_live_generation_creates_no_job(client: TestClient) -> None:
    product_id = collect(client)
    config = client.app.state.runner.config
    config.ai_mode = "live"
    config.openai_api_key = SecretStr("")
    response = client.post(f"/api/products/{product_id}/generate", json={"channels": ["coupang"]})
    assert response.status_code == 409 and "OPENAI_API_KEY" in response.json()["detail"]
    with client.app.state.runner.sessions() as session:
        assert (
            session.scalar(select(func.count()).select_from(Job).where(Job.kind == "generate")) == 0
        )


def test_full_generation_budget_and_model_check(client: TestClient) -> None:
    product_id = collect(client)
    config = client.app.state.runner.config
    config.ai_mode, config.ai_text_model, config.ai_image_model = "live", "test-text", "test-image"
    config.openai_api_key = SecretStr("fixture-ai-key")
    response = client.patch(
        "/api/settings",
        json={
            "values": {
                "daily_ai_limit": "600",
                "monthly_ai_limit": "1000",
                "ai_pricing": {
                    "text": {
                        "model": "test-text",
                        "call_limit_krw": "100",
                        "verified_at": "2026-10-01",
                        "source_url": "https://example.test/pricing",
                    },
                    "image": {
                        "model": "test-image",
                        "call_limit_krw": "500",
                        "verified_at": "2026-10-01",
                        "source_url": "https://example.test/pricing",
                    },
                },
            }
        },
    )
    assert response.status_code == 200
    body = {"channels": ["coupang", "smartstore"]}
    endpoint = f"/api/products/{product_id}"
    assert client.post(endpoint + "/generation-plan", json=body).status_code == 409
    assert client.post(endpoint + "/generate", json=body).status_code == 409
    client.patch("/api/settings", json={"values": {"daily_ai_limit": "1000"}})
    plan = client.post(endpoint + "/generation-plan", json=body).json()
    assert plan["reserved_cost_krw"] == "700"
    assert plan["text_calls"] == 2 and plan["image_count"] == 3
    config.ai_text_model = "different-model"
    assert client.post(endpoint + "/generation-plan", json=body).status_code == 409
