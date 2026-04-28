from functools import lru_cache
from typing import Optional

from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI

from app.config import get_settings
from app.rag.retriever import get_retriever
from app.utils.logger import get_logger

logger = get_logger(__name__)

_SYSTEM_PROMPT = """당신은 한국 아파트 청약 정보를 안내하는 전문 상담사입니다.
주어진 컨텍스트를 기반으로 정확하고 친절하게 답변해주세요.

규칙:
1. 반드시 한국어로 답변하세요.
2. 제공된 컨텍스트에 없는 정보는 "해당 정보를 찾을 수 없습니다"라고 답하세요.
3. 날짜는 "YYYY년 MM월 DD일" 형식으로 표시하세요.
4. 답변 시 출처(단지명)를 명시하세요.
5. 청약 조건, 자격, 일정은 반드시 원문 그대로 전달하세요.

컨텍스트:
{context}"""

_HUMAN_PROMPT = "{question}"


@lru_cache(maxsize=1)
def _get_llm() -> ChatOpenAI:
    settings = get_settings()
    return ChatOpenAI(
        model=settings.llm_model,
        openai_api_key=settings.openai_api_key,
        temperature=0,
    )


def _format_docs(docs: list[Document]) -> str:
    parts = []
    for i, doc in enumerate(docs, 1):
        name = doc.metadata.get("announcement_name", "미상")
        region = doc.metadata.get("region", "")
        doc_type = doc.metadata.get("doc_type", "")
        header = f"[출처 {i}: {name} / {region} / {doc_type}]"
        parts.append(f"{header}\n{doc.page_content}")
    return "\n\n---\n\n".join(parts)


async def run_rag_chain(
    query: str,
    region_hint: Optional[str] = None,
    subscription_type: Optional[str] = None,
    top_k: int = 8,
) -> tuple[str, list[Document]]:
    """
    RAG 체인 실행.

    Returns:
        (answer_text, source_documents)
    """
    retriever = get_retriever(
        query=query,
        region_hint=region_hint,
        subscription_type=subscription_type,
        top_k=top_k,
    )

    retrieved_docs = await retriever.ainvoke(query)
    logger.info("검색 완료", query=query, docs_found=len(retrieved_docs))

    if not retrieved_docs:
        return "해당 정보를 찾을 수 없습니다. 청약 관련 데이터가 아직 수집되지 않았을 수 있습니다.", []

    context = _format_docs(retrieved_docs)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _SYSTEM_PROMPT),
        ("human", _HUMAN_PROMPT),
    ])

    chain = prompt | _get_llm() | StrOutputParser()
    answer = await chain.ainvoke({"context": context, "question": query})

    return answer, retrieved_docs
