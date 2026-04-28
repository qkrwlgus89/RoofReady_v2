from typing import Optional

from langchain_core.vectorstores import VectorStoreRetriever

from app.config import get_settings
from app.rag.vector_store import get_vector_store

# 지역 키워드 → ChromaDB region 필드 contains 필터에 사용
_REGION_KEYWORDS = [
    "서울", "부산", "대구", "인천", "광주", "대전", "울산", "세종",
    "경기", "강원", "충북", "충남", "전북", "전남", "경북", "경남", "제주",
    "강남", "강북", "강서", "강동", "송파", "마포", "용산", "종로", "성동",
    "노원", "도봉", "은평", "서대문", "동작", "관악", "구로", "금천", "영등포",
    "양천", "중랑", "광진", "성북", "강서", "중구", "동대문",
    "수원", "성남", "고양", "용인", "부천", "안산", "안양", "남양주",
    "화성", "평택", "의정부", "시흥", "파주", "김포", "광명", "광주",
    "군포", "하남", "오산", "이천", "안성", "의왕", "양평", "여주", "동두천",
    "판교", "분당", "일산", "위례", "미사", "다산", "마곡", "창릉",
]

_ACTIVE_KEYWORDS = {"현재", "지금", "진행중", "접수중", "청약중", "모집중"}


def extract_region_filter(query: str) -> Optional[str]:
    """쿼리에서 지역 키워드 감지. 가장 긴 매칭 우선."""
    matches = [kw for kw in _REGION_KEYWORDS if kw in query]
    if not matches:
        return None
    return max(matches, key=len)


def is_active_query(query: str) -> bool:
    """'현재 진행중' 류 쿼리 감지."""
    return any(kw in query for kw in _ACTIVE_KEYWORDS)


def get_retriever(
    query: str,
    region_hint: Optional[str] = None,
    subscription_type: Optional[str] = None,
    top_k: Optional[int] = None,
) -> VectorStoreRetriever:
    """
    메타데이터 필터 + MMR 기반 retriever 반환.

    Args:
        query: 사용자 질문 (지역·상태 자동 추출에 사용)
        region_hint: 명시적 지역 (없으면 query에서 자동 추출)
        subscription_type: 청약 유형 필터
        top_k: 반환 문서 수
    """
    settings = get_settings()
    k = top_k or settings.top_k_retrieval

    filters = _build_filters(query, region_hint, subscription_type)

    store = get_vector_store()
    kwargs = {
        "search_type": "mmr",
        "search_kwargs": {
            "k": k,
            "fetch_k": k * 3,
            "lambda_mult": 0.6,
        },
    }
    if filters:
        kwargs["search_kwargs"]["filter"] = filters

    return store.as_retriever(**kwargs)


def _build_filters(
    query: str,
    region_hint: Optional[str],
    subscription_type: Optional[str],
) -> Optional[dict]:
    conditions = []

    region = region_hint or extract_region_filter(query)
    if region:
        conditions.append({"region": {"$contains": region}})

    if is_active_query(query):
        conditions.append({"subscription_status": {"$eq": "active"}})

    if subscription_type:
        conditions.append({"subscription_type": {"$contains": subscription_type}})

    if not conditions:
        return None
    if len(conditions) == 1:
        return conditions[0]
    return {"$and": conditions}
