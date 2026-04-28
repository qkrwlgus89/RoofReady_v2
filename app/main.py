import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.config import get_settings
from app.ingestion.pipeline import run_ingestion
from app.ingestion.scheduler import start_scheduler, stop_scheduler
from app.rag.vector_store import get_vector_store
from app.utils.logger import configure_logging, get_logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    logger = get_logger(__name__)

    # ChromaDB 초기화
    get_vector_store()
    logger.info("ChromaDB 준비 완료")

    # 스케줄러 시작
    start_scheduler()

    # 기동 시 1회 즉시 수집 (백그라운드)
    asyncio.create_task(run_ingestion())
    logger.info("초기 수집 태스크 등록")

    yield

    stop_scheduler()
    logger.info("서버 종료")


def create_app() -> FastAPI:
    app = FastAPI(
        title="RoofReady - 청약 RAG 챗봇 API",
        description="공공데이터포털 청약 정보 기반 RAG 챗봇 백엔드",
        version="0.1.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)
    return app


app = create_app()
