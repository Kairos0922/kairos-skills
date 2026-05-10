"""Rhythm planning for block sequences."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from .spacing import resolve_spacing


def build_rhythm_plan(
    blocks: Sequence[Dict[str, Any]],
    semantics: Sequence[Dict[str, Any]],
    theme: Dict[str, Any],
    art_direction: Dict[str, Any],
) -> List[Dict[str, Any]]:
    plans: List[Dict[str, Any]] = []
    for index, block in enumerate(blocks):
        previous = blocks[index - 1] if index > 0 else None
        following = blocks[index + 1] if index + 1 < len(blocks) else None
        semantic = semantics[index]
        spacing = resolve_spacing(block, semantic, theme, art_direction, previous, following)
        plans.append(
            {
                "component": component_for(block, semantic),
                "variant": variant_for(theme, block, semantic),
                "spacing_top": spacing["top"],
                "spacing_bottom": spacing["bottom"],
                "semantic": semantic,
            }
        )
    return plans


def component_for(block: Dict[str, Any], semantic: Dict[str, Any]) -> str:
    block_type = str(block.get("type"))
    if block_type == "component":
        return str(block.get("name", "component")).title().replace("-", "")
    if block_type == "paragraph" and semantic.get("intent") == "insight":
        return "Insight"
    return {
        "paragraph": "Paragraph",
        "heading": "Heading",
        "quote": "Quote",
        "list": "List",
        "divider": "Divider",
        "code": "Code",
        "table": "Table",
    }.get(block_type, "Paragraph")


def variant_for(theme: Dict[str, Any], block: Dict[str, Any], semantic: Dict[str, Any]) -> str:
    variants = theme.get("components", {})
    component = component_for(block, semantic).lower()
    allowed = variants.get(component, {}).get("variants", [])
    if not allowed:
        return "default"
    intent = semantic.get("intent")
    for candidate in allowed:
        if intent and str(intent) in str(candidate):
            return str(candidate)
    return str(allowed[0])
