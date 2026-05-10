"""Compilation contract for Markdown-to-WeChat rendering.

The public CLI remains in scripts/render.py. This module exists so the skill has
a stable place for future compiler expansion without letting LLMs author HTML.
"""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


def compile_plan(blocks: Sequence[Dict[str, Any]], plans: Sequence[Dict[str, Any]]) -> List[Dict[str, Any]]:
    return [{"block": block, "layout": plan} for block, plan in zip(blocks, plans)]

