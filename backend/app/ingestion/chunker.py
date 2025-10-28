from __future__ import annotations

from itertools import count
from typing import Iterable

from ..schemas import YearlyPlan


def chunk_yearly_plan(plan: YearlyPlan) -> Iterable[dict[str, str]]:
    counter = count(1)
    for trimester_index, trimester in enumerate(plan.trimesters, start=1):
        for area in trimester.areas:
            base_metadata = {
                "grade": plan.grade,
                "subject": plan.subject,
                "trimester": str(trimester_index),
                "trimester_name": trimester.name,
                "area_title": area.title,
            }
            for key, values in _iter_area_lists(area):
                if not values:
                    continue
                chunk_id = f"{plan.grade}_{plan.subject}_t{trimester_index}_{next(counter)}"
                text = f"{area.title} — {key.title()}\n" + "\n".join(values)
                metadata = base_metadata | {"topic": key}
                yield {
                    "id": chunk_id,
                    "text": text,
                    "metadata": metadata,
                }


def _iter_area_lists(area) -> Iterable[tuple[str, list[str]]]:
    for key in (
        "objectives",
        "contents",
        "competences",
        "indicators",
        "projects",
        "methodology",
        "assessment",
    ):
        values = getattr(area, key)
        yield key, values
