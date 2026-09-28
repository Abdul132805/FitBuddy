"""SQLite engine, session factory, and database initialization."""
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL, ROOT_DIR

(ROOT_DIR / "database").mkdir(parents=True, exist_ok=True)
if DATABASE_URL.startswith("sqlite:"):
    # Ensure a configured SQLite file path (for example /data/fitbuddy.db) exists.
    from pathlib import Path
    from sqlalchemy.engine import make_url

    sqlite_path = make_url(DATABASE_URL).database
    if sqlite_path and sqlite_path != ":memory:":
        Path(sqlite_path).expanduser().resolve().parent.mkdir(parents=True, exist_ok=True)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from . import models  # noqa: F401 - register ORM models before create_all
    Base.metadata.create_all(bind=engine)
