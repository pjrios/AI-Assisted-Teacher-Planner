from __future__ import annotations

from pathlib import Path

from docx import Document

from ..schemas import YearlyPlan
from .text_parser import parse_yearly_plan_from_lines


def parse_yearly_plan_docx(path: Path) -> YearlyPlan:
    document = Document(path)
    lines = (paragraph.text for paragraph in document.paragraphs)
    return parse_yearly_plan_from_lines(lines)
