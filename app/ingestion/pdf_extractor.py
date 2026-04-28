from pathlib import Path
from typing import Optional

from app.utils.logger import get_logger

logger = get_logger(__name__)

_MIN_PAGE_TEXT_LENGTH = 50


def _extract_with_pymupdf(path: Path) -> list[dict]:
    """PyMuPDF(fitz)로 PDF 텍스트 추출. 다단 컬럼을 y→x 정렬로 처리."""
    import fitz  # PyMuPDF

    pages = []
    try:
        doc = fitz.open(str(path))
    except Exception as exc:
        logger.error("PyMuPDF 파일 열기 실패", path=str(path), error=str(exc))
        return []

    for page_num in range(len(doc)):
        try:
            page = doc[page_num]
            blocks = page.get_text("blocks")
            # 블록을 위→아래, 좌→우 순서로 정렬 (다단 컬럼 대응)
            sorted_blocks = sorted(blocks, key=lambda b: (round(b[1] / 10), b[0]))
            text = "\n".join(b[4].strip() for b in sorted_blocks if b[4].strip())

            if len(text) < _MIN_PAGE_TEXT_LENGTH:
                logger.debug(
                    "페이지 텍스트 부족 (스캔 이미지 가능성)",
                    path=str(path),
                    page=page_num + 1,
                    length=len(text),
                )

            pages.append({"page": page_num + 1, "text": text})
        except Exception as exc:
            logger.warning("페이지 추출 실패", page=page_num + 1, error=str(exc))
            pages.append({"page": page_num + 1, "text": ""})

    doc.close()
    return pages


def _extract_with_pdfplumber(path: Path) -> list[dict]:
    """pdfplumber로 PDF 텍스트 추출 (fallback)."""
    import pdfplumber

    pages = []
    try:
        with pdfplumber.open(str(path)) as pdf:
            for page_num, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text() or ""
                    pages.append({"page": page_num + 1, "text": text.strip()})
                except Exception as exc:
                    logger.warning("pdfplumber 페이지 추출 실패", page=page_num + 1, error=str(exc))
                    pages.append({"page": page_num + 1, "text": ""})
    except Exception as exc:
        logger.error("pdfplumber 파일 열기 실패", path=str(path), error=str(exc))

    return pages


def extract_text(path: Path) -> list[dict]:
    """
    PDF에서 텍스트를 페이지 단위로 추출.

    PyMuPDF를 먼저 시도하고, 추출 결과가 빈 경우 pdfplumber로 fallback.

    Returns:
        [{"page": int, "text": str}, ...]
    """
    if not path.exists():
        logger.error("PDF 파일 없음", path=str(path))
        return []

    pages = _extract_with_pymupdf(path)
    total_text = sum(len(p["text"]) for p in pages)

    if total_text < _MIN_PAGE_TEXT_LENGTH * max(len(pages), 1):
        logger.info("PyMuPDF 추출 부족, pdfplumber로 재시도", path=str(path))
        fallback = _extract_with_pdfplumber(path)
        if sum(len(p["text"]) for p in fallback) > total_text:
            return fallback

    return pages
