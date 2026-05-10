#!/usr/bin/env python3
"""Run the versioned kairos-wechat-typeset workflow."""

from __future__ import annotations

import argparse
import json
import re
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional, Sequence, Tuple

from render import (
    available_themes,
    load_theme,
    parse_blocks,
    render_markdown_text,
    strip_frontmatter,
)
from verify.markdown_verify import verify_markdown_text


OUTPUT_ROOT = Path.home() / ".wechat-typeset"
HTML_NAME = "output.html"
LAYOUT_NAME = "layout.md"
META_NAME = "meta.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create versioned WeChat typesetting outputs.")
    input_group = parser.add_mutually_exclusive_group(required=False)
    input_group.add_argument("--input", help="Path to source content.")
    input_group.add_argument("--content", help="Source content text.")
    parser.add_argument("--theme", help="Registered built-in theme id.")
    parser.add_argument(
        "--optimize-layout",
        choices=["yes", "no"],
        help="Whether to output layout.md before rendering.",
    )
    parser.add_argument("--title", help="Optional article title override.")
    parser.add_argument("--slug", help="Optional output article slug.")
    parser.add_argument("--output-root", help="Override output root. Defaults to ~/.wechat-typeset.")
    parser.add_argument(
        "--fragment-only",
        action="store_true",
        help="Render only the paste-friendly body fragment.",
    )
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Fail instead of prompting when theme or layout choice is missing.",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List registered themes and exit.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Run a deterministic self-check using a temporary output directory.",
    )
    args = parser.parse_args()
    if not args.list_themes and not args.check and not (args.input or args.content):
        parser.error("one of --input, --content, --check, or --list-themes is required")
    return args


def list_themes() -> None:
    for theme in available_themes():
        suitable = " / ".join(theme.get("suitable_for", []))
        print(f"{theme['id']}\t{theme.get('name_zh', theme['name'])}\t{suitable}")


def prompt_choice(prompt: str, valid: Sequence[str], default: Optional[str] = None) -> str:
    valid_set = set(valid)
    suffix = f" [{default}]" if default else ""
    while True:
        value = input(f"{prompt}{suffix}: ").strip()
        if not value and default:
            return default
        if value in valid_set:
            return value
        print(f"Please choose one of: {', '.join(valid)}", file=sys.stderr)


def source_from_args(args: argparse.Namespace) -> Tuple[str, str, Optional[Path]]:
    if args.input:
        source_path = Path(args.input).expanduser().resolve()
        return source_path.read_text(encoding="utf-8"), "file", source_path
    return str(args.content or ""), "content", None


def looks_like_markdown(text: str) -> bool:
    return bool(
        re.search(
            r"(^#{1,6}\s+|^[-+*]\s+|^\d+[.)]\s+|^>\s+|```|^\|.+\|$|!\[[^\]]*\]\([^)]+\)|\[.+\]\(.+\))",
            text,
            re.MULTILINE,
        )
    )


def minimal_markdown(text: str, title: Optional[str] = None) -> str:
    frontmatter_title, body = strip_frontmatter(text)
    if looks_like_markdown(body):
        return text.strip() + "\n"

    clean_lines = [line.strip() for line in body.splitlines()]
    paragraphs = []
    current = []
    for line in clean_lines:
        if not line:
            if current:
                paragraphs.append(" ".join(current))
                current = []
            continue
        current.append(line)
    if current:
        paragraphs.append(" ".join(current))

    chosen_title = title or frontmatter_title
    output = []
    if chosen_title:
        output.append(f"# {chosen_title.strip()}")
        output.append("")
    output.extend(paragraphs)
    return "\n\n".join(output).strip() + "\n"


def optimized_layout_markdown(markdown: str, title: Optional[str] = None) -> str:
    """Create deterministic layout Markdown without changing article facts."""

    frontmatter_title, body = strip_frontmatter(markdown)
    blocks = parse_blocks(body)
    chosen_title = title or frontmatter_title
    rendered = []
    heading_seen = False
    section_number = 1
    paragraph_run = 0

    for block in blocks:
        block_type = block.get("type")
        if block_type == "heading":
            level = int(block.get("level", 1))
            text = str(block.get("text", "")).strip()
            if level == 1:
                heading_seen = True
                rendered.append(f"# {text}")
            elif level == 2:
                if not re.match(r"^\d{1,2}(?:[.、:：|｜\-\s]+).+", text):
                    text = f"{section_number:02d} {text}"
                    section_number += 1
                rendered.append(f"## {text}")
            else:
                rendered.append(f"### {text}")
            paragraph_run = 0
        elif block_type == "paragraph":
            text = str(block.get("text", "")).strip()
            rendered.append(text)
            paragraph_run += 1
            if paragraph_run >= 3:
                rendered.append("---")
                paragraph_run = 0
        elif block_type == "quote":
            for line in block.get("lines", []):
                rendered.append(f"> {str(line).strip()}")
            paragraph_run = 0
        elif block_type == "list":
            ordered = bool(block.get("ordered"))
            for index, item in enumerate(block.get("items", []), start=1):
                marker = f"{item.get('number') or index}." if ordered else "-"
                rendered.append(f"{marker} {str(item.get('text', '')).strip()}")
            paragraph_run = 0
        elif block_type == "divider":
            rendered.append("---")
            paragraph_run = 0
        elif block_type == "code":
            language = str(block.get("language", ""))
            rendered.append(f"```{language}")
            rendered.append(str(block.get("text", "")))
            rendered.append("```")
            paragraph_run = 0
        elif block_type == "table":
            header = [str(cell).strip() for cell in block.get("header", [])]
            rows = [[str(cell).strip() for cell in row] for row in block.get("rows", [])]
            rendered.append("| " + " | ".join(header) + " |")
            rendered.append("| " + " | ".join(["---"] * len(header)) + " |")
            for row in rows:
                rendered.append("| " + " | ".join(row) + " |")
            paragraph_run = 0

        rendered.append("")

    if chosen_title and not heading_seen:
        rendered.insert(0, "")
        rendered.insert(0, f"# {chosen_title.strip()}")

    return "\n".join(rendered).strip() + "\n"


def title_from_markdown(markdown: str, fallback: str) -> str:
    frontmatter_title, body = strip_frontmatter(markdown)
    if frontmatter_title:
        return frontmatter_title
    for block in parse_blocks(body):
        if block.get("type") == "heading" and int(block.get("level", 1)) == 1:
            return str(block.get("text", fallback)).strip() or fallback
    return fallback


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^\w\u3400-\u9fff-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    return value[:72] or "wechat-article"


def next_version_dir(article_dir: Path) -> Tuple[str, Path]:
    article_dir.mkdir(parents=True, exist_ok=True)
    existing = []
    for path in article_dir.iterdir():
        if path.is_dir() and re.fullmatch(r"v\d{3}", path.name):
            existing.append(int(path.name[1:]))
    version = (max(existing) + 1) if existing else 1
    version_name = f"v{version:03d}"
    version_dir = article_dir / version_name
    version_dir.mkdir()
    return version_name, version_dir


def write_meta(
    path: Path,
    *,
    version: str,
    theme_id: str,
    layout_optimized: bool,
    input_type: str,
    source_path: Optional[Path],
    title: str,
    fragment_only: bool,
) -> None:
    meta: Dict[str, Any] = {
        "version": version,
        "theme": theme_id,
        "layout_optimized": layout_optimized,
        "input_type": input_type,
        "source_path": str(source_path) if source_path else None,
        "title": title,
        "created_at": datetime.now(timezone.utc).astimezone().isoformat(),
        "fragment_only": fragment_only,
        "outputs": {
            "layout_markdown": LAYOUT_NAME if layout_optimized else None,
            "html": HTML_NAME,
        },
    }
    path.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def resolve_layout_choice(args: argparse.Namespace) -> bool:
    if args.optimize_layout:
        return args.optimize_layout == "yes"
    if args.non_interactive:
        raise SystemExit("--optimize-layout is required in --non-interactive mode.")
    return prompt_choice("Optimize article layout? yes/no", ["yes", "no"], "yes") == "yes"


def resolve_theme(args: argparse.Namespace) -> str:
    theme_ids = [theme["id"] for theme in available_themes()]
    if args.theme:
        load_theme(args.theme)
        return args.theme
    if args.non_interactive:
        raise SystemExit("--theme is required in --non-interactive mode.")
    list_themes()
    return prompt_choice("Choose a built-in theme", theme_ids, theme_ids[0])


def main() -> None:
    args = parse_args()
    if args.list_themes:
        list_themes()
        return
    if args.check:
        args.input = str(Path(__file__).resolve().parents[1] / "fixtures" / "theme-flow-check.md")
        args.theme = args.theme or "song"
        args.optimize_layout = args.optimize_layout or "yes"
        args.output_root = args.output_root or str(Path(tempfile.gettempdir()) / "kairos-typeset-check")
        args.slug = args.slug or "theme-flow-check"
        args.non_interactive = True

    source_text, input_type, source_path = source_from_args(args)
    theme_id = resolve_theme(args)
    layout_optimized = resolve_layout_choice(args)

    normalized = minimal_markdown(source_text, title=args.title)
    render_source = optimized_layout_markdown(normalized, title=args.title) if layout_optimized else normalized
    blocks = parse_blocks(strip_frontmatter(render_source)[1])
    findings = verify_markdown_text(strip_frontmatter(render_source)[1], blocks)
    if findings:
        for finding in findings:
            print(f"VERIFY: {finding}", file=sys.stderr)
        raise SystemExit(1)

    title = title_from_markdown(render_source, args.title or (source_path.stem if source_path else "wechat-article"))
    output_root = Path(args.output_root).expanduser() if args.output_root else OUTPUT_ROOT
    article_slug = slugify(args.slug or title)
    version, version_dir = next_version_dir(output_root / article_slug)

    if layout_optimized:
        (version_dir / LAYOUT_NAME).write_text(render_source, encoding="utf-8")

    output_html = version_dir / HTML_NAME
    theme = load_theme(theme_id)
    document = render_markdown_text(
        strip_frontmatter(render_source)[1],
        input_path=source_path or Path(f"{article_slug}.md"),
        title=title,
        frontmatter_title=None,
        theme=theme,
        fragment_only=args.fragment_only,
    )
    output_html.write_text(document, encoding="utf-8")
    write_meta(
        version_dir / META_NAME,
        version=version,
        theme_id=theme_id,
        layout_optimized=layout_optimized,
        input_type=input_type,
        source_path=source_path,
        title=title,
        fragment_only=args.fragment_only,
    )

    print(f"Created {version_dir}")
    if layout_optimized:
        print(f"Layout Markdown: {version_dir / LAYOUT_NAME}")
    print(f"HTML: {output_html}")
    print(f"Meta: {version_dir / META_NAME}")


if __name__ == "__main__":
    main()
