"""Markdown verification for WeChat article inputs and layout contracts."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Sequence

from art_direction.hierarchy import heading_hierarchy_findings
from semantic.analyze import analyze_blocks, text_of


RAW_HTML_RE = re.compile(r"<(?!!--\s*段落分割线\s*-->)[A-Za-z][^>]*>", re.IGNORECASE)
STYLE_TOKEN_RE = re.compile(r"\b(style|class)\s*=", re.IGNORECASE)
HIGHLIGHT_RE = re.compile(r"==.+?==", re.DOTALL)


def verify_markdown_safety(markdown: str) -> List[str]:
    findings: List[str] = []
    lowered = markdown.lower()

    if RAW_HTML_RE.search(markdown):
        findings.append("Markdown must not contain raw HTML tags.")
    if STYLE_TOKEN_RE.search(markdown):
        findings.append("Markdown must not contain style= or class= attributes.")
    if "<style" in lowered or "</style" in lowered:
        findings.append("Markdown must not contain style blocks.")
    if "<script" in lowered or "</script" in lowered:
        findings.append("Markdown must not contain scripts.")
    return findings


def verify_markdown_text(markdown: str, blocks: Sequence[Dict[str, Any]]) -> List[str]:
    findings = verify_markdown_safety(markdown)
    findings.extend(heading_hierarchy_findings(blocks))
    findings.extend(_highlight_frequency_findings(markdown))
    findings.extend(_block_contract_findings(blocks))
    return findings


def _highlight_frequency_findings(markdown: str) -> List[str]:
    clean = markdown.strip()
    if not clean:
        return []
    highlight_chars = sum(len(match.group(0)) - 4 for match in HIGHLIGHT_RE.finditer(clean))
    ratio = highlight_chars / max(len(clean), 1)
    if ratio > 0.08:
        return [f"Highlight frequency is {ratio:.1%}; keep ==highlight== usage at or below 8%."]
    return []


def _block_contract_findings(blocks: Sequence[Dict[str, Any]]) -> List[str]:
    findings: List[str] = []
    semantics = analyze_blocks(blocks)
    consecutive_emphasis = 0

    for index, (block, semantic) in enumerate(zip(blocks, semantics), start=1):
        block_type = str(block.get("type"))
        text = text_of(block)

        if block_type == "heading" and int(block.get("level", 1)) > 3:
            findings.append(f"Heading near block {index} is deeper than ###; keep layout Markdown to H1-H3.")

        if block_type == "paragraph" and len(text) > 240:
            findings.append(f"Paragraph near block {index} is very long; split it before rendering.")

        emphasis_block = bool(semantic.get("full_emphasis")) or int(semantic.get("highlight_count", 0)) > 0
        if emphasis_block:
            consecutive_emphasis += 1
            if consecutive_emphasis > 2:
                findings.append(f"More than 2 consecutive emphasis blocks near block {index}.")
        elif block_type != "divider":
            consecutive_emphasis = 0

    return findings
