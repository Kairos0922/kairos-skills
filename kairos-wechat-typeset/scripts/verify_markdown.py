#!/usr/bin/env python3
"""Verify Markdown against the kairos-wechat-typeset layout contract."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from render import parse_blocks, strip_frontmatter
from verify.markdown_verify import verify_markdown_text


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify layout Markdown for kairos-wechat-typeset.")
    parser.add_argument("--input", required=True, help="Path to the Markdown file.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    _, markdown = strip_frontmatter(input_path.read_text(encoding="utf-8"))
    blocks = parse_blocks(markdown)
    findings = verify_markdown_text(markdown, blocks)
    if findings:
        for finding in findings:
            print(f"VERIFY: {finding}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Verified Markdown contract: {input_path}")


if __name__ == "__main__":
    main()
