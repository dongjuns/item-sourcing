"""백그라운드 외부 작업은 단일 프로세스에서 한 번에 하나씩 실행한다."""

import asyncio
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.registry import Registry
from app.core.config import Config
from app.models import AICall, Job
from app.models.base import utc_now
from app.services.collect import collect_product
from app.services.generate import generate_product


class Runner:
    def __init__(self, sessions: sessionmaker[Session], registry: Registry, config: Config) -> None:
        self.sessions, self.registry, self.config = sessions, registry, config
        self.lock = asyncio.Lock()

    def recover(self) -> None:
        with self.sessions() as session:
            for job in session.scalars(select(Job).where(Job.status.in_(["queued", "running"]))):
                job.status, job.finished_at = "interrupted", utc_now()
                job.result = {
                    **job.result,
                    "errors": ["재시작으로 중단했습니다. 수동으로 다시 시도하세요."],
                }
            for call in session.scalars(
                select(AICall).where(AICall.status.in_(["reserved", "running"]))
            ):
                call.status = "released" if call.status == "reserved" else "unknown"
            session.commit()

    async def run(self, job_id: UUID) -> None:
        async with self.lock:
            with self.sessions() as session:
                job = session.get(Job, job_id)
                if job is None or job.status != "queued":
                    return
                job.status, job.started_at = "running", utc_now()
                session.commit()
                try:
                    if job.kind == "collect":
                        adapter = self.registry.source_for(str(job.payload["url"]))
                        if adapter is None:
                            raise ValueError("지원 소싱처가 아닙니다.")
                        await collect_product(
                            job_id, session, adapter, self.registry.http, self.config
                        )
                    elif job.kind == "generate":
                        await generate_product(
                            job_id, session, self.registry.text, self.registry.image, self.config
                        )
                except Exception:
                    session.rollback()
                    job = session.get(Job, job_id)
                    if job is not None:
                        job.status, job.result = (
                            "failed",
                            {"errors": ["작업을 완료하지 못했습니다. 설정과 원본을 확인하세요."]},
                        )
                    for call in session.scalars(
                        select(AICall).where(AICall.job_id == job_id, AICall.status == "running")
                    ):
                        call.status = "unknown"
                if job is not None:
                    job.finished_at = utc_now()
                session.commit()
