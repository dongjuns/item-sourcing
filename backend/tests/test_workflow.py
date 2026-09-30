"""수집·금액·생성·검토 흐름을 외부 호출 없이 검증한다."""

from conftest import TEST_URL
from fastapi.testclient import TestClient


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
