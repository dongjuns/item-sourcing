"""미확인 가격·배송비와 예산 예약을 실제 값으로 오인하지 않도록 검증한다."""

from datetime import UTC, datetime
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.models import Job, Setting
from app.schemas.product import PriceTier, ProductData, Shipping
from app.schemas.results import Usage
from app.services.budget import BudgetError, reserve_call, settle_call
from app.services.quote import product_quote
from app.services.settings import update_settings


def product() -> ProductData:
    return ProductData(
        source="test",
        source_url="https://example.test/item",
        fetched_at=datetime.now(UTC),
        name="테스트 상품",
        currency="KRW",
        raw={},
        wholesale_price=35000,
        minimum_order_quantity=1,
        purchase_unit=1,
        shipping=Shipping(fee=2750, fee_calculation="fixed"),
    )


def test_tier_boundaries_and_zero_price() -> None:
    data = product()
    data.wholesale_price = None
    data.price_tiers = [
        PriceTier(minimum_quantity=1, unit_price=3800),
        PriceTier(minimum_quantity=20, unit_price=3500),
    ]
    assert product_quote(data, 19).product_amount == 72200
    assert product_quote(data, 20).product_amount == 70000
    data.price_tiers = []
    assert product_quote(data, 1).product_amount is None
    assert product_quote(data, 1).total_amount is None
    data.wholesale_price = Decimal(0)
    data.shipping = Shipping(fee=0, fee_calculation="fixed")
    assert product_quote(data, 1).total_amount == 0


def test_quantity_constraints_and_unknown_shipping() -> None:
    data = product()
    data.minimum_order_quantity, data.purchase_unit = 2, 2
    assert product_quote(data, 1).total_amount is None
    assert product_quote(data, 3).product_amount is None
    data.shipping = Shipping(fee=2750, fee_calculation="unknown")
    assert product_quote(data, 2).product_amount == 70000
    assert product_quote(data, 2).total_amount is None
    data.maximum_order_quantity = 2
    assert product_quote(data, 4).product_amount is None


def test_unknown_cost_keeps_reservation_and_release_frees_it(client: TestClient) -> None:
    with client.app.state.runner.sessions() as session:
        job = Job(kind="generate", target_key="budget-fixture", status="succeeded", payload={})
        session.add(job)
        session.commit()
        with pytest.raises(BudgetError):
            reserve_call(session, job.id, "text", "live", "test-model")
        session.rollback()
        update_settings(
            session,
            {
                "daily_ai_limit": "100",
                "monthly_ai_limit": "1000",
                "ai_pricing": {
                    "text": {
                        "model": "test-model",
                        "call_limit_krw": "60",
                        "verified_at": "test",
                        "source_url": "https://example.test/pricing",
                    },
                    "image": {
                        "model": "test-model",
                        "call_limit_krw": "60",
                        "verified_at": "test",
                        "source_url": "https://example.test/pricing",
                    },
                },
            },
        )
        call = reserve_call(session, job.id, "text", "live", "test-model")
        settle_call(session, call, Usage(billing_status="unknown"))
        with pytest.raises(BudgetError):
            reserve_call(session, job.id, "text", "live", "test-model")
        session.rollback()
        settle_call(session, call, Usage(billing_status="unbilled"))
        assert reserve_call(session, job.id, "text", "live", "test-model").status == "reserved"


def test_recovery_interrupts_jobs_and_preserves_uncertain_cost(client: TestClient) -> None:
    with client.app.state.runner.sessions() as session:
        job = Job(kind="generate", target_key="restart-fixture", status="running", payload={})
        session.add(job)
        session.commit()
        reserved = reserve_call(session, job.id, "text", "mock", "test")
        running = reserve_call(session, job.id, "image", "mock", "test")
        running.status = "running"
        session.commit()
        client.app.state.runner.recover()
        session.refresh(job)
        session.refresh(reserved)
        session.refresh(running)
        assert job.status == "interrupted"
        assert reserved.status == "released"
        assert running.status == "unknown"
        assert session.get(Setting, "daily_ai_limit").value is None
