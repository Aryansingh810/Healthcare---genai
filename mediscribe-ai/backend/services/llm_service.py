"""
MediScribe AI - LLM Service (Grok)
Handles all Grok API interactions via HTTP.
Swap provider by replacing this module - no other code changes needed.
"""

import json
from typing import Optional

import requests

from config import GROK_API_KEY, GROK_MODEL, GROK_API_URL
from services.prompt_templates import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE


def _configure_grok() -> None:
    """Validate Grok API configuration."""
    if not GROK_API_KEY:
        raise ValueError(
            "GROK_API_KEY not set. Add it to .env or export in shell."
        )
    if not GROK_API_URL:
        raise ValueError("GROK_API_URL is not configured.")


class GrokAPIError(Exception):
    """Custom exception for Grok API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None, error_code: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


def generate_summary(retrieved_text: str) -> str:
    """
    Generate clinical summary from retrieved patient data using Grok.

    Args:
        retrieved_text: Patient data retrieved from vector database

    Returns:
        Formatted clinical summary string

    Raises:
        GrokAPIError: If API call fails (quota, rate limit, etc.)
        ValueError: If API key or URL is missing
    """
    _configure_grok()

    # Build plain-text prompt from system + user template
    user_prompt = USER_PROMPT_TEMPLATE.format(retrieved_text=retrieved_text)
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"

    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json",
    }

    payload = {
        "model": GROK_MODEL,
        # Send prompt as plain text payload
        "input": full_prompt,
    }

    try:
        resp = requests.post(GROK_API_URL, headers=headers, json=payload, timeout=60)
    except requests.RequestException as e:
        raise GrokAPIError(
            f"Grok API network error: {e}",
            status_code=None,
        )

    # Attempt to parse JSON response
    try:
        data = resp.json()
    except json.JSONDecodeError:
        raise GrokAPIError(
            f"Grok API returned non-JSON response with status {resp.status_code}.",
            status_code=resp.status_code,
        )

    # Handle non-2xx responses
    if not resp.ok:
        raw_error = data.get("error") if isinstance(data, dict) else None
        message = "Grok API error"
        error_code = None

        if isinstance(raw_error, dict):
            message = raw_error.get("message", message)
            error_code = raw_error.get("code")
        elif isinstance(raw_error, str):
            message = raw_error

        # Quota / rate limit
        if resp.status_code == 429 or (raw_error and "quota" in str(raw_error).lower()):
            raise GrokAPIError(
                "Grok API quota or rate limit exceeded. Please check your plan and billing.",
                status_code=429,
                error_code="RATE_LIMIT_EXCEEDED",
            )

        # Auth issues
        if resp.status_code in (401, 403):
            raise GrokAPIError(
                "Invalid or unauthorized GROK_API_KEY. Please verify your credentials.",
                status_code=resp.status_code,
                error_code="UNAUTHORIZED",
            )

        # Generic client/server error
        raise GrokAPIError(
            f"Grok API error ({resp.status_code}): {message}",
            status_code=resp.status_code,
            error_code=error_code,
        )

    # Extract generated text from Grok response.
    # Shape is API-dependent; we expect either:
    # - {'output': '...'}  or
    # - {'choices': [{'text': '...'}]} style.
    text: Optional[str] = None
    if isinstance(data, dict):
        if "output" in data and isinstance(data["output"], str):
            text = data["output"]
        elif "choices" in data and isinstance(data["choices"], list) and data["choices"]:
            choice = data["choices"][0]
            if isinstance(choice, dict):
                text = choice.get("text") or choice.get("message") or choice.get("content")

    if not text:
        raise GrokAPIError(
            "Grok API returned an empty or unrecognized response.",
            status_code=resp.status_code,
        )

    return text
