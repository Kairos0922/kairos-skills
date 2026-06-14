#!/usr/bin/env python3
"""Verify the consulting visual design-system reference stays internally usable."""

from __future__ import annotations

import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DESIGN_SYSTEM = ROOT / "references" / "design_system.md"
SKILL = ROOT / "SKILL.md"

REQUIRED_THEME_PRESETS = {
    "Ink Classic",
    "Indigo Porcelain",
    "Forest Ink",
    "Kraft Paper",
    "Dune",
    "Midnight Ink",
    "Graphite Red",
    "Olive Editorial",
    "IKB",
    "Lemon",
    "Lemon Green",
    "Safety Orange",
}

REQUIRED_RATIOS = {"4:5", "3:4", "1:1", "5:2", "16:9", "2.35:1", "9:16", "4:3"}

REQUIRED_LAYOUTS = {
    "E01 Hero Thesis",
    "E02 Magazine Feature",
    "E03 Split Tension",
    "S01 Swiss Mechanism",
    "S02 Flow Ribbon",
    "S03 Matrix Spotlight",
    "S04 KPI Editorial",
    "S05 Executive Ladder",
    "S06 Architecture Stack",
    "S07 Annotated Field",
    "S08 Evidence Ladder",
}

REQUIRED_TOKENS = {"display", "headline", "section", "body", "caption"}


def find_missing(required: set[str], text: str) -> list[str]:
    return sorted(item for item in required if item not in text)


def main() -> int:
    design_text = DESIGN_SYSTEM.read_text(encoding="utf-8")
    skill_text = SKILL.read_text(encoding="utf-8")
    errors: list[str] = []

    for label, required in (
        ("theme preset", REQUIRED_THEME_PRESETS),
        ("ratio", REQUIRED_RATIOS),
        ("layout skeleton", REQUIRED_LAYOUTS),
        ("type token", REQUIRED_TOKENS),
    ):
        missing = find_missing(required, design_text)
        if missing:
            errors.append(f"Missing {label}s in design_system.md: {', '.join(missing)}")

    css_vars = {
        "--ink",
        "--paper",
        "--muted",
        "--accent",
        "--line",
        "--font-display-zh",
        "--font-text-zh",
        "--font-en",
        "--font-serif",
    }
    missing_vars = find_missing(css_vars, design_text)
    if missing_vars:
        errors.append(f"Missing CSS variables in design_system.md: {', '.join(missing_vars)}")

    skill_presets = set(re.findall(r"`([^`]+)`", skill_text))
    referenced_presets = skill_presets & REQUIRED_THEME_PRESETS
    missing_in_design = find_missing(referenced_presets, design_text)
    if missing_in_design:
        errors.append(f"SKILL.md references presets not defined in design_system.md: {', '.join(missing_in_design)}")

    qa_terms = (
        "PNG",
        "no text is clipped",
        "thumbnail test",
        "squint test",
        "content_density",
        "content atoms",
        "text exclusion zone",
        "too empty for an infographic",
        "Swiss Sans",
        "Editorial Serif",
        "font-weight: 700",
    )
    missing_qa = find_missing(set(qa_terms), design_text)
    if missing_qa:
        errors.append(f"Missing render QA terms in design_system.md: {', '.join(missing_qa)}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1

    print("Design system verification passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
