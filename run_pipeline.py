"""Utility script to ingest a yearly plan and push it to the vector store."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from backend.app.ingestion.parser import ingest_yearly_plan
from backend.app.ingestion.embedder import EmbeddingService
from backend.app.vectorstore import VectorStore


def _persist_vector_chunks(
    *,
    store: VectorStore,
    chunks: list[dict[str, Any]],
    embedding_model: str | None = None,
) -> int:
    if not chunks:
        return 0

    texts = [chunk["text"] for chunk in chunks]
    ids = [chunk["id"] for chunk in chunks]
    metadatas = [chunk["metadata"] for chunk in chunks]

    embedder = EmbeddingService(model=embedding_model)
    embeddings = embedder.embed_texts(texts)
    store.add_texts(ids=ids, texts=texts, embeddings=embeddings, metadatas=metadatas)
    return len(chunks)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Parse a yearly plan document, emit its structured JSON, and persist semantic "
            "chunks to the configured Chroma vector store."
        )
    )
    parser.add_argument(
        "plan_path",
        type=Path,
        help="Path to the yearly plan document (.docx) that should be ingested.",
    )
    parser.add_argument(
        "--output-json",
        type=Path,
        default=None,
        help=(
            "Optional path to write the normalized yearly plan JSON. If omitted, the "
            "JSON is printed to stdout."
        ),
    )
    parser.add_argument(
        "--collection",
        default="yearly-plan",
        help="Chroma collection name to store the embeddings in (default: yearly-plan).",
    )
    parser.add_argument(
        "--embedding-model",
        default=None,
        help="Override the embedding model name configured in the environment.",
    )
    args = parser.parse_args()

    plan_path: Path = args.plan_path.expanduser().resolve()
    if not plan_path.exists():
        raise FileNotFoundError(f"Plan file not found: {plan_path}")

    print(f"➡️ Ingesting yearly plan from {plan_path}...", flush=True)
    ingestion_result = ingest_yearly_plan(plan_path)
    structured = ingestion_result.structured.model_dump()

    if args.output_json:
        output_path = args.output_json.expanduser().resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(structured, indent=2, default=str), encoding="utf-8")
        print(f"✅ Structured plan written to {output_path}")
    else:
        print(json.dumps(structured, indent=2, default=str))

    store = VectorStore(collection_name=args.collection)
    chunk_count = _persist_vector_chunks(
        store=store,
        chunks=ingestion_result.chunks,
        embedding_model=args.embedding_model,
    )
    print(f"✅ Stored {chunk_count} chunks in Chroma collection '{args.collection}'.")


if __name__ == "__main__":
    main()
