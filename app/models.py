"""Database model for user profile and generated plan history."""
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text
from .database import Base


class FitnessPlan(Base):
    __tablename__ = "fitness_plans"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(40), nullable=False)
    intensity = Column(String(30), nullable=False)
    workout_plan = Column(Text, nullable=False)
    nutrition_tip = Column(Text, nullable=False)
    feedback = Column(Text, nullable=True)
    updated_plan = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
