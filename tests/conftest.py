import pytest
import os

# 테스트 시 실제 API 키 없이 실행 가능하도록 더미 환경변수 설정
os.environ.setdefault("OPENAI_API_KEY", "sk-test-dummy")
os.environ.setdefault("DATA_GO_KR_API_KEY", "test-dummy-key")
