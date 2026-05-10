"""Spacing resolution for deterministic editorial rhythm."""

from __future__ import annotations

from typing import Any, Dict, Optional


def px(value: Any, fallback: int) -> int:
    if isinstance(value, (int, float)):
        return int(round(value))
    if isinstance(value, str) and value.endswith("px"):
        try:
            return int(round(float(value[:-2])))
        except ValueError:
            return fallback
    return fallback


def scaled(value: int, art_direction: Dict[str, Any], minimum: int = 0) -> int:
    return max(minimum, int(round(value * float(art_direction.get("spacing_scale", 1.0)))))


def rhythm_value(theme: Dict[str, Any], key: str, fallback: int) -> int:
    rhythm = theme.get("rhythm", {})
    return px(rhythm.get(key), fallback)


def resolve_spacing(
    block: Dict[str, Any],
    semantic: Dict[str, Any],
    theme: Dict[str, Any],
    art_direction: Dict[str, Any],
    previous: Optional[Dict[str, Any]] = None,
    following: Optional[Dict[str, Any]] = None,
) -> Dict[str, int]:
    block_type = str(block.get("type"))
    density = float(semantic.get("density", 0.0))

    paragraph = rhythm_value(theme, "paragraph_gap", 22)
    heading_top = rhythm_value(theme, "heading_top", 42)
    heading_bottom = rhythm_value(theme, "heading_bottom", 24)
    quote_breathing = rhythm_value(theme, "quote_breathing", 34)
    section_break = rhythm_value(theme, "section_break", 46)
    is_song = str(theme.get("id")) == "song"

    top = 0
    bottom = paragraph

    if block_type == "heading":
        level = int(block.get("level", 2))
        top = 0 if level == 1 else heading_top
        bottom = heading_bottom
    elif block_type == "quote":
        top = quote_breathing
        bottom = quote_breathing
    elif block_type == "divider":
        top = section_break
        bottom = max(14 if is_song else 30, section_break - 6)
    elif block_type in {"code", "table"}:
        top = max(22, paragraph + 4) if is_song else max(28, paragraph + 10)
        bottom = max(22, paragraph + 2) if is_song else max(30, paragraph + 8)
    elif block_type == "list":
        top = 0
        bottom = max(12, paragraph - 8)
    elif block_type == "paragraph" and semantic.get("intent") == "insight":
        bottom = paragraph + 4

    if density >= 0.76 and block_type in {"paragraph", "list"}:
        bottom += 8
    if previous and previous.get("type") == "heading" and block_type == "paragraph":
        top = 0
    if (
        is_song
        and previous
        and previous.get("type") == "divider"
        and block_type == "heading"
    ):
        top = max(6, int(round(heading_top * 0.36)))
    if following and following.get("type") == "divider":
        bottom = max(16, bottom - 8)
    if (
        is_song
        and block_type == "divider"
        and following
        and following.get("type") == "heading"
    ):
        bottom = max(10, int(round(section_break * 0.4)))

    return {
        "top": scaled(top, art_direction),
        "bottom": scaled(bottom, art_direction, minimum=8 if block_type != "heading" else 0),
    }
