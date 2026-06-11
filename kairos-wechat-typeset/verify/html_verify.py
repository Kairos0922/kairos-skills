"""HTML verification for WeChat paste compatibility."""

from __future__ import annotations

import re
from typing import List


def verify_html(document: str, fragment_only: bool = False, allow_web_fonts: bool = False) -> List[str]:
    findings: List[str] = []
    lowered = document.lower()

    forbidden_patterns = {
        " class=": "Output must not contain class attributes.",
        "<link": "Output must not contain external stylesheet links.",
        "<section": "Output must not contain section tags.",
        "<div": "Output must not contain div tags.",
        "<ul": "Output must not contain native ul tags.",
        "<ol": "Output must not contain native ol tags.",
        "<table": "Output must not contain native table tags.",
        "<script": "Output must not contain scripts.",
    }
    if not allow_web_fonts:
        forbidden_patterns["<style"] = "Output must not contain <style> blocks."

    for pattern, message in forbidden_patterns.items():
        if pattern in lowered:
            findings.append(message)

    if not fragment_only and '<body style="' not in lowered:
        findings.append("Full HTML output must include an inline body style.")

    for tag in ("p", "span", "a"):
        for match in re.finditer(rf"<{tag}\b(?![^>]*\bstyle=)", document, re.IGNORECASE):
            findings.append(f"<{tag}> at byte {match.start()} is missing an inline style.")
            break

    for match in re.finditer(r"<img\b([^>]*)>", document, re.IGNORECASE):
        attrs = match.group(1)
        if "style=" not in attrs:
            findings.append(f"<img> at byte {match.start()} is missing an inline style.")
            continue
        if "max-width: 100%" not in attrs:
            findings.append(f"<img> at byte {match.start()} is missing max-width: 100%.")

    if "overflow-x" in lowered:
        findings.append("Do not rely on overflow-x fixes; adjust inline component sizing instead.")

    return findings

