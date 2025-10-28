from __future__ import annotations

from datetime import date, time
from typing import Any

from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    pre: str | None = None
    while_: str | None = Field(default=None, alias="while")
    post: str | None = None
    materials: str | None = None

    class Config:
        populate_by_name = True
        orm_mode = True


class ActivityCreate(ActivityBase):
    pass


class ActivityRead(ActivityBase):
    id: int


class ClassSessionBase(BaseModel):
    date: date
    start_time: time
    end_time: time


class ClassSessionCreate(ClassSessionBase):
    topic_id: int
    group_id: int
    activities: list[ActivityCreate] = []


class ClassSessionRead(ClassSessionBase):
    id: int
    topic_id: int
    group_id: int
    activities: list[ActivityRead] = []

    class Config:
        orm_mode = True


class TopicMetadata(BaseModel):
    objectives: list[str] = []
    contents: list[str] = []
    competences: list[str] = []
    indicators: list[str] = []
    projects: list[str] = []
    methodology: list[str] = []
    assessment: list[str] = []


class TopicBase(BaseModel):
    title: str
    week_start: int
    week_end: int
    total_hours: int
    metadata: TopicMetadata | None = None


class TopicCreate(TopicBase):
    trimester_id: int
    level_id: int


class TopicRead(TopicBase):
    id: int
    trimester_id: int
    level_id: int

    class Config:
        orm_mode = True


class TrimesterBase(BaseModel):
    name: str
    start_date: date
    end_date: date
    total_weeks: int


class TrimesterCreate(TrimesterBase):
    year_id: int


class TrimesterRead(TrimesterBase):
    id: int
    year_id: int

    class Config:
        orm_mode = True


class LevelBase(BaseModel):
    grade: str
    subject: str


class LevelCreate(LevelBase):
    year_id: int


class LevelRead(LevelBase):
    id: int
    year_id: int

    class Config:
        orm_mode = True


class AcademicYearBase(BaseModel):
    year: int
    start_date: date
    end_date: date


class AcademicYearCreate(AcademicYearBase):
    owner_id: int


class AcademicYearRead(AcademicYearBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class YearlyPlanArea(BaseModel):
    title: str
    objectives: list[str] = []
    contents: list[str] = []
    competences: list[str] = []
    indicators: list[str] = []
    projects: list[str] = []
    methodology: list[str] = []
    assessment: list[str] = []


class YearlyPlanTrimester(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None
    weeks: int | None = None
    areas: list[YearlyPlanArea] = []


class YearlyPlan(BaseModel):
    year: int
    grade: str
    subject: str
    trimesters: list[YearlyPlanTrimester]


class YearlyPlanIngestionResult(BaseModel):
    structured: YearlyPlan
    chunks: list[dict[str, Any]]


class LessonSessionSlot(BaseModel):
    date: date
    start_time: time
    end_time: time


class LessonGenerationRequest(BaseModel):
    schedule: list[LessonSessionSlot]
    metadata: dict[str, str] = {}

