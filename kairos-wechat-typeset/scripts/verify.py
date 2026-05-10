#!/usr/bin/env python3
"""Verify generated WeChat HTML output for inline-style constraints."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from render import load_theme, parse_blocks, strip_frontmatter, verify_html
from verify.editorial_verify import verify_editorial_blocks


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify kairos-wechat-typeset HTML output.")
    parser.add_argument("--input", required=True, help="Path to the generated HTML file.")
    parser.add_argument(
        "--fragment-only",
        action="store_true",
        help="Verify a body fragment rather than a full HTML document.",
    )
    parser.add_argument("--source", help="Optional source Markdown path for editorial verification.")
    parser.add_argument("--theme", help="Registered theme id for editorial verification.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    document = input_path.read_text(encoding="utf-8")
    findings = verify_html(document, args.fragment_only)
    if args.source or args.theme:
        if not args.source or not args.theme:
            findings.append("Editorial verification requires both --source and --theme.")
        else:
            source_path = Path(args.source).expanduser().resolve()
            theme = load_theme(args.theme)
            _, markdown = strip_frontmatter(source_path.read_text(encoding="utf-8"))
            blocks = parse_blocks(markdown)
            findings.extend(verify_editorial_blocks(blocks, theme))
    if findings:
        for finding in findings:
            print(f"VERIFY: {finding}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Verified {input_path}")


if __name__ == "__main__":
    main()
