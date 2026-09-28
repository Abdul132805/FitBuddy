"""Application settings loaded from the environment and the project .env file."""
from pathlib import Path
import os

from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "").strip()
AI_PROVIDER = os.getenv("AI_PROVIDER", "groq").strip().lower()
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{(ROOT_DIR / 'database' / 'fitbuddy.db').as_posix()}").strip()
# Railway's PostgreSQL plugin may expose the legacy postgres:// scheme.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+psycopg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
GROQ_MODEL = (os.getenv("GROQ_MODEL") or os.getenv("GROQ_WORKOUT_MODEL") or "openai/gpt-oss-120b").strip()
# GROQ_WORKOUT_MODEL remains available for existing integrations.
GROQ_WORKOUT_MODEL = GROQ_MODEL
GROQ_NUTRITION_MODEL = os.getenv("GROQ_NUTRITION_MODEL", "openai/gpt-oss-20b").strip()
