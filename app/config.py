from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openai_api_key: str
    data_go_kr_api_key: str

    chroma_db_path: str = "./data/chroma_db"
    pdf_cache_path: str = "./data/pdfs"

    scheduler_interval_hours: int = 6

    embedding_model: str = "text-embedding-3-small"
    llm_model: str = "gpt-4o"
    top_k_retrieval: int = 8

    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")


@lru_cache
def get_settings() -> Settings:
    return Settings()
