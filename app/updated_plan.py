"""Refine the existing workout plan using user feedback."""
import json
from .gemini_generator import _generate


def update_workout_plan(user_info: dict, existing_plan: dict, feedback: str) -> dict:
    prompt = ("Revise this seven-day workout plan based on the user's feedback. Regenerate the plan meaningfully; "
              "keep it safe, practical, goal and intensity appropriate, preserve exactly seven days and the JSON "
              "schema {days:[{day,warmup:[...],main_workout:[...],cooldown:[...]}]}. Return JSON only. "
              f"Profile: {json.dumps(user_info)}. Existing plan: {json.dumps(existing_plan)}. "
              f"Feedback: {feedback}")
    return _generate(prompt)
