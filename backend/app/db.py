from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from .config import get_settings

settings = get_settings()

engine = create_engine(settings.database_url, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_database() -> None:
    """Create database tables if they do not already exist."""

    # Importing the models inside the function avoids circular imports while
    # ensuring all SQLAlchemy metadata is registered before ``create_all`` runs.
    from . import models  # noqa: F401 (imported for side effects)

    Base.metadata.create_all(bind=engine)
