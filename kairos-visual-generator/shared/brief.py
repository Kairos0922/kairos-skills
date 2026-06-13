"""
Visual Brief: the deterministic interface between AI and code.

AI generates the Brief, code validates and consumes it.
Brief must pass JSON Schema validation before rendering.
"""

import json
from dataclasses import dataclass, field, asdict
from typing import Any


# Required fields for Visual Brief (quality gate)
REQUIRED_FIELDS = [
    "style_id",
    "theme_id",
    "usage",
    "ratio",
    "language",
    "core_word",
    "title_full",
    "tags",
    "main_metaphor",
    "layout_skeleton",
    "text_reconstruction",
    "content_density",
]

OPTIONAL_FIELDS = [
    "subtitle",
    "context",
    "banned_elements",
]


@dataclass
class VisualBrief:
    """Visual Brief data structure."""
    style_id: str = ""
    theme_id: str = ""
    usage: str = ""
    ratio: str = "4:5"
    language: str = "chinese"
    core_word: str = ""
    title_full: str = ""
    tags: list[str] = field(default_factory=list)
    main_metaphor: str = ""
    layout_skeleton: str = ""
    text_reconstruction: str = ""
    content_density: str = "cover"
    subtitle: str = ""
    context: str = ""
    banned_elements: list[str] = field(default_factory=list)


def validate_brief(brief: dict[str, Any]) -> tuple[bool, list[str]]:
    """Validate a Visual Brief against required fields.

    Returns (is_valid, list_of_missing_fields).
    """
    missing = [f for f in REQUIRED_FIELDS if not brief.get(f)]
    return len(missing) == 0, missing


def brief_to_dict(brief: VisualBrief) -> dict[str, Any]:
    """Convert VisualBrief dataclass to dict."""
    return asdict(brief)


def dict_to_brief(data: dict[str, Any]) -> VisualBrief:
    """Convert dict to VisualBrief dataclass."""
    return VisualBrief(**{k: v for k, v in data.items() if k in VisualBrief.__dataclass_fields__})


def save_brief(brief: VisualBrief, path: str) -> None:
    """Save Visual Brief to JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(brief_to_dict(brief), f, ensure_ascii=False, indent=2)


def load_brief(path: str) -> VisualBrief:
    """Load Visual Brief from JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return dict_to_brief(json.load(f))
