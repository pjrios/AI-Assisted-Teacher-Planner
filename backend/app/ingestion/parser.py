from __future__ import annotations

from pathlib import Path

from ..schemas import YearlyPlan, YearlyPlanIngestionResult
from .chunker import chunk_yearly_plan
from .docx_parser import parse_yearly_plan_docx


SUPPORTED_EXTENSIONS = {".docx"}


def ingest_yearly_plan(path: Path) -> YearlyPlanIngestionResult:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {extension}")

    structured: YearlyPlan
    if extension == ".docx":
        structured = parse_yearly_plan_docx(path)
    else:
        raise ValueError(f"Unsupported file extension: {extension}")

    chunks = list(chunk_yearly_plan(structured))
    return YearlyPlanIngestionResult(structured=structured, chunks=chunks)
