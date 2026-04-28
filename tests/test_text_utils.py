import pytest
from app.utils.text_utils import (
    compute_subscription_status,
    make_doc_id,
    parse_date,
    extract_region_parts,
)


def test_parse_date_yyyymmdd():
    assert parse_date("20260420") == "2026-04-20"


def test_parse_date_iso():
    assert parse_date("2026-04-20") == "2026-04-20"


def test_parse_date_none():
    assert parse_date(None) is None
    assert parse_date("") is None
    assert parse_date("invalid") is None


def test_make_doc_id_stable():
    id1 = make_doc_id("판교 XX 아파트", "2026-04-20")
    id2 = make_doc_id("판교 XX 아파트", "2026-04-20")
    assert id1 == id2


def test_make_doc_id_normalizes_whitespace():
    id1 = make_doc_id("판교 XX 아파트", "2026-04-20")
    id2 = make_doc_id("판교XX아파트", "2026-04-20")
    assert id1 == id2


def test_compute_subscription_status_active():
    # 오늘(2026-04-28) 기준 active 구간
    status = compute_subscription_status("2026-04-27", "2026-04-30")
    assert status == "active"


def test_compute_subscription_status_upcoming():
    # 시작일이 미래
    status = compute_subscription_status("2099-01-01", "2099-01-10")
    assert status == "upcoming"


def test_compute_subscription_status_closed():
    # 종료일이 과거
    status = compute_subscription_status("2020-01-01", "2020-01-10")
    assert status == "closed"


def test_extract_region_parts():
    region, short, district = extract_region_parts("경기도 성남시 분당구 판교동")
    assert region == "경기도 성남시 분당구 판교동"
    assert short == "성남시"
    assert district == "분당구"


def test_extract_region_parts_empty():
    region, short, district = extract_region_parts(None)
    assert region == short == district == ""
