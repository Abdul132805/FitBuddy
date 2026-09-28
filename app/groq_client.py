"""Shared Groq client call with redacted diagnostics and safe user errors."""
import logging
import re
from typing import Any

from .config import AI_PROVIDER, GROQ_API_KEY

logger = logging.getLogger(__name__)


class GroqError(RuntimeError):
    """Safe-to-display error for unavailable Groq generation."""


def log_provider_error(operation: str, exc: Exception) -> None:
    """Log actionable provider details after redacting keys and bearer tokens."""
    try:
        message = str(exc)
    except Exception:
        message = "<exception message unavailable>"
    if GROQ_API_KEY:
        message = message.replace(GROQ_API_KEY, "[REDACTED]")
    message = re.sub(r"gsk_[A-Za-z0-9_-]+", "[REDACTED]", message)
    message = re.sub(r"(?i)Bearer\s+\S+", "Bearer [REDACTED]", message)
    message = " ".join(message.split())[:500]
    logger.error(
        "Groq %s failed (exception_type=%s, status_code=%s, request_id=%s, message=%s)",
        operation, type(exc).__name__, getattr(exc, "status_code", None),
        getattr(exc, "request_id", None), message,
    )


def generate_text(
    *, model: str, messages: list[dict[str, str]], json_mode: bool = False,
    temperature: float = 0.4, max_tokens: int = 3000,
) -> str:
    if not GROQ_API_KEY:
        raise GroqError("Groq is not configured. Set GROQ_API_KEY in the project .env file and restart FitBuddy.")
    if AI_PROVIDER != "groq":
        raise GroqError("AI_PROVIDER must be set to 'groq' in the project .env file.")

    try:
        from groq import Groq

        client = Groq(api_key=GROQ_API_KEY)
        request: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_completion_tokens": max_tokens,
        }
        if json_mode:
            request["response_format"] = {"type": "json_object"}
        completion = client.chat.completions.create(**request)
        choice = completion.choices[0]
        content = choice.message.content
        if not content or not content.strip():
            raise ValueError(f"The provider returned no visible content (finish_reason={choice.finish_reason}).")
        return content
    except Exception as exc:
        # Requests and prompts are never logged; the error message is credential-redacted.
        log_provider_error("completion", exc)
        raise GroqError("The AI service could not create a plan right now. Check your Groq API key and model configuration.") from exc
