from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

from docx import Document

from ..schemas import YearlyPlan, YearlyPlanArea, YearlyPlanTrimester

SECTION_HEADERS = {
    "objectives": {"objective", "objectives", "learning objectives"},
    "contents": {"content", "contents"},
    "competences": {"competence", "competences"},
    "indicators": {"indicator", "indicators of achievement", "indicators"},
    "projects": {"project", "projects"},
    "methodology": {"methodology", "methodologies"},
    "assessment": {"assessment", "summative assessment", "assessments"},
}


def normalise_header(value: str) -> str | None:
    lower_value = value.strip().lower()
    for canonical, aliases in SECTION_HEADERS.items():
        if any(lower_value.startswith(alias) for alias in aliases):
            return canonical
    return None


def parse_trimester_header(text: str) -> dict[str, Any]:
    data: dict[str, Any] = {}
    lower = text.lower()
    if "trimester" in lower:
        data["name"] = text.strip().title()
    if "from" in lower and "to" in lower:
        parts = text.replace("–", "-").split(" ")
        try:
            from_index = next(i for i, part in enumerate(parts) if part.lower() == "from")
            to_index = next(i for i, part in enumerate(parts) if part.lower() == "to")
            start_str = parts[from_index + 1]
            end_str = parts[to_index + 1]
            data["start_date"] = _coerce_date(start_str)
            data["end_date"] = _coerce_date(end_str)
        except (StopIteration, ValueError):
            pass
    return data


def _coerce_date(value: str) -> datetime.date | None:
    value = value.strip().strip(",")
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue
    return None


def parse_yearly_plan_docx(path: Path) -> YearlyPlan:
    document = Document(path)
    year = 0
    grade = ""
    subject = ""
    trimesters: list[YearlyPlanTrimester] = []

    current_trimester: YearlyPlanTrimester | None = None
    current_area: YearlyPlanArea | None = None
    current_section: str | None = None

    for paragraph in document.paragraphs:
        text = paragraph.text.strip()
        if not text:
            continue
        if text.lower().startswith("year"):
            year = int("".join(filter(str.isdigit, text)))
            continue
        if text.lower().startswith("grade"):
            grade = text.split(":", 1)[-1].strip()
            continue
        if text.lower().startswith("subject"):
            subject = text.split(":", 1)[-1].strip()
            continue

        trimester_info = parse_trimester_header(text)
        if trimester_info:
            if current_trimester:
                trimesters.append(current_trimester)
            current_trimester = YearlyPlanTrimester(
                name=trimester_info.get("name", text.strip()),
                start_date=trimester_info.get("start_date"),
                end_date=trimester_info.get("end_date"),
                weeks=None,
                areas=[],
            )
            current_area = None
            current_section = None
            continue

        if text.lower().startswith("working weeks") and current_trimester:
            digits = "".join(filter(str.isdigit, text))
            if digits:
                current_trimester.weeks = int(digits)
            continue

        if text.isupper() and len(text.split()) <= 6:
            if current_trimester:
                if current_area:
                    current_trimester.areas.append(current_area)
                current_area = YearlyPlanArea(title=text.title())
                current_section = None
            continue

        section = normalise_header(text)
        if section:
            current_section = section
            continue

        if current_area and current_section:
            target_list = getattr(current_area, current_section)
            if isinstance(target_list, list):
                target_list.extend(_split_list(text))
            continue

    if current_area and current_trimester:
        current_trimester.areas.append(current_area)
    if current_trimester:
        trimesters.append(current_trimester)

    if not year:
        year = datetime.now().year

    return YearlyPlan(year=year, grade=grade or "", subject=subject or "", trimesters=trimesters)


def _split_list(text: str) -> list[str]:
    separators = [";", "•", "-", "\n"]
    normalized = text
    for separator in separators:
        normalized = normalized.replace(separator, "|")
    parts = [part.strip(" .") for part in normalized.split("|")]
    return [part for part in parts if part]
