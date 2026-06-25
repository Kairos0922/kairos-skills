"""Theme registry access.

Reads ``themes/registry.json`` and resolves theme ids to their JSON contracts.
Kept separate from the render pipeline so theme loading stays a pure file-IO
concern with no rendering coupling.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List

from renderer._tokens import REGISTRY_PATH, THEMES_ROOT


def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Theme registry not found: {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def available_themes() -> List[Dict[str, Any]]:
    return list(load_registry().get("themes", []))


def default_theme_id() -> str:
    registry = load_registry()
    return str(registry.get("default") or "song")


def load_theme(theme_id: str) -> Dict[str, Any]:
    registry = load_registry()
    themes = {theme["id"]: theme for theme in registry.get("themes", [])}
    if theme_id not in themes:
        valid = ", ".join(sorted(themes))
        raise ValueError(f"Unknown theme '{theme_id}'. Available themes: {valid}")

    theme_path = THEMES_ROOT / themes[theme_id]["path"]
    if not theme_path.exists():
        raise FileNotFoundError(f"Registered theme file not found: {theme_path}")
    theme = json.loads(theme_path.read_text(encoding="utf-8"))
    if theme.get("id") != theme_id:
        raise ValueError(f"Theme id mismatch in {theme_path}: expected {theme_id}")
    return theme


def print_themes() -> None:
    for theme in available_themes():
        suitable = " / ".join(theme.get("suitable_for", []))
        print(f"{theme['id']}\t{theme.get('name_zh', theme['name'])}\t{suitable}")
