from __future__ import annotations

from datetime import date, time
from typing import Any

from sqlalchemy import Date, ForeignKey, Integer, JSON, String, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)

    academic_years: Mapped[list[AcademicYear]] = relationship(
        "AcademicYear", back_populates="owner", cascade="all, delete-orphan"
    )


class AcademicYear(Base):
    __tablename__ = "academic_years"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    owner: Mapped[User] = relationship("User", back_populates="academic_years")
    trimesters: Mapped[list[Trimester]] = relationship(
        "Trimester", back_populates="academic_year", cascade="all, delete-orphan"
    )
    levels: Mapped[list[Level]] = relationship(
        "Level", back_populates="academic_year", cascade="all, delete-orphan"
    )


class Trimester(Base):
    __tablename__ = "trimesters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(64), nullable=False)
    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    end_date: Mapped[date] = mapped_column(Date, nullable=False)
    total_weeks: Mapped[int] = mapped_column(Integer, nullable=False)

    academic_year: Mapped[AcademicYear] = relationship("AcademicYear", back_populates="trimesters")
    topics: Mapped[list[Topic]] = relationship(
        "Topic", back_populates="trimester", cascade="all, delete-orphan"
    )
    rubrics: Mapped[list[Rubric]] = relationship(
        "Rubric", back_populates="trimester", cascade="all, delete-orphan"
    )


class Level(Base):
    __tablename__ = "levels"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    year_id: Mapped[int] = mapped_column(ForeignKey("academic_years.id"), nullable=False)
    grade: Mapped[str] = mapped_column(String(32), nullable=False)
    subject: Mapped[str] = mapped_column(String(128), nullable=False)

    academic_year: Mapped[AcademicYear] = relationship("AcademicYear", back_populates="levels")
    groups: Mapped[list[Group]] = relationship(
        "Group", back_populates="level", cascade="all, delete-orphan"
    )
    topics: Mapped[list[Topic]] = relationship(
        "Topic", back_populates="level", cascade="all, delete-orphan"
    )
    rubrics: Mapped[list[Rubric]] = relationship(
        "Rubric", back_populates="level", cascade="all, delete-orphan"
    )
    resources: Mapped[list[Resource]] = relationship(
        "Resource", back_populates="level", cascade="all, delete-orphan"
    )


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    weekly_schedule: Mapped[Any] = mapped_column(JSON, nullable=False)

    level: Mapped[Level] = relationship("Level", back_populates="groups")
    classes: Mapped[list[ClassSession]] = relationship(
        "ClassSession", back_populates="group", cascade="all, delete-orphan"
    )


class Topic(Base):
    __tablename__ = "topics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    trimester_id: Mapped[int] = mapped_column(ForeignKey("trimesters.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    week_start: Mapped[int] = mapped_column(Integer, nullable=False)
    week_end: Mapped[int] = mapped_column(Integer, nullable=False)
    total_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata: Mapped[Any] = mapped_column(JSON, nullable=True)

    level: Mapped[Level] = relationship("Level", back_populates="topics")
    trimester: Mapped[Trimester] = relationship("Trimester", back_populates="topics")
    classes: Mapped[list[ClassSession]] = relationship(
        "ClassSession", back_populates="topic", cascade="all, delete-orphan"
    )


class ClassSession(Base):
    __tablename__ = "classes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), nullable=False)
    topic_id: Mapped[int] = mapped_column(ForeignKey("topics.id"), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)

    group: Mapped[Group] = relationship("Group", back_populates="classes")
    topic: Mapped[Topic] = relationship("Topic", back_populates="classes")
    activities: Mapped[list[Activity]] = relationship(
        "Activity", back_populates="class_session", cascade="all, delete-orphan"
    )


class Activity(Base):
    __tablename__ = "activities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"), nullable=False)
    pre: Mapped[str] = mapped_column(String, nullable=True)
    while_: Mapped[str] = mapped_column("while", String, nullable=True)
    post: Mapped[str] = mapped_column(String, nullable=True)
    materials: Mapped[str | None] = mapped_column(String, nullable=True)

    class_session: Mapped[ClassSession] = relationship("ClassSession", back_populates="activities")


class Rubric(Base):
    __tablename__ = "rubrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    trimester_id: Mapped[int] = mapped_column(ForeignKey("trimesters.id"), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    criteria: Mapped[Any] = mapped_column(JSON, nullable=False)
    weight: Mapped[int] = mapped_column(Integer, nullable=False)

    level: Mapped[Level] = relationship("Level", back_populates="rubrics")
    trimester: Mapped[Trimester] = relationship("Trimester", back_populates="rubrics")


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    level_id: Mapped[int] = mapped_column(ForeignKey("levels.id"), nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    file_url: Mapped[str] = mapped_column(String(255), nullable=False)

    level: Mapped[Level] = relationship("Level", back_populates="resources")
