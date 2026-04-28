import asyncio
from datetime import datetime, timezone
from typing import Optional

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

_scheduler: Optional[AsyncIOScheduler] = None
_JOB_ID = "cheongyak_ingestion"


def _run_ingestion_sync() -> None:
    """APScheduler는 동기 콜백을 요구하므로 asyncio.create_task로 위임."""
    from app.ingestion.pipeline import run_ingestion
    asyncio.create_task(run_ingestion())


def start_scheduler() -> None:
    global _scheduler
    settings = get_settings()

    _scheduler = AsyncIOScheduler()
    _scheduler.add_job(
        _run_ingestion_sync,
        trigger=IntervalTrigger(hours=settings.scheduler_interval_hours),
        id=_JOB_ID,
        replace_existing=True,
        misfire_grace_time=300,
    )
    _scheduler.start()
    logger.info(
        "스케줄러 시작",
        interval_hours=settings.scheduler_interval_hours,
    )


def stop_scheduler() -> None:
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        logger.info("스케줄러 종료")


def is_scheduler_running() -> bool:
    return _scheduler is not None and _scheduler.running


def get_next_run_time() -> Optional[str]:
    if not _scheduler or not _scheduler.running:
        return None
    job = _scheduler.get_job(_JOB_ID)
    if job and job.next_run_time:
        return job.next_run_time.isoformat()
    return None
