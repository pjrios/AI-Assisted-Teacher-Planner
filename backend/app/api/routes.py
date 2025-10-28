from __future__ import annotations

from pathlib import Path
from tempfile import NamedTemporaryFile

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from .. import schemas
from ..db import Base, engine, get_db
from ..ingestion.embedder import EmbeddingService
from ..ingestion.parser import ingest_yearly_plan
from ..vectorstore import VectorStore

router = APIRouter()


@router.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@router.post("/plans/ingest", response_model=schemas.YearlyPlan)
def ingest_plan(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
) -> schemas.YearlyPlan:
    with NamedTemporaryFile(delete=False, suffix=Path(file.filename or "plan.docx").suffix) as tmp:
        content = file.file.read()
        tmp.write(content)
        tmp_path = Path(tmp.name)
    try:
        result = ingest_yearly_plan(tmp_path)
        _ = db  # Placeholder for persistence integration
    except ValueError as exc:  # pragma: no cover - validation path
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    finally:
        tmp_path.unlink(missing_ok=True)

    embeddings_service = EmbeddingService()
    embeddings = embeddings_service.embed_texts(chunk["text"] for chunk in result.chunks)
    vector_store = VectorStore()
    vector_store.add_texts(
        ids=[chunk["id"] for chunk in result.chunks],
        texts=[chunk["text"] for chunk in result.chunks],
        embeddings=embeddings,
        metadatas=[chunk["metadata"] for chunk in result.chunks],
    )
    return result.structured


@router.post("/plans/{plan_id}/topics/{topic_id}/generate")
def generate_lessons(
    plan_id: int,
    topic_id: int,
    request: schemas.LessonGenerationRequest,
) -> dict[str, list[dict[str, str]]]:
    vector_store = VectorStore()
    from ..services.planner import LessonPlanner

    planner = LessonPlanner(vector_store=vector_store)
    schedule = [
        (slot.date, slot.start_time, slot.end_time) for slot in request.schedule
    ]
    sessions = planner.plan_topic(
        query=request.metadata.get("topic", ""),
        schedule=schedule,
        metadata=request.metadata,
    )
    return {"sessions": sessions}
