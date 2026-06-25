"""Shared constants, compiled regexes, and path roots.

Centralizes the tokens that both markdown parsing and HTML rendering depend on,
so ``scripts/render.py`` can stay focused on the render pipeline while the
renderer package owns the cross-cutting vocabulary.
"""

from __future__ import annotations

import re
from pathlib import Path

from renderer.blocks import ALLOWED_KAIROS_COMPONENTS

# Skill root is one level up from this package (renderer/ -> kairos-wechat-typeset/).
SKILL_ROOT = Path(__file__).resolve().parents[1]
THEMES_ROOT = SKILL_ROOT / "themes"
REGISTRY_PATH = THEMES_ROOT / "registry.json"

# ─── Markdown structure regexes ───
HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
UNORDERED_RE = re.compile(r"^(\s*)[-+*]\s+(.*)$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
TASK_ITEM_RE = re.compile(r"^\[(?P<mark>[ xX])\]\s+(?P<text>.+)$")
FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]*)\s*$")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
NUMERIC_SECTION_RE = re.compile(r"^(?P<num>\d{1,2})(?:[.、:：|｜\-\s]+)(?P<title>.+)$")
FULL_STRONG_RE = re.compile(r"^\s*(\*\*|__)(.+?)\1\s*$", re.DOTALL)
NOTE_RE = re.compile(r"^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s*(.*)$", re.IGNORECASE)
LATIN_WORD_RE = r"[A-Za-z0-9]+(?:[A-Za-z0-9./_:+%#@-]*[A-Za-z0-9])?"
COMPONENT_OPEN_RE = re.compile(r"^:::\s*([A-Za-z][A-Za-z0-9_-]*)\s*$")
COMPONENT_CLOSE_RE = re.compile(r"^:::\s*$")
FIGURE_IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")

# ─── Component vocabulary ───
SUPPORTED_COMPONENTS = ALLOWED_KAIROS_COMPONENTS

CHINESE_NUMERALS = {
    "01": "一",
    "02": "二",
    "03": "三",
    "04": "四",
    "05": "五",
    "06": "六",
    "07": "七",
    "08": "八",
    "09": "九",
    "10": "十",
}
