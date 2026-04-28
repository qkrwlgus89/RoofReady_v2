import pytest
from app.rag.retriever import extract_region_filter, is_active_query


def test_extract_region_판교():
    assert extract_region_filter("판교 청약 있어?") == "판교"


def test_extract_region_longer_wins():
    # "남양주"(3자)가 "성남"(2자)보다 길어서 우선
    assert extract_region_filter("성남 남양주 청약 알려줘") == "남양주"


def test_extract_region_none():
    assert extract_region_filter("청약 정보 알려줘") is None


def test_is_active_query_현재():
    assert is_active_query("현재 청약 중인 곳 있어?") is True


def test_is_active_query_접수중():
    assert is_active_query("접수중인 아파트 알려줘") is True


def test_is_not_active_query():
    assert is_active_query("판교 청약 일정 알려줘") is False
