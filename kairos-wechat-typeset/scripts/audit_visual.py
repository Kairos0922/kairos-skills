#!/usr/bin/env python3
"""Summarize visual style inventory for rendered WeChat HTML."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Iterable, List


STYLE_RE = re.compile(r'\bstyle="([^"]*)"', re.IGNORECASE)
DECL_RE = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;]+)")
PX_RE = re.compile(r"(-?\d+(?:\.\d+)?)px")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit rendered HTML visual style inventory.")
    parser.add_argument("--input", required=True, help="Rendered HTML file to inspect.")
    parser.add_argument(
        "--allowed-font-size",
        action="append",
        default=[],
        help="Allowed font-size value. Repeat for multiple values, e.g. 16px and 18px.",
    )
    parser.add_argument(
        "--max-margin-px",
        type=float,
        help="Fail if any margin shorthand contains a px value above this number.",
    )
    parser.add_argument(
        "--max-border-count",
        type=int,
        help="Fail if non-zero border declarations exceed this count.",
    )
    return parser.parse_args()


def style_declarations(document: str) -> Iterable[tuple[str, str]]:
    for style_match in STYLE_RE.finditer(document):
        for name, value in DECL_RE.findall(style_match.group(1)):
            yield name.strip().lower(), value.strip()


def px_values(value: str) -> List[float]:
    return [float(match.group(1)) for match in PX_RE.finditer(value)]


def is_visible_border(value: str) -> bool:
    normalized = value.strip().lower()
    return not (
        normalized.startswith("0")
        or normalized == "none"
        or normalized.startswith("transparent")
    )


def is_border_property(name: str) -> bool:
    return name == "border" or name in {
        "border-top",
        "border-right",
        "border-bottom",
        "border-left",
    }


def format_counter(counter: Counter[str]) -> str:
    if not counter:
        return "  (none)"
    return "\n".join(f"  {value}: {count}" for value, count in sorted(counter.items()))


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    document = input_path.read_text(encoding="utf-8")

    font_sizes: Counter[str] = Counter()
    background_colors: Counter[str] = Counter()
    borders: Counter[str] = Counter()
    margin_values: List[tuple[str, float]] = []

    for name, value in style_declarations(document):
        if name == "font-size":
            font_sizes[value] += 1
        elif name == "background-color":
            background_colors[value] += 1
        elif is_border_property(name) and is_visible_border(value):
            borders[name] += 1
        elif name == "margin":
            for px_value in px_values(value):
                margin_values.append((value, px_value))

    max_margin = max((px_value for _, px_value in margin_values), default=0.0)
    visible_border_count = sum(borders.values())

    findings: List[str] = []
    allowed = set(args.allowed_font_size)
    if allowed:
        unexpected = sorted(set(font_sizes) - allowed)
        if unexpected:
            findings.append(f"Unexpected font-size values: {', '.join(unexpected)}")

    if args.max_margin_px is not None:
        too_large = sorted({value for value, px_value in margin_values if px_value > args.max_margin_px})
        if too_large:
            findings.append(
                f"Margins exceed {args.max_margin_px:g}px: " + "; ".join(too_large[:8])
            )

    if args.max_border_count is not None and visible_border_count > args.max_border_count:
        findings.append(
            f"Visible border declarations: {visible_border_count}; maximum is {args.max_border_count}."
        )

    print(f"Visual audit: {input_path}")
    print("Font sizes:")
    print(format_counter(font_sizes))
    print(f"Max margin px: {max_margin:g}")
    print(f"Visible border declarations: {visible_border_count}")
    print("Border declarations:")
    print(format_counter(borders))
    print("Background colors:")
    print(format_counter(background_colors))

    if findings:
        for finding in findings:
            print(f"AUDIT: {finding}", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
