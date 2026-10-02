"""앱이 만든 작업 실행기를 요청에 제공한다."""

from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_session
from app.workers.runner import Runner

DB = Annotated[Session, Depends(get_session)]


def get_runner(request: Request) -> Runner:
    return cast(Runner, request.app.state.runner)


Worker = Annotated[Runner, Depends(get_runner)]
