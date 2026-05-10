"""Resolve theme philosophy into deterministic art direction."""

from __future__ import annotations

from typing import Any, Dict, Optional


DENSITY_SCALE = {
    "low": 0.94,
    "medium": 1.0,
    "high": 1.08,
}

TONE_EMPHASIS = {
    "literary": "restrained",
    "analytical": "precise",
    "professional": "quiet",
}


def select_art_direction(
    theme: Dict[str, Any],
    article_type: Optional[str] = None,
    density: Optional[str] = None,
    tone: Optional[str] = None,
) -> Dict[str, Any]:
    philosophy = theme.get("philosophy", {})
    defaults = theme.get("art_direction", {})
    resolved_density = density or philosophy.get("density") or defaults.get("visual_density") or "medium"
    resolved_tone = tone or philosophy.get("mood") or article_type or "professional"

    spacing_scale = float(defaults.get("spacing_scale", 1.0)) * DENSITY_SCALE.get(str(resolved_density), 1.0)
    emphasis_mode = defaults.get("emphasis_mode") or TONE_EMPHASIS.get(str(resolved_tone), "restrained")

    return {
        "theme": theme.get("id"),
        "article_type": article_type or defaults.get("article_type") or "editorial",
        "tone": resolved_tone,
        "spacing_scale": round(spacing_scale, 3),
        "emphasis_mode": emphasis_mode,
        "visual_density": defaults.get("visual_density") or resolved_density,
        "section_rhythm": defaults.get("section_rhythm") or philosophy.get("rhythm") or "editorial",
        "hierarchy": philosophy.get("hierarchy") or "clean",
    }

