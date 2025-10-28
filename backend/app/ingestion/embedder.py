from __future__ import annotations

from typing import Iterable

from sentence_transformers import SentenceTransformer

from ..config import get_settings

settings = get_settings()


class EmbeddingService:
    def __init__(
        self,
        *,
        model: str | None = None,
        device: str | None = None,
        batch_size: int | None = None,
        normalize_embeddings: bool | None = None,
    ) -> None:
        self.model_name = model or settings.embedding_model
        self.device = device or settings.embedding_device
        self.batch_size = batch_size or settings.embedding_batch_size
        self.normalize_embeddings = (
            normalize_embeddings
            if normalize_embeddings is not None
            else settings.embedding_normalize
        )
        self._model = SentenceTransformer(self.model_name, device=self.device)

    def embed_texts(self, texts: Iterable[str]) -> list[list[float]]:
        text_list = list(texts)
        if not text_list:
            return []
        embeddings = self._model.encode(
            text_list,
            batch_size=self.batch_size,
            show_progress_bar=False,
            convert_to_numpy=True,
            normalize_embeddings=self.normalize_embeddings,
        )
        return embeddings.tolist()
