from typing import TypedDict


class DocumentMetadata(TypedDict, total=False):
    # Identity
    doc_id: str
    doc_type: str           # "structured_summary" | "pdf_chunk"
    chunk_index: int
    page_number: int

    # Announcement
    announcement_name: str
    announcement_id: str    # == doc_id, links chunks to parent

    # Location
    region: str             # 전체 주소 (e.g. "경기도 성남시 분당구")
    region_short: str       # 시군구 (e.g. "성남시")
    district: str           # 구/군 (e.g. "분당구")

    # Key dates (YYYY-MM-DD)
    subscription_start: str
    subscription_end: str
    winner_announcement: str
    contract_start: str
    contract_end: str

    # Supply info
    total_supply: int
    subscription_type: str   # "일반공급" | "특별공급" | "혼합"
    housing_type: str        # "아파트" | "오피스텔" 등

    # Status — computed at ingest time
    subscription_status: str  # "upcoming" | "active" | "closed" | "unknown"

    # Provenance
    source_url: str
    pdf_url: str
    ingested_at: str         # ISO 8601
