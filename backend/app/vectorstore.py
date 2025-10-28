from __future__ import annotations

from pathlib import Path
from typing import Iterable

import chromadb
from chromadb.config import Settings as ChromaSettings

from .config import get_settings

settings = get_settings()


class VectorStore:
    def __init__(self, collection_name: str = "yearly-plan") -> None:
        persist_path = Path(settings.chroma_persist_directory).expanduser()
        persist_path.mkdir(parents=True, exist_ok=True)

        self.client = chromadb.Client(
            ChromaSettings(persist_directory=str(persist_path))
        )
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_texts(
        self,
        *,
        ids: list[str],
        texts: list[str],
        embeddings: list[list[float]],
        metadatas: list[dict[str, str]],
    ) -> None:
        self.collection.add(ids=ids, documents=texts, embeddings=embeddings, metadatas=metadatas)

    def similarity_search(
        self, query: str, *, n_results: int = 5
    ) -> list[dict[str, str]]:
        results = self.collection.query(query_texts=[query], n_results=n_results)
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        return [
            {
                "text": doc,
                "metadata": metadata,
            }
            for doc, metadata in zip(documents, metadatas, strict=False)
        ]
