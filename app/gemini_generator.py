"""Groq-powered structured workout plan generation."""
import json
import re
import logging
from typing import Any

from .config import GROQ_WORKOUT_MODEL
from .groq_client import GroqError, generate_text, log_provider_error
from .schemas import WorkoutPlan

logger = logging.getLogger(__name__)
# Kept as an alias for code that imported this historical exception name.
GeminiError = GroqError


def _decode_plan(text: str) -> dict[str, Any]:
    cleaned = text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.IGNORECASE)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start < 0 or end < start:
        raise ValueError("Provider did not return JSON.")
    data = json.loads(cleaned[start:end + 1])
    plan = WorkoutPlan.model_validate(data)
    return plan.model_dump()


def _generate(prompt: str, *, model: str = GROQ_WORKOUT_MODEL) -> dict[str, Any]:
    try:
        content = generate_text(
            model=model,
            messages=[
                {"role": "system", "content": "You create safe, practical fitness plans. Return only a valid JSON object."},
                {"role": "user", "content": prompt},
            ],
            json_mode=True,
            temperature=0.5,
            max_tokens=3500,
        )
        return _decode_plan(content)
    except GroqError:
        raise
    except Exception as exc:
        log_provider_error("workout response validation", exc)
        raise GroqError("Groq returned a response that did not match the seven-day plan format. Please try again.") from exc


def generate_workout_groq(age: int, weight: float, goal: str, intensity: str, username: str) -> dict[str, Any]:
    prompt = f"""Create a safe, practical fitness plan as JSON only with exactly seven days, each with string arrays warmup, main_workout, cooldown, and a day label. Include specific exercises and sets/reps or duration. Match the goal and stated intensity, account reasonably for age and weight, include appropriate rest/recovery, avoid medical claims, and keep it readable. Profile: name={username}, age={age}, weight_kg={weight}, goal={goal}, intensity={intensity}. Use rest or active recovery where appropriate. Format: {{\"days\":[{{\"day\":\"Day 1\",\"warmup\":[\"...\"],\"main_workout\":[\"...\"],\"cooldown\":[\"...\"]}}]}}"""
    return _generate(prompt)


# Preserve imports from the original project while routing all requests through Groq.
generate_workout_gemini = generate_workout_groq
