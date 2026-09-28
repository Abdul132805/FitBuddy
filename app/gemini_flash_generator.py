"""Groq fast-model nutrition and recovery tip generation."""
import logging

from .config import GROQ_NUTRITION_MODEL
from .groq_client import GroqError, generate_text

logger = logging.getLogger(__name__)


def generate_nutrition_tip_with_flash(age: int, weight: float, goal: str, intensity: str) -> str:
    from .groq_client import GROQ_API_KEY
    if not GROQ_API_KEY:
        return "Build meals around protein-rich foods, colorful vegetables, whole-food carbohydrates, and regular hydration. Adjust portions to your needs and recovery."
    try:
        prompt = (f"Give one concise, practical general nutrition and recovery tip for an adult age {age}, "
                  f"weight {weight} kg, goal {goal}, training intensity {intensity}. Avoid calorie prescriptions, "
                  "medical claims, and restrictive advice. Return plain text in 1-2 sentences.")
        response = generate_text(
            model=GROQ_NUTRITION_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            # GPT-OSS may spend part of this budget on reasoning before its answer.
            max_tokens=1024,
        )
        return response.strip()
    except GroqError:
        logger.warning("Groq nutrition tip unavailable; using the built-in general guidance.")
        return "Choose balanced meals with protein, vegetables, and nourishing carbohydrates, and drink water regularly to support training and recovery."
