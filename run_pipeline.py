"""Utility script to bootstrap the environment and ingest yearly plans."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from getpass import getpass
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
VENV_DIR = PROJECT_ROOT / ".venv"
REQUIREMENTS_PATH = PROJECT_ROOT / "requirements.txt"
REQUIREMENTS_MARKER = VENV_DIR / ".requirements_installed"


def _venv_python_executable() -> Path:
    if os.name == "nt":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def _requirements_are_current() -> bool:
    if not REQUIREMENTS_MARKER.exists() or not REQUIREMENTS_PATH.exists():
        return False

    try:
        recorded_mtime = float(REQUIREMENTS_MARKER.read_text().strip())
    except ValueError:
        return False

    return recorded_mtime >= REQUIREMENTS_PATH.stat().st_mtime


def _install_requirements(python_executable: Path) -> None:
    print("📦 Installing project dependencies...", flush=True)
    subprocess.run(
        [str(python_executable), "-m", "pip", "install", "--upgrade", "pip"],
        cwd=PROJECT_ROOT,
        check=True,
    )
    subprocess.run(
        [str(python_executable), "-m", "pip", "install", "-r", str(REQUIREMENTS_PATH)],
        cwd=PROJECT_ROOT,
        check=True,
    )
    REQUIREMENTS_MARKER.write_text(str(REQUIREMENTS_PATH.stat().st_mtime))


def _ensure_virtualenv() -> None:
    if os.environ.get("RUN_PIPELINE_ACTIVE_VENV") == "1":
        return

    if not VENV_DIR.exists():
        print("🛠️ Creating project virtual environment...", flush=True)
        subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], cwd=PROJECT_ROOT, check=True)

    python_executable = _venv_python_executable()

    if not python_executable.exists():
        raise RuntimeError("Virtual environment appears corrupted; missing Python executable.")

    if not _requirements_are_current():
        _install_requirements(python_executable)

    env = os.environ.copy()
    env["RUN_PIPELINE_ACTIVE_VENV"] = "1"

    result = subprocess.run(
        [str(python_executable), str(Path(__file__).resolve()), *sys.argv[1:]],
        cwd=PROJECT_ROOT,
        env=env,
    )
    raise SystemExit(result.returncode)


_ensure_virtualenv()

from backend.app.config import get_settings
from backend.app.db import init_database
from backend.app.ingestion.embedder import EmbeddingService
from backend.app.ingestion.parser import ingest_yearly_plan
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


def _write_env_setting(key: str, value: str) -> None:
    env_path = PROJECT_ROOT / ".env"
    if env_path.exists():
        lines = env_path.read_text(encoding="utf-8").splitlines()
    else:
        lines = []

    filtered = [line for line in lines if not line.startswith(f"{key}=")]
    filtered.append(f"{key}={value}")
    env_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")


def _ensure_openai_api_key() -> None:
    settings = get_settings()
    if settings.openai_api_key:
        return

    print("🔐 An OpenAI API key is required to embed and generate lessons.")
    try:
        api_key = getpass("Enter your OPENAI_API_KEY: ").strip()
    except (EOFError, KeyboardInterrupt) as exc:  # pragma: no cover - interactive
        raise RuntimeError("OPENAI_API_KEY is required to continue.") from exc

    if not api_key:
        raise RuntimeError("OPENAI_API_KEY cannot be empty.")

    os.environ["OPENAI_API_KEY"] = api_key
    _write_env_setting("OPENAI_API_KEY", api_key)
    get_settings.cache_clear()
    refreshed = get_settings()
    if not refreshed.openai_api_key:
        raise RuntimeError("Failed to persist OPENAI_API_KEY to the environment.")


def _bootstrap_environment() -> None:
    _ensure_openai_api_key()

    print("⚙️ Ensuring database schema exists...", flush=True)
    init_database()
    print("✅ Database ready.")


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

    _bootstrap_environment()

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
