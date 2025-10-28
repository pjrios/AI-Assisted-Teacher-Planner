from __future__ import annotations

from datetime import date, datetime, time, timedelta
from typing import Iterable

from openai import OpenAI

from ..config import get_settings
from ..vectorstore import VectorStore

settings = get_settings()


class LessonPlanner:
    def __init__(self, *, vector_store: VectorStore | None = None) -> None:
        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY must be configured for lesson planning")
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.vector_store = vector_store or VectorStore()

    def plan_topic(
        self,
        *,
        query: str,
        schedule: list[tuple[date, time, time]],
        metadata: dict[str, str],
        k: int = 5,
    ) -> list[dict[str, str]]:
        context_blocks = self.vector_store.similarity_search(query, n_results=k)
        prompt = self._build_prompt(schedule=schedule, metadata=metadata, context_blocks=context_blocks)
        response = self.client.responses.create(
            model="gpt-4.1",
            input=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        message = response.output[0].content[0].text if response.output else ""
        return self._parse_response(message)

    def _build_prompt(
        self,
        *,
        schedule: list[tuple[date, time, time]],
        metadata: dict[str, str],
        context_blocks: Iterable[dict[str, str]],
    ) -> str:
        context_text = "\n\n".join(
            f"Topic: {block['metadata'].get('topic')}\n{block['text']}" for block in context_blocks
        )
        schedule_text = "\n".join(
            f"- {slot_date.isoformat()} {start.strftime('%H:%M')} - {end.strftime('%H:%M')}"
            for slot_date, start, end in schedule
        )
        metadata_lines = "\n".join(f"{key.title()}: {value}" for key, value in metadata.items())
        return (
            "You are an instructional designer. Use the provided context to craft detailed "
            "lesson activities following the pre-while-post structure."
            "\n\nContext:\n"
            f"{context_text}\n\nSchedule:\n{schedule_text}\n\nMetadata:\n{metadata_lines}\n\n"
            "Return the plan as bullet points grouped by class session. Each bullet must include "
            "pre, while, and post segments."
        )

    def _parse_response(self, text: str) -> list[dict[str, str]]:
        sessions: list[dict[str, str]] = []
        current_session: dict[str, str] | None = None
        for line in text.splitlines():
            stripped = line.strip().lstrip("- ")
            if not stripped:
                continue
            if stripped.lower().startswith("session"):
                if current_session:
                    sessions.append(current_session)
                current_session = {"title": stripped, "content": ""}
            else:
                if current_session is None:
                    current_session = {"title": "Session", "content": stripped}
                else:
                    current_session["content"] += ("\n" if current_session["content"] else "") + stripped
        if current_session:
            sessions.append(current_session)
        return sessions
