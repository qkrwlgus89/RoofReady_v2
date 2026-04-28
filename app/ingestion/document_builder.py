from datetime import datetime, timezone
from typing import Optional

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.models.api_models import AptAnnouncementRaw
from app.utils.text_utils import (
    compute_subscription_status,
    extract_region_parts,
    make_doc_id,
)

_SPLITTER = RecursiveCharacterTextSplitter(
    chunk_size=800,
    chunk_overlap=150,
    separators=["\n\n", "\n", "。", ".", " ", ""],
)


def build_documents(
    announcement: AptAnnouncementRaw,
    pdf_pages: Optional[list[dict]] = None,
) -> tuple[list[Document], list[str]]:
    """
    API 공고 + PDF 페이지 → LangChain Document 리스트.

    Returns:
        (documents, ids)
    """
    # 날짜는 이미 YYYY-MM-DD 형식이므로 그대로 사용
    name = announcement.HOUSE_NM or announcement.BSNS_MBY_NM or "미상"
    sub_start = announcement.RCEPT_BGNDE
    sub_end = announcement.RCEPT_ENDDE
    winner_date = announcement.PRZWNER_PRESNATN_DE
    contract_start = announcement.CNTRCT_CNCLS_BGNDE
    contract_end = announcement.CNTRCT_CNCLS_ENDDE

    doc_id = make_doc_id(name, sub_start or "")
    region_full, region_short, district = extract_region_parts(announcement.HSSPLY_ADRES)
    status = compute_subscription_status(sub_start, sub_end)
    ingested_at = datetime.now(timezone.utc).isoformat()

    base_meta: dict = {
        "doc_id": doc_id,
        "announcement_id": doc_id,
        "announcement_name": name,
        "region": region_full,
        "region_short": region_short,
        "district": district,
        "subscription_start": sub_start or "",
        "subscription_end": sub_end or "",
        "winner_announcement": winner_date or "",
        "contract_start": contract_start or "",
        "contract_end": contract_end or "",
        "total_supply": announcement.TOT_SUPLY_HSHLDCO or 0,
        "subscription_type": announcement.HOUSE_DTL_SECD_NM or "미상",
        "housing_type": announcement.HOUSE_SECD_NM or "APT",
        "subscription_status": status,
        "source_url": announcement.PBLANC_URL or announcement.HMPG_ADRES or "",
        "pdf_url": "",
        "ingested_at": ingested_at,
    }

    documents: list[Document] = []
    ids: list[str] = []

    # 1. Structured Summary Document
    summary_text = _build_summary_text(name, announcement, region_full)
    summary_meta = {**base_meta, "doc_type": "structured_summary", "chunk_index": 0, "page_number": -1}
    documents.append(Document(page_content=summary_text, metadata=summary_meta))
    ids.append(f"struct_{doc_id}")

    # 2. PDF Chunk Documents
    if pdf_pages:
        for page_info in pdf_pages:
            page_num = page_info["page"]
            page_text = page_info["text"].strip()
            if not page_text:
                continue
            for chunk_idx, chunk in enumerate(_SPLITTER.split_text(page_text)):
                chunk_meta = {
                    **base_meta,
                    "doc_type": "pdf_chunk",
                    "chunk_index": chunk_idx,
                    "page_number": page_num,
                }
                documents.append(Document(page_content=chunk, metadata=chunk_meta))
                ids.append(f"pdf_{doc_id}_p{page_num}_c{chunk_idx}")

    return documents, ids


def _build_summary_text(
    name: str,
    ann: AptAnnouncementRaw,
    region: str,
) -> str:
    lines = [
        "[청약 공고 요약]",
        f"단지명: {name}",
        f"주택유형: {ann.HOUSE_SECD_NM or 'APT'} / {ann.HOUSE_DTL_SECD_NM or ''}",
        f"위치: {region}",
        f"모집공고일: {ann.RCRIT_PBLANC_DE or '미정'}",
        f"특별공급 접수: {ann.SPSPLY_RCEPT_BGNDE or '미정'} ~ {ann.SPSPLY_RCEPT_ENDDE or '미정'}",
        f"일반공급 접수: {ann.RCEPT_BGNDE or '미정'} ~ {ann.RCEPT_ENDDE or '미정'}",
        f"  1순위 해당지역: {ann.GNRL_RNK1_CRSPAREA_RCPTDE or '미정'}",
        f"  1순위 기타지역: {ann.GNRL_RNK1_ETC_AREA_RCPTDE or '미정'}",
        f"  2순위: {ann.GNRL_RNK2_CRSPAREA_RCPTDE or '미정'}",
        f"당첨자 발표: {ann.PRZWNER_PRESNATN_DE or '미정'}",
        f"계약: {ann.CNTRCT_CNCLS_BGNDE or '미정'} ~ {ann.CNTRCT_CNCLS_ENDDE or '미정'}",
        f"입주예정: {ann.MVN_PREARNGE_YM or '미정'}",
        f"총 공급세대수: {ann.TOT_SUPLY_HSHLDCO or '미상'}세대",
        f"분양/임대: {ann.RENT_SECD_NM or '미상'}",
        f"사업주체: {ann.BSNS_MBY_NM or '미상'}",
    ]
    if ann.PBLANC_URL:
        lines.append(f"공고 URL: {ann.PBLANC_URL}")
    if ann.HMPG_ADRES:
        lines.append(f"홈페이지: {ann.HMPG_ADRES}")
    if ann.MDHS_TELNO:
        lines.append(f"문의: {ann.MDHS_TELNO}")

    # 투기과열/조정대상 등 규제 정보
    flags = []
    if ann.SPECLT_RDN_EARTH_AT == "Y":
        flags.append("투기과열지구")
    if ann.MDAT_TRGET_AREA_SECD == "Y":
        flags.append("조정대상지역")
    if ann.PARCPRC_ULS_AT == "Y":
        flags.append("분양가상한제")
    if flags:
        lines.append(f"규제지역: {', '.join(flags)}")

    return "\n".join(lines)
