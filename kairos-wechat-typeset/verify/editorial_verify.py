"""Editorial verification for rhythm, hierarchy, and restraint."""

from __future__ import annotations

from typing import Any, Dict, List, Sequence

from art_direction.hierarchy import heading_hierarchy_findings
from renderer.variants import variant_findings
from semantic.analyze import analyze_blocks, text_of


def verify_editorial_blocks(blocks: Sequence[Dict[str, Any]], theme: Dict[str, Any]) -> List[str]:
    findings: List[str] = []
    semantics = analyze_blocks(blocks)
    findings.extend(heading_hierarchy_findings(blocks))
    findings.extend(variant_findings(theme))

    consecutive_long_paragraphs = 0
    consecutive_emphasis = 0
    section_density = 0.0
    section_has_breathing = True
    section_start = 1

    def flush_section(current_index: int) -> None:
        nonlocal section_density, section_has_breathing, section_start
        if section_density >= 3.0 and not section_has_breathing:
            findings.append(
                f"High-density section starting near block {section_start} needs a divider, quote, or list breathing point."
            )
        section_density = 0.0
        section_has_breathing = False
        section_start = current_index + 1

    for index, (block, semantic) in enumerate(zip(blocks, semantics)):
        block_type = block.get("type")
        text = text_of(block)

        if block_type == "heading":
            flush_section(index)
            consecutive_long_paragraphs = 0
            consecutive_emphasis = 0
            continue

        if block_type in {"divider", "quote", "list"}:
            section_has_breathing = True

        section_density += float(semantic.get("density", 0.0))

        if block_type == "paragraph" and len(text) >= 120:
            consecutive_long_paragraphs += 1
            if consecutive_long_paragraphs > 3:
                findings.append(
                    f"More than 3 consecutive long paragraphs near block {index + 1}; add breathing or split content."
                )
        elif block_type != "paragraph":
            consecutive_long_paragraphs = 0

        emphasis_block = bool(semantic.get("full_emphasis")) or int(semantic.get("highlight_count", 0)) > 0
        if emphasis_block:
            consecutive_emphasis += 1
            if consecutive_emphasis > 2:
                findings.append(
                    f"More than 2 consecutive emphasis blocks near block {index + 1}; reduce highlight frequency."
                )
        elif block_type not in {"divider"}:
            consecutive_emphasis = 0

    flush_section(len(blocks))
    return findings
