"""OpenRouter-backed LLM factory shared by every agent in the crew."""

from __future__ import annotations

import os

from crewai import LLM
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_MODEL = "anthropic/claude-sonnet-5"
_OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

_ROLE_TEMPERATURES: dict[str, float] = {
    "researcher": 0.2,
    "strategist": 0.4,
    "copywriter": 0.7,
}


def _require_env(var_name: str) -> str:
    """Return the value of an environment variable or raise a clear error."""
    value = os.environ.get(var_name)
    if not value:
        raise RuntimeError(
            f"Missing required environment variable '{var_name}'. "
            "Set it in your .env file before running the crew."
        )
    return value


def get_llm(role: str, model: str | None = None) -> LLM:
    """Build an OpenRouter-backed `LLM` configured for the given agent role.

    Args:
        role: One of "researcher", "strategist", "copywriter" — controls
            the sampling temperature used for that agent.
        model: Optional OpenRouter model slug override. Falls back to the
            `OPENROUTER_MODEL` env var, then a hardcoded default.

    Raises:
        RuntimeError: if `OPENROUTER_API_KEY` or `SERPER_API_KEY` is unset.
    """
    api_key = _require_env("OPENROUTER_API_KEY")
    # SerperDevTool reads this itself, but we validate its presence here too
    # so a missing key fails fast at startup rather than mid-crew.
    _require_env("SERPER_API_KEY")

    model_slug = model or os.environ.get("OPENROUTER_MODEL", _DEFAULT_MODEL)
    temperature = _ROLE_TEMPERATURES.get(role, 0.4)

    return LLM(
        model=f"openrouter/{model_slug}",
        base_url=_OPENROUTER_BASE_URL,
        api_key=api_key,
        temperature=temperature,
    )
