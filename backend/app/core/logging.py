"""외부 HTTP 요청 URL과 인증 값을 로그에 남기지 않는다."""

import logging


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s %(message)s")
    for name in ("httpx", "httpcore", "sqlalchemy.engine"):
        logging.getLogger(name).setLevel(logging.CRITICAL)
