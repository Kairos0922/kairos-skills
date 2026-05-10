"""Deterministic semantic analysis for editorial block planning.

This module defines the contract that an LLM may mimic when layout optimization
is requested. The renderer itself uses this deterministic fallback and never asks
an LLM to produce HTML, CSS, spacing, or component styles.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence


EMPHASIS_RE = re.compile(r"(==.+?==|\*\*.+?\*\*|__.+?__)", re.DOTALL)
HIGHLIGHT_RE = re.compile(r"==.+?==", re.DOTALL)
FULL_EMPHASIS_RE = re.compile(r"^\s*(?:==(.+?)==|\*\*(.+?)\*\*|__(.+?)__)\s*$", re.DOTALL)
TECH_RE = re.compile(r"\b(API|SDK|CLI|JSON|HTML|CSS|Python|Agent|AI|LLM|Markdown|HTTP|URL)\b")


def text_of(block: Dict[str, Any]) -> str:
    block_type = block.get("type")
    if block_type in {"paragraph", "heading", "code"}:
        return str(block.get("text", ""))
    if block_type == "component":
        if block.get("name") == "figure":
            return f"{block.get('alt', '')} {block.get('caption', '')}".strip()
        if block.get("name") == "soft-list":
            return " ".join(str(item.get("text", "")) for item in block.get("items", []))
        return str(block.get("text", ""))
    if block_type == "quote":
        return " ".join(str(line) for line in block.get("lines", []))
    if block_type == "list":
        return " ".join(str(item.get("text", "")) for item in block.get("items", []))
    if block_type == "table":
        header = " ".join(str(cell) for cell in block.get("header", []))
        rows = " ".join(" ".join(str(cell) for cell in row) for row in block.get("rows", []))
        return f"{header} {rows}".strip()
    return ""


def density_score(text: str) -> float:
    clean = text.strip()
    if not clean:
        return 0.0
    cjk_chars = len(re.findall(r"[\u3400-\u9fff]", clean))
    latin_terms = len(TECH_RE.findall(clean))
    punctuation = len(re.findall(r"[，。！？；：,.!?;:]", clean))
    raw = (len(clean) / 180.0) + (latin_terms * 0.06) + (punctuation / 120.0)
    if cjk_chars > 0 and len(clean) / max(cjk_chars, 1) > 1.35:
        raw += 0.08
    return max(0.0, min(1.0, raw))


def analyze_block(block: Dict[str, Any], index: int, total: int) -> Dict[str, Any]:
    block_type = block.get("type")
    text = text_of(block)
    density = density_score(text)
    emphasis_count = len(EMPHASIS_RE.findall(text))
    highlight_count = len(HIGHLIGHT_RE.findall(text))
    full_emphasis = bool(FULL_EMPHASIS_RE.match(text))

    intent = "body"
    importance = "normal"
    should_split = False

    if block_type == "heading":
        intent = "structure"
        importance = "high"
    elif block_type == "quote":
        intent = "quote"
        importance = "medium"
        if text.lstrip().upper().startswith("[!TIP]"):
            intent = "insight"
            importance = "high"
    elif block_type == "list":
        intent = "structured"
        importance = "medium"
    elif block_type in {"code", "table"}:
        intent = "reference"
        importance = "medium"
    elif block_type == "divider":
        intent = "breathing"
    elif block_type == "component":
        component_name = str(block.get("name", ""))
        intent = {
            "lead": "opening",
            "insight": "insight",
            "pullquote": "quote",
            "figure": "media",
            "soft-list": "structured",
            "closing-note": "closing",
        }.get(component_name, "body")
        importance = "high" if component_name in {"lead", "insight", "pullquote"} else "medium"
    elif block_type == "paragraph":
        if full_emphasis or highlight_count or re.search(r"(关键|核心|真正|必须|注意|结论|因此|所以)", text):
            intent = "insight"
            importance = "high" if density >= 0.42 or full_emphasis or highlight_count else "medium"
        if len(text) >= 180 or density >= 0.82:
            should_split = True

    return {
        "index": index,
        "type": block_type,
        "importance": importance,
        "intent": intent,
        "density": round(density, 3),
        "emphasis_count": emphasis_count,
        "highlight_count": highlight_count,
        "full_emphasis": full_emphasis,
        "should_split": should_split,
        "position": "opening" if index <= 1 else "closing" if index >= total - 2 else "body",
    }


def analyze_blocks(blocks: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    total = len(blocks)
    return [analyze_block(block, index, total) for index, block in enumerate(blocks)]
