from typing import Optional
from pydantic import BaseModel, Field
import uuid


class ChatRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="사용자 질문")
    region: Optional[str] = Field(None, description="지역 필터 (자동 추출 시 생략 가능)")
    subscription_type: Optional[str] = Field(None, description="청약 유형 (일반공급/특별공급 등)")
    top_k: int = Field(8, ge=1, le=20, description="검색할 문서 수")


class SourceDocument(BaseModel):
    announcement_name: str
    region: str
    subscription_start: Optional[str] = None
    subscription_end: Optional[str] = None
    winner_announcement: Optional[str] = None
    subscription_status: Optional[str] = None
    source_url: Optional[str] = None
    doc_type: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceDocument]
    query_id: str = Field(default_factory=lambda: str(uuid.uuid4()))


class IngestTriggerResponse(BaseModel):
    message: str
    job_id: str


class IngestStatusResponse(BaseModel):
    last_run: Optional[str] = None
    next_run: Optional[str] = None
    docs_ingested_last_run: int = 0
    total_docs_in_store: int = 0
    errors_last_run: list[str] = []
    is_running: bool = False


class HealthResponse(BaseModel):
    status: str
    chroma_document_count: int
    last_ingestion: Optional[str] = None
    scheduler_running: bool
