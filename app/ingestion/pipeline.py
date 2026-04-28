import re
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.ingestion.api_client import fetch_announcements
from app.ingestion.document_builder import build_documents
from app.ingestion.pdf_downloader import download_pdf
from app.ingestion.pdf_extractor import extract_text
from app.rag.vector_store import document_exists, upsert_documents
from app.utils.logger import get_logger
from app.utils.text_utils import make_doc_id

logger = get_logger(__name__)

_state: dict = {
    "last_run": None,
    "docs_ingested_last_run": 0,
    "errors_last_run": [],
    "is_running": False,
}


def get_ingestion_state() -> dict:
    return dict(_state)


async def extract_pdf_url_from_pblanc(pblanc_url: str) -> Optional[str]:
    """
    청약홈 공고 상세 페이지(PBLANC_URL)에서 입주자모집공고 PDF 링크를 추출.
    PDF URL이 없으면 None 반환.
    """
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=15.0) as client:
            resp = await client.get(pblanc_url, headers={"User-Agent": "Mozilla/5.0"})
            html = resp.text

        # 청약홈 상세 페이지에서 PDF 링크 패턴 탐색
        # 예: href="...모집공고....pdf" 또는 fileDown 함수 인자
        patterns = [
            r'href=["\']([^"\']*\.pdf[^"\']*)["\']',
            r'fileDown\(["\']([^"\']+)["\']',
            r'downloadFile\(["\']([^"\']+)["\']',
            r'(https?://[^\s"\'<>]+\.pdf)',
        ]
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                url = match.group(1)
                if not url.startswith("http"):
                    url = "https://www.applyhome.co.kr" + url
                logger.info("PDF URL 추출 성공", pdf_url=url)
                return url

        logger.debug("PDF URL 없음", pblanc_url=pblanc_url)
        return None
    except Exception as exc:
        logger.warning("PBLANC 페이지 접근 실패", url=pblanc_url, error=str(exc))
        return None


async def run_ingestion(region_codes: Optional[list[str]] = None) -> dict:
    """
    전체 수집 파이프라인.

    1. API에서 공고 목록 수집
    2. 신규 공고만 필터 (중복 체크)
    3. PBLANC_URL → PDF URL 추출 → 다운로드 → 텍스트 추출
    4. ChromaDB upsert
    """
    if _state["is_running"]:
        logger.warning("이미 수집 중")
        return _state

    _state["is_running"] = True
    _state["errors_last_run"] = []
    _state["docs_ingested_last_run"] = 0

    try:
        targets = region_codes or [None]  # None = 전국
        total_new = 0

        for region_code in targets:
            try:
                announcements = await fetch_announcements(region_code=region_code)
            except Exception as exc:
                msg = f"API 수집 실패 (region={region_code}): {exc}"
                logger.error(msg)
                _state["errors_last_run"].append(msg)
                continue

            for ann in announcements:
                try:
                    name = ann.HOUSE_NM or ann.BSNS_MBY_NM or ""
                    doc_id = make_doc_id(name, ann.RCEPT_BGNDE or "")

                    if document_exists(doc_id):
                        logger.debug("SKIP (이미 존재)", name=name)
                        continue

                    # PBLANC_URL → PDF 추출 시도
                    pdf_pages = None
                    if ann.PBLANC_URL:
                        pdf_url = await extract_pdf_url_from_pblanc(ann.PBLANC_URL)
                        if pdf_url:
                            local_path = await download_pdf(pdf_url)
                            if local_path:
                                pdf_pages = extract_text(local_path)

                    docs, ids = build_documents(ann, pdf_pages)
                    upsert_documents(docs, ids)
                    total_new += len(docs)
                    logger.info("공고 저장", name=name, docs=len(docs))

                except Exception as exc:
                    msg = f"공고 처리 실패 ({ann.HOUSE_NM}): {exc}"
                    logger.error(msg)
                    _state["errors_last_run"].append(msg)

        _state["docs_ingested_last_run"] = total_new

    finally:
        _state["is_running"] = False
        _state["last_run"] = datetime.now(timezone.utc).isoformat()

    logger.info("수집 완료", new_docs=total_new)
    return dict(_state)
