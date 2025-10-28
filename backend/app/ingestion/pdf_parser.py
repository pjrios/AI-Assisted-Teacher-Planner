from __future__ import annotations

from pathlib import Path

from pypdf import PdfReader

from ..schemas import YearlyPlan
from .text_parser import parse_yearly_plan_from_lines


def parse_yearly_plan_pdf(path: Path) -> YearlyPlan:
    reader = PdfReader(str(path))
    lines: list[str] = []
    for page in reader.pages:
        text = page.extract_text()
        if text:
            lines.extend(text.splitlines())
    return parse_yearly_plan_from_lines(lines)
