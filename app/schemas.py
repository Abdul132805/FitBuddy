"""Input validation and shared workout-plan shape."""
from typing import List
from pydantic import BaseModel, Field, field_validator

GOALS = ("Weight Loss", "Muscle Gain", "General Wellness")
INTENSITIES = ("Beginner", "Moderate", "Advanced")


class UserInput(BaseModel):
    username: str = Field(min_length=1, max_length=80)
    age: int = Field(ge=13, le=100)
    weight: float = Field(ge=25, le=350)
    goal: str
    intensity: str

    @field_validator("username")
    @classmethod
    def clean_username(cls, value: str) -> str:
        value = " ".join(value.split())
        if not value:
            raise ValueError("Please enter a username.")
        return value

    @field_validator("goal")
    @classmethod
    def valid_goal(cls, value: str) -> str:
        if value not in GOALS:
            raise ValueError("Choose a supported fitness goal.")
        return value

    @field_validator("intensity")
    @classmethod
    def valid_intensity(cls, value: str) -> str:
        if value not in INTENSITIES:
            raise ValueError("Choose a supported workout intensity.")
        return value


class WorkoutDay(BaseModel):
    day: str
    warmup: List[str]
    main_workout: List[str]
    cooldown: List[str]


class WorkoutPlan(BaseModel):
    days: List[WorkoutDay] = Field(min_length=7, max_length=7)


class FeedbackInput(BaseModel):
    feedback: str = Field(min_length=3, max_length=1000)


class UpdatedWorkoutPlan(WorkoutPlan):
    pass
