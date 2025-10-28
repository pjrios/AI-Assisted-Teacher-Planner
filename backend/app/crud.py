from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from . import models, schemas


def get_or_create_academic_year(
    db: Session, *, owner_id: int, year: int, start_date: date, end_date: date
) -> models.AcademicYear:
    statement = select(models.AcademicYear).where(
        models.AcademicYear.owner_id == owner_id,
        models.AcademicYear.year == year,
    )
    academic_year = db.execute(statement).scalar_one_or_none()
    if academic_year is None:
        academic_year = models.AcademicYear(
            owner_id=owner_id, year=year, start_date=start_date, end_date=end_date
        )
        db.add(academic_year)
        db.commit()
        db.refresh(academic_year)
    return academic_year


def create_trimester(
    db: Session, *, year_id: int, trimester: schemas.TrimesterBase
) -> models.Trimester:
    db_trimester = models.Trimester(
        year_id=year_id,
        name=trimester.name,
        start_date=trimester.start_date,
        end_date=trimester.end_date,
        total_weeks=trimester.total_weeks,
    )
    db.add(db_trimester)
    db.commit()
    db.refresh(db_trimester)
    return db_trimester


def create_level(db: Session, *, year_id: int, data: schemas.LevelBase) -> models.Level:
    db_level = models.Level(year_id=year_id, grade=data.grade, subject=data.subject)
    db.add(db_level)
    db.commit()
    db.refresh(db_level)
    return db_level


def create_topic(
    db: Session,
    *,
    level_id: int,
    trimester_id: int,
    data: schemas.TopicBase,
) -> models.Topic:
    db_topic = models.Topic(
        level_id=level_id,
        trimester_id=trimester_id,
        title=data.title,
        week_start=data.week_start,
        week_end=data.week_end,
        total_hours=data.total_hours,
        metadata=data.metadata.dict() if data.metadata else None,
    )
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    return db_topic


def create_class_session(
    db: Session,
    *,
    topic_id: int,
    group_id: int,
    data: schemas.ClassSessionCreate,
) -> models.ClassSession:
    db_class = models.ClassSession(
        topic_id=topic_id,
        group_id=group_id,
        date=data.date,
        start_time=data.start_time,
        end_time=data.end_time,
    )
    db.add(db_class)
    db.flush()
    for activity in data.activities:
        db_activity = models.Activity(
            class_id=db_class.id,
            pre=activity.pre,
            while_=activity.while_,
            post=activity.post,
            materials=activity.materials,
        )
        db.add(db_activity)
    db.commit()
    db.refresh(db_class)
    return db_class
