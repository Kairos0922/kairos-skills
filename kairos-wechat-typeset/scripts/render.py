#!/usr/bin/env python3
"""Render Markdown into WeChat-friendly HTML with inline styles only."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


CJK_FONT_STACK = "'Songti SC', 'STSong', 'Noto Serif CJK SC', 'Source Han Serif SC', SimSun, serif"
LATIN_FONT_STACK = "'Baskerville', 'Iowan Old Style', 'Palatino Linotype', 'Book Antiqua', Georgia, 'Times New Roman', serif"
MONO_FONT_STACK = "'SFMono-Regular', Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace"
CONTENT_WIDTH = 640
BODY_STYLE = (
    "margin: 0; padding: 24px 16px 42px 16px; background-color: #f5f0e8; "
    "-webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;"
)
BASE_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 0 auto 22px auto; font-family: {CJK_FONT_STACK}; "
    "font-size: 15.5px; line-height: 1.98; color: #413932; text-align: left; letter-spacing: 0.015em;"
)
TITLE_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 0 auto 34px auto; font-family: {CJK_FONT_STACK}; "
    "font-size: 23px; line-height: 1.6; font-weight: 700; color: #231c17; text-align: left; letter-spacing: 0.035em;"
)
SECTION_NUM_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 40px auto 8px auto; font-family: {LATIN_FONT_STACK}; "
    "font-size: 38px; line-height: 1; font-weight: 400; letter-spacing: 0.1em; color: #d3c6b6; text-align: left;"
)
SECTION_TITLE_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 0 auto 24px auto; font-family: {CJK_FONT_STACK}; "
    "font-size: 15px; line-height: 1.88; font-weight: 700; color: #241d17; text-align: left; "
    "border-bottom: 1px solid #d8ccbe; padding-bottom: 10px; letter-spacing: 0.05em;"
)
SUBTITLE_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 36px auto 22px auto; font-family: {CJK_FONT_STACK}; "
    "font-size: 15px; line-height: 1.88; font-weight: 700; color: #241d17; text-align: left; "
    "border-bottom: 1px solid #dfd4c8; padding-bottom: 10px; letter-spacing: 0.04em;"
)
LIST_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 0 auto 12px auto; font-family: {CJK_FONT_STACK}; "
    "font-size: 15px; line-height: 1.96; color: #403831; text-align: left;"
)
QUOTE_P = (
    f"display: block; padding: 18px 20px 18px 20px; font-family: {CJK_FONT_STACK}; "
    "font-size: 15px; line-height: 1.95; text-align: left; background-color: #f3ede3; "
    "border-left: 3px solid #c8b59f; border-radius: 14px; color: #5b534b;"
)
QUOTE_WRAP_P = f"max-width: {CONTENT_WIDTH}px; margin: 30px auto;"
NOTE_P = QUOTE_P.replace("border-left: 3px solid #c8b59f;", "border-left: 3px solid #b7ad9f;")
TIP_P = QUOTE_P.replace("border-left: 3px solid #c8b59f;", "border-left: 3px solid #07C160;")
WARNING_P = (
    f"display: block; padding: 18px 20px 18px 20px; font-family: {CJK_FONT_STACK}; "
    "font-size: 15px; line-height: 1.95; text-align: left; background-color: #f7efe1; "
    "border-left: 3px solid #c69245; border-radius: 14px; color: #6b5434;"
)
CODE_META_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 34px auto 10px auto; font-family: {LATIN_FONT_STACK}; "
    "font-size: 10.8px; line-height: 1.4; color: #8a8074; text-align: left; letter-spacing: 0.18em;"
)
CODE_P = (
    f"display: block; padding: 18px 20px 18px 20px; font-family: {MONO_FONT_STACK}; "
    "font-size: 12.5px; line-height: 1.86; color: #2f2a25; text-align: left; white-space: pre-wrap; "
    "background-color: #f0e8dc; border: 1px solid #ddd2c2; border-radius: 14px;"
)
CODE_WRAP_P = f"max-width: {CONTENT_WIDTH}px; margin: 0 auto 32px auto;"
TABLE_META_P = (
    f"max-width: {CONTENT_WIDTH}px; margin: 34px auto 12px auto; font-family: {LATIN_FONT_STACK}; "
    "font-size: 11.3px; line-height: 1.4; color: #8a8074; text-align: left; letter-spacing: 0.16em;"
)
TABLE_CARD_P = (
    f"display: block; padding: 17px 20px 17px 20px; font-family: {CJK_FONT_STACK}; "
    "font-size: 15px; line-height: 1.95; color: #403831; text-align: left; background-color: #f3ede3; "
    "border: 1px solid #ddd2c3; border-radius: 14px;"
)
TABLE_WRAP_P = f"max-width: {CONTENT_WIDTH}px; margin: 0 auto 14px auto;"
TABLE_LABEL_STYLE = (
    f"display: block; margin-bottom: 4px; font-family: {LATIN_FONT_STACK}; "
    "font-size: 11.3px; line-height: 1.4; color: #877d72; letter-spacing: 0.14em;"
)
TABLE_VALUE_STYLE = "display: block; margin-bottom: 10px; color: #403831;"

INLINE_CODE_STYLE = (
    f"font-family: {MONO_FONT_STACK}; font-size: 0.9em; background-color: #ece3d7; "
    "color: #2f2c28; padding: 1px 6px; border-radius: 4px;"
)
LINK_STYLE = "color: #23201c; text-decoration: none; border-bottom: 1px solid #cfc3b4;"
STRONG_STYLE = "font-weight: 700; color: #1d1813;"
HIGHLIGHT_STYLE = "border-bottom: 1px dashed #07C160; font-weight: 600;"
EM_STYLE = "font-style: italic; color: #595048;"
STRIKE_STYLE = "text-decoration: line-through; color: #766d63;"
LATIN_INLINE_STYLE = f"font-family: {LATIN_FONT_STACK}; font-size: 0.96em; letter-spacing: 0.02em; color: #322b25;"
LIST_MARKER_STYLE = (
    f"display: inline-block; width: 24px; margin-right: 10px; text-align: center; vertical-align: top; font-family: {LATIN_FONT_STACK}; "
    "font-size: 12px; line-height: 1.96; color: #988c7f;"
)
ORDERED_MARKER_STYLE = (
    f"display: inline-block; width: 24px; margin-right: 10px; text-align: center; vertical-align: top; font-family: {LATIN_FONT_STACK}; "
    "font-size: 12px; line-height: 1.96; color: #938678; letter-spacing: 0.04em;"
)
LIST_CONTENT_STYLE = "display: inline-block; max-width: 88%; vertical-align: top;"

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
UNORDERED_RE = re.compile(r"^(\s*)[-+*]\s+(.*)$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]*)\s*$")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
NUMERIC_SECTION_RE = re.compile(r"^(?P<num>\d{1,2})(?:[.、:：|｜\-\s]+)(?P<title>.+)$")
FULL_STRONG_RE = re.compile(r"^\s*(\*\*|__)(.+?)\1\s*$", re.DOTALL)
NOTE_RE = re.compile(r"^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s*(.*)$", re.IGNORECASE)
LATIN_WORD_RE = r"[A-Za-z0-9]+(?:[A-Za-z0-9./_:+%#@-]*[A-Za-z0-9])?"
LATIN_TEXT_RE = re.compile(rf"{LATIN_WORD_RE}(?: {LATIN_WORD_RE})*")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Markdown into WeChat-friendly HTML.")
    parser.add_argument("--input", required=True, help="Path to the input markdown file.")
    parser.add_argument(
        "--output",
        help="Path to the output HTML file. Defaults to the input path with a .html suffix.",
    )
    parser.add_argument("--title", help="Optional document title override.")
    parser.add_argument(
        "--fragment-only",
        action="store_true",
        help="Output only the body fragment instead of a full HTML document.",
    )
    return parser.parse_args()


def strip_frontmatter(text: str) -> Tuple[Optional[str], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text

    for idx in range(1, len(lines)):
        if lines[idx].strip() != "---":
            continue

        title = None
        for line in lines[1:idx]:
            if ":" not in line:
                continue
            key, value = line.split(":", 1)
            if key.strip() == "title":
                title = value.strip().strip("'\"")
                break

        body = "\n".join(lines[idx + 1 :])
        return title, body

    return None, text


def is_blank(line: str) -> bool:
    return not line.strip()


def is_divider(line: str) -> bool:
    stripped = line.strip()
    return stripped in {"<!--段落分割线-->", "<!-- 段落分割线 -->"} or bool(
        re.fullmatch(r"(-{3,}|\*{3,}|_{3,})", stripped)
    )


def is_table_start(lines: Sequence[str], index: int) -> bool:
    if index + 1 >= len(lines):
        return False
    if "|" not in lines[index]:
        return False
    return bool(TABLE_DIVIDER_RE.match(lines[index + 1]))


def is_block_start(lines: Sequence[str], index: int) -> bool:
    if index >= len(lines):
        return False
    line = lines[index]
    stripped = line.strip()
    if not stripped:
        return False
    return any(
        (
            bool(HEADING_RE.match(line)),
            bool(FENCE_RE.match(stripped)),
            stripped.startswith(">"),
            bool(UNORDERED_RE.match(line)),
            bool(ORDERED_RE.match(line)),
            is_divider(line),
            is_table_start(lines, index),
        )
    )


def split_table_row(line: str) -> List[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def is_cjk(char: str) -> bool:
    return bool(re.match(r"[\u3400-\u9fff]", char))


def should_insert_space(left: str, right: str) -> bool:
    if not left or not right:
        return False
    left_char = left[-1]
    right_char = right[0]
    if is_cjk(left_char) or is_cjk(right_char):
        return False
    if left_char in "([{<\"'“‘《【":
        return False
    if right_char in ".,!?;:%)]}>\"'”’》】、，。！？；：":
        return False
    return True


def merge_lines(lines: Sequence[str]) -> str:
    if not lines:
        return ""

    merged = lines[0].strip()
    for previous, current in zip(lines, lines[1:]):
        current_text = current.strip()
        if previous.endswith("  ") or previous.rstrip().endswith("\\"):
            merged += "\n" + current_text
            continue
        if should_insert_space(merged, current_text):
            merged += " " + current_text
        else:
            merged += current_text
    return merged


def parse_blocks(markdown: str) -> List[Dict[str, Any]]:
    lines = markdown.splitlines()
    blocks: List[Dict[str, Any]] = []
    index = 0

    while index < len(lines):
        line = lines[index]
        if is_blank(line):
            index += 1
            continue

        if is_divider(line):
            blocks.append({"type": "divider"})
            index += 1
            continue

        heading_match = HEADING_RE.match(line)
        if heading_match:
            blocks.append(
                {
                    "type": "heading",
                    "level": len(heading_match.group(1)),
                    "text": heading_match.group(2).strip(),
                }
            )
            index += 1
            continue

        fence_match = FENCE_RE.match(line.strip())
        if fence_match:
            language = fence_match.group(1) or ""
            index += 1
            code_lines: List[str] = []
            while index < len(lines) and not FENCE_RE.match(lines[index].strip()):
                code_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            blocks.append({"type": "code", "language": language, "text": "\n".join(code_lines)})
            continue

        if line.strip().startswith(">"):
            quote_lines: List[str] = []
            while index < len(lines) and lines[index].strip().startswith(">"):
                quote_lines.append(re.sub(r"^\s*>\s?", "", lines[index]))
                index += 1
            blocks.append({"type": "quote", "lines": quote_lines})
            continue

        if is_table_start(lines, index):
            header = split_table_row(lines[index])
            index += 2
            rows: List[List[str]] = []
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                rows.append(split_table_row(lines[index]))
                index += 1
            blocks.append({"type": "table", "header": header, "rows": rows})
            continue

        unordered_match = UNORDERED_RE.match(line)
        ordered_match = ORDERED_RE.match(line)
        if unordered_match or ordered_match:
            ordered = bool(ordered_match)
            marker_indent = len((ordered_match or unordered_match).group(1))
            items: List[Dict[str, Any]] = []
            while index < len(lines):
                current = lines[index]
                current_match = ORDERED_RE.match(current) if ordered else UNORDERED_RE.match(current)
                if not current_match:
                    break

                number = current_match.group(2) if ordered else None
                content = [current_match.group(3) if ordered else current_match.group(2)]
                index += 1
                while index < len(lines):
                    if is_blank(lines[index]):
                        break
                    if (ORDERED_RE.match(lines[index]) if ordered else UNORDERED_RE.match(lines[index])):
                        break
                    if is_block_start(lines, index):
                        break
                    current_indent = len(lines[index]) - len(lines[index].lstrip(" "))
                    if current_indent > marker_indent:
                        content.append(lines[index].strip())
                        index += 1
                        continue
                    break
                items.append({"number": number, "text": merge_lines(content)})

                if index < len(lines) and is_blank(lines[index]):
                    break

            blocks.append({"type": "list", "ordered": ordered, "items": items})
            continue

        paragraph_lines = [line]
        index += 1
        while index < len(lines) and not is_blank(lines[index]) and not is_block_start(lines, index):
            paragraph_lines.append(lines[index])
            index += 1
        blocks.append({"type": "paragraph", "text": merge_lines(paragraph_lines)})

    return blocks


def placeholder_token(index: int) -> str:
    return chr(0xE000 + index)


def render_image(alt_text: str, source: str) -> str:
    safe_alt = html.escape(alt_text.strip())
    safe_source = html.escape(source.strip(), quote=True)
    image_html = (
        f'<img src="{safe_source}" alt="{safe_alt}" '
        'style="display: block; max-width: 100%; height: auto; margin: 14px auto; border-radius: 8px;" />'
    )
    if safe_alt:
        image_html += (
            f'<span style="display: block; width: 88%; margin: 12px auto 0 auto; padding-top: 9px; '
            f'border-top: 1px solid #e3d9cc; font-size: 13px; line-height: 1.72; color: #877c70; '
            f'text-align: center; letter-spacing: 0.03em; font-family: {CJK_FONT_STACK};">{balance_serif_text(safe_alt)}</span>'
        )
    return image_html


def render_link(label: str, target: str) -> str:
    safe_target = html.escape(target.strip(), quote=True)
    return f'<a href="{safe_target}" style="{LINK_STYLE}">{render_inline(label)}</a>'


def apply_recursive_pattern(
    text: str, pattern: re.Pattern[str], repl: Any, recursive: bool = True
) -> str:
    while True:
        def replace(match: re.Match[str]) -> str:
            inner = match.group(1)
            return repl(render_inline(inner) if recursive else inner)

        updated, count = pattern.subn(replace, text)
        text = updated
        if count == 0:
            return text


def balance_serif_text(fragment: str) -> str:
    # Only wrap plain text segments so we do not disturb existing tags or HTML entities.
    segments = re.split(r"(<[^>]+>|&[A-Za-z0-9#]+;)", fragment)
    balanced: List[str] = []
    for segment in segments:
        if not segment:
            continue
        if segment.startswith("<") and segment.endswith(">"):
            balanced.append(segment)
            continue
        if segment.startswith("&") and segment.endswith(";"):
            balanced.append(segment)
            continue
        balanced.append(
            LATIN_TEXT_RE.sub(
                lambda match: f'<span style="{LATIN_INLINE_STYLE}">{match.group(0)}</span>',
                segment,
            )
        )
    return "".join(balanced)


def render_inline(text: str) -> str:
    placeholders: List[str] = []

    def stash(fragment: str) -> str:
        token = placeholder_token(len(placeholders))
        placeholders.append(fragment)
        return token

    working = text
    working = re.sub(
        r"`([^`]+)`",
        lambda match: stash(
            f'<span style="{INLINE_CODE_STYLE}">{html.escape(match.group(1))}</span>'
        ),
        working,
    )
    working = re.sub(
        r"!\[([^\]]*)\]\(([^)]+)\)",
        lambda match: stash(render_image(match.group(1), match.group(2))),
        working,
    )
    working = re.sub(
        r"\[([^\]]+)\]\(([^)]+)\)",
        lambda match: stash(render_link(match.group(1), match.group(2))),
        working,
    )

    escaped = html.escape(working).replace("\n", "<br>")
    escaped = apply_recursive_pattern(
        escaped,
        re.compile(r"==(.+?)==", re.DOTALL),
        lambda inner: f'<span style="{HIGHLIGHT_STYLE}">{inner}</span>',
    )
    escaped = apply_recursive_pattern(
        escaped,
        re.compile(r"(?:\*\*|__)(.+?)(?:\*\*|__)", re.DOTALL),
        lambda inner: f'<span style="{STRONG_STYLE}">{inner}</span>',
    )
    escaped = apply_recursive_pattern(
        escaped,
        re.compile(r"~~(.+?)~~", re.DOTALL),
        lambda inner: f'<span style="{STRIKE_STYLE}">{inner}</span>',
    )
    escaped = apply_recursive_pattern(
        escaped,
        re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.DOTALL),
        lambda inner: f'<span style="{EM_STYLE}">{inner}</span>',
    )
    escaped = apply_recursive_pattern(
        escaped,
        re.compile(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", re.DOTALL),
        lambda inner: f'<span style="{EM_STYLE}">{inner}</span>',
    )
    escaped = balance_serif_text(escaped)

    for index, fragment in enumerate(placeholders):
        escaped = escaped.replace(placeholder_token(index), fragment)
    return escaped


def paragraph_style(extra: str = "") -> str:
    return BASE_P if not extra else f"{BASE_P} {extra}"


def render_paragraph(text: str) -> str:
    strong_match = FULL_STRONG_RE.match(text)
    if strong_match:
        content = render_inline(strong_match.group(2).strip())
        return f'<p style="{paragraph_style("font-weight: 700; color: #000; letter-spacing: 0.02em;")}">{content}</p>'
    return f'<p style="{BASE_P}">{render_inline(text)}</p>'


def render_heading(level: int, text: str) -> List[str]:
    stripped = text.strip()
    if level == 1:
        return [
            (
                f'<p style="{TITLE_TOPLINE_P}"><span style="display: inline-block; width: 48px; '
                'border-top: 1px solid #d9cec0;"></span></p>'
            ),
            f'<p style="{TITLE_P}">{render_inline(stripped)}</p>',
        ]

    numeric_match = NUMERIC_SECTION_RE.match(stripped)
    if numeric_match:
        number = numeric_match.group("num").zfill(2)
        title = numeric_match.group("title").strip()
        return [
            f'<p style="{SECTION_NUM_P}">{html.escape(number)}</p>',
            f'<p style="{SECTION_TITLE_P}">{render_inline(title)}</p>',
        ]

    return [f'<p style="{SUBTITLE_P}">{render_inline(stripped)}</p>']


def render_quote(lines: Sequence[str]) -> str:
    cleaned = [line for line in lines if line.strip()]
    quote_kind = "QUOTE"
    style = QUOTE_P

    if cleaned:
        kind_match = NOTE_RE.match(cleaned[0].strip())
        if kind_match:
            quote_kind = kind_match.group(1).upper()
            remainder = kind_match.group(2).strip()
            cleaned = cleaned[1:]
            if remainder:
                cleaned.insert(0, remainder)

    if quote_kind in {"NOTE", "IMPORTANT", "CAUTION"}:
        style = NOTE_P
    elif quote_kind == "TIP":
        style = TIP_P
    elif quote_kind == "WARNING":
        style = WARNING_P

    text = merge_lines(cleaned)
    return f'<p style="{QUOTE_WRAP_P}"><span style="{style}">{render_inline(text)}</span></p>'


def render_list(items: Sequence[Dict[str, Any]], ordered: bool) -> List[str]:
    rendered = []
    for item in items:
        marker = f"{item['number']}." if ordered else "•"
        content = render_inline(item["text"])
        marker_style = ORDERED_MARKER_STYLE if ordered else LIST_MARKER_STYLE
        rendered.append(
            f'<p style="{LIST_P}"><span style="{marker_style}">{html.escape(marker)}</span>{content}</p>'
        )
    return rendered


def render_code(text: str, language: str) -> List[str]:
    label = html.escape(language.upper() if language else "CODE")
    return [
        (
            f'<p style="{CODE_META_P}"><span style="display: inline-block; width: 28px; '
            f'border-top: 1px solid #cfc3b4; margin: 0 10px 4px 0;"></span>{label}</p>'
        ),
        f'<p style="{CODE_WRAP_P}"><span style="{CODE_P}">{html.escape(text)}</span></p>',
    ]


def render_table(header: Sequence[str], rows: Sequence[Sequence[str]]) -> List[str]:
    rendered = [
        (
            f'<p style="{TABLE_META_P}"><span style="display: inline-block; width: 28px; '
            f'border-top: 1px solid #cfc3b4; margin: 0 10px 4px 0;"></span>'
            f'{" × ".join(render_inline(cell) for cell in header)}</p>'
        )
    ]
    for row in rows:
        pairs: List[str] = []
        for index, cell in enumerate(row):
            label = header[index] if index < len(header) else f"Column {index + 1}"
            value_style = TABLE_VALUE_STYLE if index < len(row) - 1 else "display: block; color: #36322d;"
            pairs.append(f'<span style="{TABLE_LABEL_STYLE}">{render_inline(label)}</span>')
            pairs.append(f'<span style="{value_style}">{render_inline(cell)}</span>')
        rendered.append(f'<p style="{TABLE_WRAP_P}"><span style="{TABLE_CARD_P}">{"".join(pairs)}</span></p>')
    return rendered


def render_divider() -> str:
    return (
        f'<p style="max-width: {CONTENT_WIDTH}px; margin: 42px auto 38px auto; text-align: center; line-height: 1;">'
        '<span style="display: inline-block; width: 54px; border-top: 1px solid #ddd2c4; vertical-align: middle;"></span>'
        '<span style="display: inline-block; margin: 0 12px; font-family: \'Iowan Old Style\', Baskerville, \'Palatino Linotype\', \'Book Antiqua\', Georgia, \'Times New Roman\', serif; '
        'font-size: 10px; line-height: 1; color: #c3b7a8; letter-spacing: 0.28em; vertical-align: middle;">··</span>'
        '<span style="display: inline-block; width: 54px; border-top: 1px solid #ddd2c4; vertical-align: middle;"></span>'
        "</p>"
    )


def render_blocks(blocks: Sequence[Dict[str, Any]]) -> str:
    rendered: List[str] = []
    for block in blocks:
        block_type = block["type"]
        if block_type == "heading":
            rendered.extend(render_heading(block["level"], block["text"]))
        elif block_type == "paragraph":
            rendered.append(render_paragraph(block["text"]))
        elif block_type == "quote":
            rendered.append(render_quote(block["lines"]))
        elif block_type == "list":
            rendered.extend(render_list(block["items"], block["ordered"]))
        elif block_type == "code":
            rendered.extend(render_code(block["text"], block["language"]))
        elif block_type == "table":
            rendered.extend(render_table(block["header"], block["rows"]))
        elif block_type == "divider":
            rendered.append(render_divider())
    return "\n".join(rendered).strip() + "\n"


def choose_title(
    explicit_title: Optional[str], frontmatter_title: Optional[str], blocks: Sequence[Dict[str, Any]], input_path: Path
) -> str:
    if explicit_title:
        return explicit_title
    if frontmatter_title:
        return frontmatter_title
    for block in blocks:
        if block["type"] == "heading" and block["level"] == 1:
            return block["text"]
    return input_path.stem


def wrap_document(title: str, fragment: str) -> str:
    safe_title = html.escape(title)
    return (
        "<!DOCTYPE html>\n"
        '<html lang="zh-CN">\n'
        "<head>\n"
        '  <meta charset="UTF-8" />\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        f"  <title>{safe_title}</title>\n"
        "</head>\n"
        f'<body style="{BODY_STYLE}">\n'
        f"{fragment}"
        "</body>\n"
        "</html>\n"
    )


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_suffix(".html")
    )

    frontmatter_title, markdown = strip_frontmatter(input_path.read_text(encoding="utf-8"))
    blocks = parse_blocks(markdown)
    fragment = render_blocks(blocks)
    title = choose_title(args.title, frontmatter_title, blocks, input_path)
    document = fragment if args.fragment_only else wrap_document(title, fragment)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    print(f"Rendered {input_path} -> {output_path}")


if __name__ == "__main__":
    main()
