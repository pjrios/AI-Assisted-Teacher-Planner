from __future__ import annotations

from pathlib import Path

from ..schemas import YearlyPlan, YearlyPlanIngestionResult
from .chunker import chunk_yearly_plan
from .docx_parser import parse_yearly_plan_docx
from .pdf_parser import parse_yearly_plan_pdf
from .pptx_parser import parse_yearly_plan_pptx
from .text_parser import parse_yearly_plan_from_lines


SUPPORTED_EXTENSIONS = {".docx", ".pdf", ".pptx", ".txt", ".md"}


def ingest_yearly_plan(path: Path) -> YearlyPlanIngestionResult:
    extension = path.suffix.lower()
    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension: {extension}")

    structured: YearlyPlan
    if extension == ".docx":
        structured = parse_yearly_plan_docx(path)
    elif extension == ".pdf":
        structured = parse_yearly_plan_pdf(path)
    elif extension == ".pptx":
        structured = parse_yearly_plan_pptx(path)
    elif extension in {".txt", ".md"}:
        lines = path.read_text(encoding="utf-8").splitlines()
        structured = parse_yearly_plan_from_lines(lines)
    else:
        raise ValueError(f"Unsupported file extension: {extension}")

    chunks = list(chunk_yearly_plan(structured))
    return YearlyPlanIngestionResult(structured=structured, chunks=chunks)
