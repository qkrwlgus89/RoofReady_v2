import hashlib
from pathlib import Path
from typing import Optional

import httpx

from app.config import get_settings
from app.utils.logger import get_logger

logger = get_logger(__name__)


def _url_to_filename(url: str) -> str:
    """URL을 SHA256 해시 기반 파일명으로 변환."""
    return hashlib.sha256(url.encode()).hexdigest() + ".pdf"


async def download_pdf(url: str) -> Optional[Path]:
    """
    PDF URL을 로컬 캐시 경로에 다운로드.

    이미 캐시된 파일이 있으면 재사용.
    실패 시 None 반환 (호출자가 계속 진행할 수 있도록).
    """
    settings = get_settings()
    cache_dir = Path(settings.pdf_cache_path)
    cache_dir.mkdir(parents=True, exist_ok=True)

    dest = cache_dir / _url_to_filename(url)

    if dest.exists() and dest.stat().st_size > 0:
        logger.debug("PDF 캐시 사용", url=url, path=str(dest))
        return dest

    logger.info("PDF 다운로드 시작", url=url)
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=60.0) as client:
            async with client.stream("GET", url) as resp:
                resp.raise_for_status()

                content_type = resp.headers.get("content-type", "")
                if "pdf" not in content_type.lower() and not url.lower().endswith(".pdf"):
                    logger.warning(
                        "PDF가 아닌 콘텐츠 타입", url=url, content_type=content_type
                    )

                with open(dest, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=65536):
                        f.write(chunk)

        if dest.stat().st_size == 0:
            dest.unlink(missing_ok=True)
            logger.warning("빈 PDF 파일 수신", url=url)
            return None

        logger.info("PDF 다운로드 완료", url=url, size_bytes=dest.stat().st_size)
        return dest

    except Exception as exc:
        dest.unlink(missing_ok=True)
        logger.warning("PDF 다운로드 실패", url=url, error=str(exc))
        return None
