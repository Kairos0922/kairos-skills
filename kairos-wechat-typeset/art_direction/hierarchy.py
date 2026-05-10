"""Heading hierarchy checks."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence


def heading_hierarchy_findings(blocks: Sequence[Dict[str, Any]]) -> List[str]:
    findings: List[str] = []
    previous_level = 0
    for index, block in enumerate(blocks):
        if block.get("type") != "heading":
            continue
        level = int(block.get("level", 1))
        if previous_level and level > previous_level + 1:
            findings.append(
                f"Heading hierarchy skips from H{previous_level} to H{level} near block {index + 1}."
            )
        previous_level = level
    return findings

