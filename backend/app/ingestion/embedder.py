from __future__ import annotations

from typing import Iterable

from openai import OpenAI

from ..config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(self, *, model: str | None = None) -> None:
        self.model = model or settings.embedding_model
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY must be configured for embedding generation")
        self.client = OpenAI(api_key=settings.openai_api_key)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        text_list = list(texts)
        if not text_list:
            return []
        response = self.client.embeddings.create(model=self.model, input=text_list)
        return [item.embedding for item in response.data]
