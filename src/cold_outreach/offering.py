"""Loads the DataMantra offering catalogue and formats it for prompt injection."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import yaml

_OFFERING_PATH = Path(__file__).parent / "config" / "offering.yaml"


@lru_cache(maxsize=1)
def load_offering() -> dict:
    """Load and parse the offering catalogue YAML, relative to this file."""
    with _OFFERING_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def format_offering_catalogue() -> str:
    """Render the offering catalogue as compact, readable text for a prompt."""
    data = load_offering()

    lines: list[str] = []
    lines.append(f"Company: {data['company']} ({data['website']})")
    lines.append(f"Positioning: {data['positioning'].strip()}")
    lines.append("")
    lines.append("Course tracks:")
    for track in data["tracks"]:
        lines.append(f"- {track['name']}: {track['covers']} (Best for: {track['best_for']})")
    lines.append("")
    lines.append("Proof points:")
    for point in data["proof_points"]:
        lines.append(f"- {point}")
    lines.append("")
    lines.append(f"Delivery formats: {data['delivery_formats'].strip()}")
    lines.append(f"Contact: {data['contact']}")

    return "\n".join(lines)
