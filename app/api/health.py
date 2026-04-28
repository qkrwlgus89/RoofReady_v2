from fastapi import APIRouter
from app.ingestion.pipeline import get_ingestion_state
from app.models.request_models import HealthResponse
from app.rag.vector_store import get_collection_count

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    state = get_ingestion_state()
    try:
        count = get_collection_count()
    except Exception:
        count = -1

    from app.ingestion.scheduler import is_scheduler_running
    return HealthResponse(
        status="ok",
        chroma_document_count=count,
        last_ingestion=state.get("last_run"),
        scheduler_running=is_scheduler_running(),
    )
