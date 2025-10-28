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
    embedding_model: str = Field(default="text-embedding-3-large")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache
def get_settings() -> Settings:
    return Settings()
