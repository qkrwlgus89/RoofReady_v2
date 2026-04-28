from fastapi import APIRouter, HTTPException
from app.models.request_models import ChatRequest, ChatResponse, SourceDocument
from app.rag.chain import run_rag_chain
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        answer, source_docs = await run_rag_chain(
            query=request.query,
            region_hint=request.region,
            subscription_type=request.subscription_type,
            top_k=request.top_k,
        )
    except Exception as exc:
        logger.error("RAG 체인 오류", error=str(exc))
        raise HTTPException(status_code=503, detail="챗봇 서비스 일시 오류입니다.")

    sources = []
    seen_ids = set()
    for doc in source_docs:
        meta = doc.metadata
        ann_id = meta.get("announcement_id", "")
        if ann_id in seen_ids:
            continue
        seen_ids.add(ann_id)
        sources.append(
            SourceDocument(
                announcement_name=meta.get("announcement_name", "미상"),
                region=meta.get("region", ""),
                subscription_start=meta.get("subscription_start") or None,
                subscription_end=meta.get("subscription_end") or None,
                winner_announcement=meta.get("winner_announcement") or None,
                subscription_status=meta.get("subscription_status") or None,
                source_url=meta.get("source_url") or None,
                doc_type=meta.get("doc_type", ""),
            )
        )

    return ChatResponse(answer=answer, sources=sources)
