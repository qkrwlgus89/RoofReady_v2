from pathlib import Path
from typing import Optional
from functools import lru_cache

from langchain_chroma import Chroma
from langchain_core.documents import Document

from app.config import get_settings
from app.rag.embeddings import get_embeddings
from app.utils.logger import get_logger

logger = get_logger(__name__)

COLLECTION_NAME = "cheongak_announcements"


@lru_cache(maxsize=1)
def get_vector_store() -> Chroma:
    settings = get_settings()
    persist_dir = str(Path(settings.chroma_db_path).resolve())
    Path(persist_dir).mkdir(parents=True, exist_ok=True)

    store = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=get_embeddings(),
        persist_directory=persist_dir,
    )
    logger.info("ChromaDB 초기화 완료", path=persist_dir)
    return store


def upsert_documents(documents: list[Document], ids: list[str]) -> None:
    """문서를 ChromaDB에 upsert (중복 ID는 덮어씀)."""
    if not documents:
        return

    store = get_vector_store()
    # langchain-chroma는 add_documents에 ids를 전달하면 upsert 처리
    store.add_documents(documents=documents, ids=ids)
    logger.info("문서 upsert 완료", count=len(documents))


def document_exists(doc_id: str) -> bool:
    """structured_summary 문서가 이미 존재하는지 확인."""
    store = get_vector_store()
    result = store.get(ids=[f"struct_{doc_id}"], include=[])
    return len(result["ids"]) > 0


def get_collection_count() -> int:
    """컬렉션 내 총 문서 수 반환."""
    store = get_vector_store()
    return store._collection.count()
