import asyncio
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel

from app.ingestion.pipeline import get_ingestion_state, run_ingestion
from app.models.request_models import IngestStatusResponse, IngestTriggerResponse
from app.rag.vector_store import get_collection_count
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


class IngestTriggerRequest(BaseModel):
    region_codes: Optional[list[str]] = None


@router.post("/ingest/trigger", response_model=IngestTriggerResponse)
async def trigger_ingestion(
    request: IngestTriggerRequest,
    background_tasks: BackgroundTasks,
) -> IngestTriggerResponse:
    job_id = f"manual_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}"
    background_tasks.add_task(run_ingestion, request.region_codes)
    logger.info("수동 수집 트리거", job_id=job_id)
    return IngestTriggerResponse(message="수집이 시작되었습니다.", job_id=job_id)


@router.get("/ingest/status", response_model=IngestStatusResponse)
async def ingest_status() -> IngestStatusResponse:
    state = get_ingestion_state()
    try:
        total = get_collection_count()
    except Exception:
        total = 0

    from app.ingestion.scheduler import get_next_run_time
    return IngestStatusResponse(
        last_run=state.get("last_run"),
        next_run=get_next_run_time(),
        docs_ingested_last_run=state.get("docs_ingested_last_run", 0),
        total_docs_in_store=total,
        errors_last_run=state.get("errors_last_run", []),
        is_running=state.get("is_running", False),
    )
