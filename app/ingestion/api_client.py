import asyncio
from typing import Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.models.api_models import AptAnnouncementRaw
from app.utils.logger import get_logger

logger = get_logger(__name__)

# 한국부동산원 청약홈 분양정보 조회 서비스 (data.go.kr 데이터셋 ID: 15098547)
_BASE_URL = "https://api.odcloud.kr/api/ApplyhomeInfoDetailSvc/v1"
_OPERATION = "getAPTLttotPblancDetail"
_PER_PAGE = 100


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
async def _get_page(client: httpx.AsyncClient, page: int, extra_params: dict) -> dict:
    settings = get_settings()
    params = {
        "serviceKey": settings.data_go_kr_api_key,
        "page": page,
        "perPage": _PER_PAGE,
        **extra_params,
    }
    resp = await client.get(
        f"{_BASE_URL}/{_OPERATION}",
        params=params,
        headers={"accept": "*/*"},
        timeout=30.0,
    )
    resp.raise_for_status()
    return resp.json()


async def fetch_announcements(
    region_code: Optional[str] = None,
) -> list[AptAnnouncementRaw]:
    """
    청약홈 APT 분양공고 전체 수집 (페이지네이션).

    Args:
        region_code: SUBSCRPT_AREA_CODE 값 (None이면 전국)
    """
    extra: dict = {}
    if region_code:
        extra["cond[SUBSCRPT_AREA_CODE::EQ]"] = region_code

    announcements: list[AptAnnouncementRaw] = []

    async with httpx.AsyncClient() as client:
        first = await _get_page(client, 1, extra)
        total_count = int(first.get("totalCount", 0))

        if total_count == 0:
            logger.info("수집된 공고 없음", region_code=region_code)
            return []

        for item in first.get("data", []):
            _append_safe(announcements, item)

        total_pages = (total_count + _PER_PAGE - 1) // _PER_PAGE
        for page in range(2, total_pages + 1):
            await asyncio.sleep(0.3)
            try:
                page_data = await _get_page(client, page, extra)
                for item in page_data.get("data", []):
                    _append_safe(announcements, item)
            except Exception as exc:
                logger.error("페이지 수집 실패", page=page, error=str(exc))

    logger.info("공고 수집 완료", total=len(announcements), region_code=region_code)
    return announcements


def _append_safe(lst: list, item: dict) -> None:
    try:
        lst.append(AptAnnouncementRaw(**item))
    except Exception as exc:
        logger.warning("공고 파싱 실패", error=str(exc), item=str(item)[:100])
