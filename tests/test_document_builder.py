import pytest
from app.ingestion.document_builder import build_documents
from app.models.api_models import AptAnnouncementRaw


def _make_announcement(**kwargs) -> AptAnnouncementRaw:
    defaults = {
        "pblancNm": "판교 테스트 아파트",
        "bsnsMbyNm": "테스트건설",
        "hssplyAdres": "경기도 성남시 분당구 판교동",
        "totSuplyHshldco": "500",
        "rcptBgnde": "20260420",
        "rcptEndde": "20260425",
        "przwnerPresnatnDe": "20260502",
        "cntrctCnclsBgnde": "20260510",
        "cntrctCnclsEndde": "20260515",
        "hmpgAdres": "https://example.com",
        "houseSecdNm": "아파트",
    }
    defaults.update(kwargs)
    return AptAnnouncementRaw(**defaults)


def test_build_documents_creates_structured_summary():
    ann = _make_announcement()
    docs, ids = build_documents(ann)
    assert any(d.metadata["doc_type"] == "structured_summary" for d in docs)
    assert any(ids[i].startswith("struct_") for i in range(len(ids)))


def test_build_documents_with_pdf_pages():
    ann = _make_announcement()
    pdf_pages = [{"page": 1, "text": "특별공급 자격 조건: 무주택 세대구성원"}]
    docs, ids = build_documents(ann, pdf_pages)
    assert any(d.metadata["doc_type"] == "pdf_chunk" for d in docs)
    assert any("pdf_" in id_ for id_ in ids)


def test_build_documents_metadata_fields():
    ann = _make_announcement()
    docs, ids = build_documents(ann)
    summary = next(d for d in docs if d.metadata["doc_type"] == "structured_summary")
    assert summary.metadata["announcement_name"] == "판교 테스트 아파트"
    assert summary.metadata["region"] == "경기도 성남시 분당구 판교동"
    assert summary.metadata["subscription_start"] == "2026-04-20"
    assert summary.metadata["total_supply"] == 500


def test_build_documents_ids_are_stable():
    ann = _make_announcement()
    _, ids1 = build_documents(ann)
    _, ids2 = build_documents(ann)
    assert ids1 == ids2


def test_build_documents_empty_pdf_pages():
    ann = _make_announcement()
    docs, ids = build_documents(ann, pdf_pages=[])
    # 빈 PDF 페이지 → structured_summary만 생성
    assert len(docs) == 1
    assert docs[0].metadata["doc_type"] == "structured_summary"
