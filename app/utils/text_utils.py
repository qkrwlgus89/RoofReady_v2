import hashlib
import re
import unicodedata
from datetime import date
from typing import Optional


def make_doc_id(announcement_name: str, subscription_start: str) -> str:
    """사업명 + 청약접수시작일로 안정적인 doc_id 생성."""
    normalized = _normalize_name(announcement_name) + subscription_start
    return hashlib.sha256(normalized.encode()).hexdigest()[:32]


def _normalize_name(name: str) -> str:
    """사업명 정규화: 전각문자 → 반각, 공백 제거."""
    name = unicodedata.normalize("NFKC", name)
    return re.sub(r"\s+", "", name).strip()


def compute_subscription_status(
    start: Optional[str],
    end: Optional[str],
) -> str:
    """청약 접수 기간 기반으로 상태 계산."""
    if not start or not end:
        return "unknown"
    try:
        today = date.today()
        s = date.fromisoformat(start)
        e = date.fromisoformat(end)
        if today < s:
            return "upcoming"
        elif s <= today <= e:
            return "active"
        else:
            return "closed"
    except ValueError:
        return "unknown"


def parse_date(raw: Optional[str]) -> Optional[str]:
    """
    공공데이터포털 날짜 형식(YYYYMMDD 또는 YYYY-MM-DD)을 ISO 형식으로 변환.
    파싱 실패 시 None 반환.
    """
    if not raw:
        return None
    raw = raw.strip()
    if re.fullmatch(r"\d{8}", raw):
        return f"{raw[:4]}-{raw[4:6]}-{raw[6:]}"
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
        return raw
    return None


def extract_region_parts(full_address: Optional[str]) -> tuple[str, str, str]:
    """
    전체 주소에서 (region, region_short, district) 추출.
    예: "경기도 성남시 분당구 판교동" → ("경기도 성남시 분당구 판교동", "성남시", "분당구")
    """
    if not full_address:
        return ("", "", "")
    parts = full_address.split()
    region_short = parts[1] if len(parts) > 1 else ""
    district = parts[2] if len(parts) > 2 else ""
    return (full_address, region_short, district)
