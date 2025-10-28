from functools import lru_cache
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    app_name: str = "AI Assisted Teacher Planner"
    openai_api_key: str | None = Field(default=None, env="OPENAI_API_KEY")
    database_url: str = Field(
        default="postgresql+psycopg://planner:planner@localhost:5432/planner",
        env="DATABASE_URL",
    )
    chroma_persist_directory: str = Field(default="./.chroma")
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    embedding_device: str | None = Field(default=None)
    embedding_batch_size: int = Field(default=32)
    embedding_normalize: bool = Field(default=True)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
