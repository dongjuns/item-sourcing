"""예시 수수료와 비용을 실제 값처럼 넣지 않는다."""

from pydantic import JsonValue
from sqlalchemy.orm import Session

from app.db.session import session_factory
from app.models import Setting

DEFAULTS: dict[str, JsonValue] = {
    "daily_ai_limit": None,
    "monthly_ai_limit": None,
    "ai_pricing": None,
    "ai_budget_lock": {},
    "ai_budget_blocked": False,
    "default_tone": "담백한 설명",
    "channel_modes": {"coupang": "mock", "smartstore": "mock"},
    "channel_fees": {"coupang": None, "smartstore": None},
    "shipping_costs": None,
}


def seed_settings(session: Session) -> None:
    for key, value in DEFAULTS.items():
        if session.get(Setting, key) is None:
            session.add(Setting(key=key, value=value))
    session.commit()


if __name__ == "__main__":
    with session_factory()() as session:
        seed_settings(session)
    print("기본 설정을 저장했습니다.")
