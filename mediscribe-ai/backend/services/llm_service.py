

import json
from typing import Optional

import requests

from config import GROQ_API_KEY, GROQ_MODEL, GROQ_API_URL
from services.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def _configure_groq() -> None:
    """Validate Groq API configuration."""
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY not set. Add it to .env or export in shell."
        )
    if not GROQ_API_URL:
        raise ValueError("GROQ_API_URL is not configured.")


class GroqAPIError(Exception):
    """Custom exception for Groq API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


def generate_summary(retrieved_text: str) -> str:
    """
    Generate clinical summary from retrieved patient data using Groq.

    Args:
        retrieved_text: Patient data retrieved from vector database

    Returns:
        Formatted clinical summary string

    Raises:
        GroqAPIError: If API call fails (quota, rate limit, etc.)
        ValueError: If API key or URL is missing
    """
    _configure_groq()

    # Build chat-style prompt from system + user template
    user_prompt = USER_PROMPT_TEMPLATE.format(retrieved_text=retrieved_text)

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    }

    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=60)
    except requests.RequestException as e:
        raise GroqAPIError(
            f"Groq API network error: {e}",
            status_code=None,
        )

    # Attempt to parse JSON response
    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise GroqAPIError(
            f"Groq API returned non-JSON response with status {resp.status_code}.",
            status_code=resp.status_code,
        )

    # Handle non-2xx responses
    if not resp.ok:
        raw_error = data.get("error") if isinstance(data, dict) else None
        message = "Groq API error"
        error_code = None

        if isinstance(raw_error, dict):
            message = raw_error.get("message", message)
            error_code = raw_error.get("code")
        elif isinstance(raw_error, str):
            message = raw_error

        # Quota / rate limit
        if resp.status_code == 429 or (raw_error and "quota" in str(raw_error).lower()):
            raise GroqAPIError(
                "Groq API quota or rate limit exceeded. Please check your plan and billing.",
                status_code=429,
                error_code="RATE_LIMIT_EXCEEDED",
            )

        # Auth issues
        if resp.status_code in (401, 403):
            raise GroqAPIError(
                "Invalid or unauthorized GROQ_API_KEY. Please verify your credentials.",
                status_code=resp.status_code,
                error_code="UNAUTHORIZED",
            )

        # Generic client/server error
        raise GroqAPIError(
            f"Groq API error ({resp.status_code}): {message}",
            status_code=resp.status_code,
            error_code=error_code,
        )

    # Extract generated text from Groq chat completion response.
    text: Optional[str] = None
    if isinstance(data, dict) and isinstance(data.get("choices"), list) and data["choices"]:
        first = data["choices"][0]
        if isinstance(first, dict):
            # OpenAI-compatible: choices[0].message.content
            message = first.get("message")
            if isinstance(message, dict):
                text = message.get("content")
            # Fallbacks
            if not text:
                text = first.get("text")

    if not text:
        raise GroqAPIError(
            "Groq API returned an empty or unrecognized response.",
            status_code=resp.status_code,
        )

    return text
