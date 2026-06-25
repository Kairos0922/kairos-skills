"""Markdown block parser.

Splits Markdown text (with Kairos ``:::`` container syntax) into a list of
typed block dicts consumed by the renderer. Pure parsing — no theme access,
no HTML emission. Depends only on the shared regex vocabulary in
``renderer._tokens``.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Sequence, Tuple

from renderer._tokens import (
    COMPONENT_CLOSE_RE,
    COMPONENT_OPEN_RE,
    FENCE_RE,
    FIGURE_IMAGE_RE,
    HEADING_RE,
    ORDERED_RE,
    SUPPORTED_COMPONENTS,
    TABLE_DIVIDER_RE,
    UNORDERED_RE,
)


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


def split_table_row(line: str) -> List[str]:
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


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
            bool(COMPONENT_OPEN_RE.match(stripped)),
            bool(HEADING_RE.match(line)),
            bool(FENCE_RE.match(stripped)),
            stripped.startswith(">"),
            bool(UNORDERED_RE.match(line)),
            bool(ORDERED_RE.match(line)),
            is_divider(line),
            is_table_start(lines, index),
        )
    )


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


def parse_component_payload(name: str, lines: Sequence[str]) -> Dict[str, Any]:
    if name not in SUPPORTED_COMPONENTS:
        return {
            "type": "unknown_component",
            "name": name,
            "text": merge_lines([f":::{name}", *lines, ":::"]),
        }

    cleaned = [line.rstrip() for line in lines]
    if name == "figure":
        image_alt = ""
        source = ""
        caption_lines: List[str] = []
        for line in cleaned:
            stripped = line.strip()
            if not stripped:
                continue
            image_match = FIGURE_IMAGE_RE.match(stripped)
            if image_match and not source:
                image_alt = image_match.group(1).strip()
                source = image_match.group(2).strip()
            else:
                caption_lines.append(stripped)
        if not source:
            return {"type": "paragraph", "text": merge_lines(cleaned)}
        caption = merge_lines(caption_lines) if caption_lines else image_alt
        return {
            "type": "component",
            "name": name,
            "source": source,
            "alt": image_alt,
            "caption": caption,
        }

    if name == "soft-list":
        items = []
        for line in cleaned:
            item_match = UNORDERED_RE.match(line)
            if item_match:
                items.append({"text": item_match.group(2).strip()})
            elif line.strip() and items:
                items[-1]["text"] = merge_lines([items[-1]["text"], line.strip()])
            elif line.strip():
                items.append({"text": line.strip()})
        return {"type": "component", "name": name, "items": items}

    return {"type": "component", "name": name, "text": merge_lines(cleaned)}


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

        component_match = COMPONENT_OPEN_RE.match(line.strip())
        if component_match:
            name = component_match.group(1).lower()
            index += 1
            component_lines: List[str] = []
            while index < len(lines) and not COMPONENT_CLOSE_RE.match(lines[index].strip()):
                component_lines.append(lines[index])
                index += 1
            if index < len(lines):
                index += 1
            blocks.append(parse_component_payload(name, component_lines))
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
