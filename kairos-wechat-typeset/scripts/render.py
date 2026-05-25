#!/usr/bin/env python3
"""Render Markdown into theme-driven, WeChat-friendly HTML with inline styles only."""

from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple


SKILL_ROOT = Path(__file__).resolve().parents[1]
THEMES_ROOT = SKILL_ROOT / "themes"
REGISTRY_PATH = THEMES_ROOT / "registry.json"

if str(SKILL_ROOT) not in sys.path:
    sys.path.insert(0, str(SKILL_ROOT))

from art_direction.mood import select_art_direction
from art_direction.rhythm import build_rhythm_plan
from renderer.blocks import ALLOWED_KAIROS_COMPONENTS
from renderer.compiler import compile_plan
from semantic.analyze import analyze_blocks
from verify.editorial_verify import verify_editorial_blocks
from verify.html_verify import verify_html
from verify.markdown_verify import verify_markdown_safety

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
UNORDERED_RE = re.compile(r"^(\s*)[-+*]\s+(.*)$")
ORDERED_RE = re.compile(r"^(\s*)(\d+)[.)]\s+(.*)$")
TASK_ITEM_RE = re.compile(r"^\[(?P<mark>[ xX])\]\s+(?P<text>.+)$")
FENCE_RE = re.compile(r"^```([A-Za-z0-9_+-]*)\s*$")
TABLE_DIVIDER_RE = re.compile(r"^\s*\|?(?:\s*:?-{3,}:?\s*\|)+\s*:?-{3,}:?\s*\|?\s*$")
NUMERIC_SECTION_RE = re.compile(r"^(?P<num>\d{1,2})(?:[.、:：|｜\-\s]+)(?P<title>.+)$")
FULL_STRONG_RE = re.compile(r"^\s*(\*\*|__)(.+?)\1\s*$", re.DOTALL)
NOTE_RE = re.compile(r"^\[!(NOTE|TIP|WARNING|IMPORTANT|CAUTION)\]\s*(.*)$", re.IGNORECASE)
LATIN_WORD_RE = r"[A-Za-z0-9]+(?:[A-Za-z0-9./_:+%#@-]*[A-Za-z0-9])?"
COMPONENT_OPEN_RE = re.compile(r"^:::\s*([A-Za-z][A-Za-z0-9_-]*)\s*$")
COMPONENT_CLOSE_RE = re.compile(r"^:::\s*$")
FIGURE_IMAGE_RE = re.compile(r"^!\[([^\]]*)\]\(([^)]+)\)\s*$")
SUPPORTED_COMPONENTS = ALLOWED_KAIROS_COMPONENTS
CHINESE_NUMERALS = {
    "01": "一",
    "02": "二",
    "03": "三",
    "04": "四",
    "05": "五",
    "06": "六",
    "07": "七",
    "08": "八",
    "09": "九",
    "10": "十",
}


def load_registry() -> Dict[str, Any]:
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Theme registry not found: {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def available_themes() -> List[Dict[str, Any]]:
    return list(load_registry().get("themes", []))


def default_theme_id() -> str:
    registry = load_registry()
    return str(registry.get("default") or "song")


def load_theme(theme_id: str) -> Dict[str, Any]:
    registry = load_registry()
    themes = {theme["id"]: theme for theme in registry.get("themes", [])}
    if theme_id not in themes:
        valid = ", ".join(sorted(themes))
        raise ValueError(f"Unknown theme '{theme_id}'. Available themes: {valid}")

    theme_path = THEMES_ROOT / themes[theme_id]["path"]
    if not theme_path.exists():
        raise FileNotFoundError(f"Registered theme file not found: {theme_path}")
    theme = json.loads(theme_path.read_text(encoding="utf-8"))
    if theme.get("id") != theme_id:
        raise ValueError(f"Theme id mismatch in {theme_path}: expected {theme_id}")
    return theme


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render Markdown into theme-driven WeChat HTML.")
    parser.add_argument("--input", help="Path to the input markdown file.")
    parser.add_argument(
        "--output",
        help="Path to the output HTML file. Defaults to the input path with a .html suffix.",
    )
    parser.add_argument("--title", help="Optional document title override.")
    parser.add_argument(
        "--theme",
        default=default_theme_id(),
        help="Registered theme id. Use --list-themes to see available themes.",
    )
    parser.add_argument(
        "--list-themes",
        action="store_true",
        help="List registered themes and exit.",
    )
    parser.add_argument(
        "--fragment-only",
        action="store_true",
        help="Output only the body fragment instead of a full HTML document.",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="Verify the generated HTML for WeChat inline-style constraints.",
    )
    parser.add_argument("--article-type", help=argparse.SUPPRESS)
    parser.add_argument("--density", choices=["low", "medium", "high"], help=argparse.SUPPRESS)
    parser.add_argument("--tone", help=argparse.SUPPRESS)
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


def spacing_from_layout(layout: Optional[Dict[str, Any]], fallback_bottom: int) -> Dict[str, int]:
    if not layout:
        return {"top": 0, "bottom": fallback_bottom}
    return {
        "top": int(layout.get("spacing_top", 0)),
        "bottom": int(layout.get("spacing_bottom", fallback_bottom)),
    }


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


def placeholder_token(index: int) -> str:
    return chr(0xE000 + index)


class Renderer:
    def __init__(self, theme: Dict[str, Any], plans: Optional[Sequence[Dict[str, Any]]] = None):
        self.theme = theme
        self.theme_id = str(theme.get("id", ""))
        self.width = int(theme.get("content_width", 640))
        self.fonts = theme["fonts"]
        self.colors = theme["colors"]
        self.typography = theme["typography"]
        self.shape = theme["shape"]
        self.plans = list(plans or [])
        self.latin_text_re = re.compile(rf"{LATIN_WORD_RE}(?: {LATIN_WORD_RE})*")

    def c(self, key: str) -> str:
        return self.colors[key]

    def f(self, key: str) -> str:
        return self.fonts[key]

    def t(self, key: str) -> str:
        return self.typography[key]

    def rhythm(self, key: str, fallback: int) -> int:
        value = self.theme.get("rhythm", {}).get(key, fallback)
        if isinstance(value, (int, float)):
            return int(round(value))
        if isinstance(value, str) and value.endswith("px"):
            try:
                return int(round(float(value[:-2])))
            except ValueError:
                return fallback
        return fallback

    def margin(self, top: int, bottom: int) -> str:
        return f"{top}px auto {bottom}px auto"

    def chinese_section_label(self, number: str) -> str:
        return CHINESE_NUMERALS.get(number.zfill(2), number)

    def radius(self, key: str = "radius") -> str:
        return self.shape[key]

    def is_theme(self, theme_id: str) -> bool:
        return self.theme_id == theme_id

    def body_style(self) -> str:
        body = self.theme["body"]
        return (
            f"margin: 0; padding: {body['padding']}; background-color: {body['background']}; "
            "-webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;"
        )

    def base_p(self, spacing: Optional[Dict[str, int]] = None) -> str:
        spacing = spacing or {"top": 0, "bottom": self.rhythm("paragraph_gap", 22)}
        return (
            f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; font-family: {self.f('cjk')}; "
            f"font-size: {self.t('body_size')}; line-height: {self.t('body_line')}; color: {self.c('text')}; "
            "text-align: left; letter-spacing: 0;"
        )

    def title_p(self, spacing: Optional[Dict[str, int]] = None) -> str:
        spacing = spacing or {"top": 0, "bottom": 34}
        if self.is_theme("song"):
            return (
                f"max-width: {self.width}px; margin: {self.margin(spacing['top'], max(spacing['bottom'], 24))}; "
                f"padding: 0; font-family: {self.f('cjk')}; font-size: {self.t('title_size')}; "
                f"line-height: {self.t('title_line')}; font-weight: 700; color: {self.c('ink')}; "
                "text-align: left; letter-spacing: 0;"
            )
        return (
            f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; font-family: {self.f('cjk')}; "
            f"font-size: {self.t('title_size')}; line-height: {self.t('title_line')}; font-weight: 700; "
            f"color: {self.c('ink')}; text-align: left; letter-spacing: 0;"
        )

    def section_num_p(self, top: int) -> str:
        if self.is_theme("song"):
            return (
                f"max-width: {self.width}px; margin: {top}px auto 8px auto; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('section_num_size')}; line-height: 1.6; font-weight: 700; "
                f"letter-spacing: 0; color: {self.c('ink')}; text-align: left;"
            )
        return (
            f"max-width: {self.width}px; margin: {top}px auto 8px auto; font-family: {self.f('latin')}; "
            f"font-size: {self.t('section_num_size')}; line-height: 1; font-weight: 500; "
            f"letter-spacing: 0.08em; color: {self.c('soft')}; text-align: left;"
        )

    def section_title_p(self, bottom: int) -> str:
        if self.is_theme("song"):
            return (
                f"display: inline; padding: 0; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('section_title_size')}; line-height: 1.72; "
                "font-weight: 700; color: "
                f"{self.c('ink')}; letter-spacing: 0;"
            )
        return (
            f"max-width: {self.width}px; margin: 0 auto {bottom}px auto; font-family: {self.f('cjk')}; "
            f"font-size: {self.t('section_title_size')}; line-height: 1.88; font-weight: 600; "
            f"color: {self.c('ink')}; text-align: left; border-bottom: 1px solid {self.c('line')}; "
            "padding-bottom: 12px; letter-spacing: 0;"
        )

    def song_section_heading_p(self, spacing: Dict[str, int]) -> str:
        return (
            f"max-width: {self.width}px; margin: {spacing['top']}px auto {spacing['bottom']}px auto; "
            f"padding: 0 0 14px 0; border-bottom: 1px solid {self.c('line')}; "
            f"font-family: {self.f('cjk')}; color: {self.c('ink')}; text-align: left; letter-spacing: 0;"
        )

    def song_section_meta_span(self) -> str:
        return (
            f"display: block; margin: 0 0 10px 0; font-family: {self.f('latin')}; "
            "font-size: 12px; line-height: 1.2; font-weight: 400; "
            f"color: {self.c('muted')}; letter-spacing: 0.14em;"
        )

    def song_section_title_span(self) -> str:
        return (
            "display: block; "
            f"font-size: {self.t('section_title_size')}; line-height: 1.44; "
            f"font-weight: 700; color: {self.c('ink')};"
        )

    def subtitle_p(self, spacing: Optional[Dict[str, int]] = None) -> str:
        spacing = spacing or {"top": 36, "bottom": 22}
        if self.is_theme("song"):
            return (
                f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; "
                f"font-family: {self.f('cjk')}; font-size: {self.t('body_size')}; line-height: 1.6; font-weight: 500; "
                f"color: {self.c('ink')}; text-align: left; padding: 0; letter-spacing: 0;"
            )
        return (
            f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; font-family: {self.f('cjk')}; "
            f"font-size: {self.t('section_title_size')}; line-height: 1.88; font-weight: 700; "
            f"color: {self.c('ink')}; text-align: left; border-bottom: 1px solid {self.c('line_soft')}; "
            "padding-bottom: 10px; letter-spacing: 0;"
        )

    def list_p(self, spacing: Optional[Dict[str, int]] = None) -> str:
        spacing = spacing or {"top": 0, "bottom": 12}
        return (
            f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; font-family: {self.f('cjk')}; "
            f"font-size: {self.t('small_size')}; line-height: 1.8; color: {self.c('text')}; text-align: left;"
        )

    def quote_wrap_p(self, spacing: Optional[Dict[str, int]] = None) -> str:
        spacing = spacing or {"top": 30, "bottom": 30}
        return f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])};"

    def quote_p(self, border: str, background: Optional[str] = None, text: Optional[str] = None) -> str:
        if self.is_theme("song"):
            return (
                f"display: block; padding: 16px 20px 16px 20px; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('small_size')}; line-height: 1.8; text-align: left; "
                f"background-color: {background or self.c('surface')}; border: 1px solid {self.c('line')}; "
                f"border-radius: {self.radius()}; "
                f"color: {text or self.c('text')};"
            )
        return (
            f"display: block; padding: 18px 20px 18px 20px; font-family: {self.f('cjk')}; "
            f"font-size: {self.t('body_size')}; line-height: 1.92; text-align: left; "
            f"background-color: {background or self.c('surface')}; border-left: 3px solid {border}; "
            f"border-radius: {self.radius()}; color: {text or self.c('text')};"
        )

    def code_meta_p(self, top: int) -> str:
        if self.is_theme("song"):
            return (
                f"max-width: {self.width}px; margin: {top}px auto 8px auto; font-family: {self.f('latin')}; "
                f"font-size: {self.t('small_size')}; line-height: 1.6; color: {self.c('muted')}; "
                "text-align: left; letter-spacing: 0;"
            )
        return (
            f"max-width: {self.width}px; margin: {top}px auto 10px auto; font-family: {self.f('mono')}; "
            f"font-size: {self.t('small_size')}; line-height: 1.4; color: {self.c('muted')}; "
            "text-align: left; letter-spacing: 0.08em;"
        )

    def code_p(self) -> str:
        if self.is_theme("song"):
            return (
                f"display: block; padding: 14px 18px 14px 18px; font-family: {self.f('mono')}; "
                f"font-size: {self.t('code_size')}; line-height: 1.6; color: {self.c('code_text')}; "
                f"text-align: left; white-space: pre-wrap; background-color: {self.c('surface')}; "
                f"border: 1px solid {self.c('line')}; border-radius: {self.radius()};"
            )
        return (
            f"display: block; padding: 18px 20px 18px 20px; font-family: {self.f('mono')}; "
            f"font-size: {self.t('code_size')}; line-height: 1.82; color: {self.c('code_text')}; "
            f"text-align: left; white-space: pre-wrap; background-color: {self.c('surface_alt')}; "
            f"border: 1px solid {self.c('line')}; border-radius: {self.radius()};"
        )

    def code_wrap_p(self, bottom: int) -> str:
        return f"max-width: {self.width}px; margin: 0 auto {bottom}px auto;"

    def table_meta_p(self, top: int) -> str:
        if self.is_theme("song"):
            return (
                f"max-width: {self.width}px; margin: {top}px auto 8px auto; font-family: {self.f('latin')}; "
                f"font-size: {self.t('small_size')}; line-height: 1.6; color: {self.c('ink')}; "
                "text-align: left; letter-spacing: 0;"
            )
        return (
            f"max-width: {self.width}px; margin: {top}px auto 12px auto; font-family: {self.f('mono')}; "
            f"font-size: {self.t('small_size')}; line-height: 1.4; color: {self.c('muted')}; "
            "text-align: left; letter-spacing: 0.08em;"
        )

    def table_card_p(self) -> str:
        if self.is_theme("song"):
            return (
                f"display: block; padding: 0; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('body_size')}; line-height: 1.92; color: {self.c('text')}; "
                f"text-align: left; background-color: transparent;"
            )
        return (
            f"display: block; padding: 17px 20px 17px 20px; font-family: {self.f('cjk')}; "
            f"font-size: {self.t('body_size')}; line-height: 1.9; color: {self.c('text')}; "
            f"text-align: left; background-color: {self.c('surface')}; border: 1px solid {self.c('line')}; "
            f"border-radius: {self.radius()};"
        )

    def table_wrap_p(self, bottom: int = 14) -> str:
        return f"max-width: {self.width}px; margin: 0 auto {bottom}px auto;"

    def table_value_style(self, is_last: bool) -> str:
        bottom = "0" if is_last else "12px"
        if self.is_theme("song"):
            return (
                f"display: block; margin-bottom: {bottom}; padding-bottom: 0; color: {self.c('text')};"
            )
        return (
            f"display: block; margin-bottom: 10px; color: {self.c('text')};"
            if not is_last
            else f"display: block; color: {self.c('text')};"
        )

    def table_label_style(self) -> str:
        if self.is_theme("song"):
            return (
                f"display: block; margin-bottom: 3px; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('small_size')}; line-height: 1.48; color: {self.c('muted')}; "
                "letter-spacing: 0;"
            )
        return (
            f"display: block; margin-bottom: 4px; font-family: {self.f('mono')}; "
            f"font-size: {self.t('small_size')}; line-height: 1.4; color: {self.c('muted')}; "
            "letter-spacing: 0.08em;"
        )

    def song_table_cell_style(self, index: int, total: int, header: bool, last_row: bool) -> str:
        weight = "700" if header else "400"
        color = self.c("ink") if header else self.c("text")
        background = self.c("surface_alt") if header else "transparent"
        return (
            f"display: table-cell; width: {100 / max(total, 1):.4f}%; box-sizing: border-box; "
            f"padding: 8px 8px; font-family: {self.f('cjk')}; font-size: {self.t('small_size')}; "
            f"line-height: 1.6; color: {color}; font-weight: {weight}; text-align: center; "
            f"vertical-align: middle; overflow-wrap: anywhere; word-break: break-word; "
            f"background-color: {background}; border: 1px solid {self.c('line_soft')};"
        )

    def song_table_row(self, cells: Sequence[str], total: int, header: bool, last_row: bool) -> str:
        normalized = list(cells[:total]) + [""] * max(0, total - len(cells))
        cells_html = "".join(
            f'<span style="{self.song_table_cell_style(index, total, header, last_row)}">{self.render_inline(cell)}</span>'
            for index, cell in enumerate(normalized)
        )
        return f'<span style="display: table-row;">{cells_html}</span>'

    def task_box_style(self, checked: bool) -> str:
        mark = self.c("accent")
        return (
            f"display: inline-block; width: 12px; height: 12px; margin: 0 10px 0 0; "
            f"line-height: 12px; text-align: center; vertical-align: middle; "
            f"font-family: {self.f('latin')}; font-size: {self.t('small_size')}; color: {mark}; "
            f"border: 1px solid {mark}; background-color: "
            f"{self.c('surface_alt') if checked else 'transparent'};"
        )

    def inline_code_style(self) -> str:
        if self.is_theme("song"):
            return (
                f"font-family: {self.f('mono')}; font-size: {self.t('small_size')}; background-color: {self.c('surface')}; "
                f"color: {self.c('code_text')}; padding: 1px 5px; border-radius: 1px; "
                f"border: 1px solid {self.c('line')}; "
                "vertical-align: middle; overflow-wrap: anywhere; word-break: break-word;"
            )
        return (
            f"font-family: {self.f('mono')}; font-size: 0.9em; background-color: {self.c('surface_alt')}; "
            f"color: {self.c('code_text')}; padding: 1px 6px; border-radius: 4px;"
        )

    def link_style(self) -> str:
        if self.is_theme("song"):
            return f"color: {self.c('ink')}; text-decoration: none; border-bottom: 1px solid {self.c('accent')};"
        return f"color: {self.c('ink')}; text-decoration: none; border-bottom: 1px solid {self.c('accent')};"

    def strong_style(self) -> str:
        return f"font-weight: 700; color: {self.c('ink')};"

    def highlight_style(self) -> str:
        if self.is_theme("song"):
            return f"font-weight: 700; color: {self.c('ink')};"
        return f"border-bottom: 1px dashed {self.c('accent')}; font-weight: 600;"

    def em_style(self) -> str:
        return f"font-style: italic; color: {self.c('muted')};"

    def strike_style(self) -> str:
        return f"text-decoration: line-through; color: {self.c('muted')};"

    def latin_inline_style(self) -> str:
        if self.is_theme("song"):
            return (
                f"font-family: {self.f('latin')}; letter-spacing: 0; "
                f"color: {self.c('ink')};"
            )
        return (
            f"font-family: {self.f('latin')}; font-size: 0.96em; letter-spacing: 0.01em; "
            f"color: {self.c('ink')};"
        )

    def marker_style(self, ordered: bool) -> str:
        color = self.c("muted")
        weight = "500"
        if self.is_theme("song"):
            color = self.c("accent")
            weight = "400"
        return (
            f"display: inline-block; width: 18px; margin-right: 10px; text-align: center; "
            f"vertical-align: middle; font-family: {self.f('latin')}; font-size: {self.t('small_size') if self.is_theme('song') else '12px'}; line-height: 1.6; "
            f"font-weight: {weight}; color: {color}; letter-spacing: {'0.04em' if ordered else '0'};"
        )

    def render_image(self, alt_text: str, source: str) -> str:
        safe_alt = html.escape(alt_text.strip())
        safe_source = html.escape(source.strip(), quote=True)
        image_html = (
            f'<img src="{safe_source}" alt="{safe_alt}" '
            f'style="display: block; max-width: 100%; height: auto; margin: 14px auto; '
            f'border-radius: {self.radius("image_radius")};" />'
        )
        if safe_alt:
            if self.is_theme("song"):
                image_html += (
                    f'<span style="display: block; width: 88%; margin: 10px auto 0 auto; padding-top: 0; '
                    f'font-size: {self.t("small_size")}; line-height: 1.72; color: {self.c("muted")}; '
                    f'text-align: center; letter-spacing: 0.02em; font-family: {self.f("cjk")};">'
                    f'{self.balance_latin_text(safe_alt)}</span>'
                )
            else:
                image_html += (
                    f'<span style="display: block; width: 88%; margin: 12px auto 0 auto; padding-top: 9px; '
                    f'border-top: 1px solid {self.c("line_soft")}; font-size: {self.t("small_size")}; '
                    f'line-height: 1.72; color: {self.c("muted")}; text-align: center; letter-spacing: 0.02em; '
                    f'font-family: {self.f("cjk")};">{self.balance_latin_text(safe_alt)}</span>'
                )
        return image_html

    def component_wrap_p(self, spacing: Optional[Dict[str, int]] = None) -> str:
        spacing = spacing or {"top": 0, "bottom": self.rhythm("paragraph_gap", 22)}
        return f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])};"

    def render_component_lead(self, text: str, layout: Optional[Dict[str, Any]] = None) -> str:
        spacing = spacing_from_layout(layout, self.rhythm("paragraph_gap", 22))
        if self.is_theme("song"):
            style = (
                f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; "
                f"font-family: {self.f('cjk')}; font-size: {self.t('body_size')}; line-height: 1.8; "
                f"color: {self.c('text')}; text-align: left; letter-spacing: 0; font-weight: 400;"
            )
        else:
            style = self.base_p(spacing)
        return f'<p style="{style}">{self.render_inline(text)}</p>'

    def render_component_insight(self, text: str, layout: Optional[Dict[str, Any]] = None) -> str:
        spacing = spacing_from_layout(layout, self.rhythm("paragraph_gap", 22) + 4)
        if self.is_theme("song"):
            style = (
                f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; "
                f"font-family: {self.f('cjk')}; font-size: {self.t('small_size')}; line-height: 1.8; "
                f"color: {self.c('ink')}; text-align: left; letter-spacing: 0; font-weight: 700; "
                f"border-left: 2px solid {self.c('accent')}; padding: 2px 0 2px 14px;"
            )
        else:
            style = (
                f"{self.base_p(spacing)} font-weight: 700; color: {self.c('ink')}; "
                f"border-left: 3px solid {self.c('accent')}; padding-left: 14px;"
            )
        return f'<p style="{style}">{self.render_inline(text)}</p>'

    def render_component_pullquote(self, text: str, layout: Optional[Dict[str, Any]] = None) -> str:
        spacing = spacing_from_layout(layout, self.rhythm("quote_breathing", 18))
        if self.is_theme("song"):
            quote_style = (
                f"display: block; padding: 18px 24px 18px 24px; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('small_size')}; line-height: 1.8; text-align: left; "
                f"color: {self.c('ink')}; background-color: {self.c('surface')}; "
                f"border-left: 3px solid {self.c('accent')}; border-radius: 0;"
            )
        else:
            quote_style = self.quote_p(self.c("accent"), self.c("surface"), self.c("ink"))
        return (
            f'<p style="{self.component_wrap_p(spacing)}">'
            f'<span style="{quote_style}">{self.render_inline(text)}</span>'
            "</p>"
        )

    def render_component_figure(
        self,
        source: str,
        alt: str,
        caption: str,
        layout: Optional[Dict[str, Any]] = None,
    ) -> str:
        spacing = spacing_from_layout(layout, 22)
        safe_source = html.escape(source.strip(), quote=True)
        safe_alt = html.escape(alt.strip())
        if self.is_theme("song"):
            image_style = (
                f"display: block; width: 100%; max-width: 100%; height: auto; margin: 0 auto; "
                f"border-radius: {self.radius('image_radius')};"
            )
            caption_style = (
                f"display: block; width: 88%; margin: 10px auto 0 auto; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('small_size')}; line-height: 1.8; color: {self.c('muted')}; "
                "text-align: center; letter-spacing: 0.02em;"
            )
        else:
            image_style = (
                f"display: block; width: 100%; max-width: 100%; height: auto; margin: 0 auto; "
                f"border-radius: {self.radius('image_radius')};"
            )
            caption_style = (
                f"display: block; width: 88%; margin: 12px auto 0 auto; padding-top: 9px; "
                f"border-top: 1px solid {self.c('line_soft')}; font-family: {self.f('cjk')}; "
                f"font-size: {self.t('small_size')}; line-height: 1.72; color: {self.c('muted')}; "
                "text-align: center; letter-spacing: 0.02em;"
            )
        caption_html = ""
        if caption.strip():
            caption_html = f'<span style="{caption_style}">{self.render_inline(caption.strip())}</span>'
        return (
            f'<p style="{self.component_wrap_p(spacing)}">'
            f'<img src="{safe_source}" alt="{safe_alt}" style="{image_style}" />'
            f"{caption_html}</p>"
        )

    def render_component_soft_list(
        self, items: Sequence[Dict[str, Any]], layout: Optional[Dict[str, Any]] = None
    ) -> List[str]:
        spacing = spacing_from_layout(layout, 12)
        rendered: List[str] = []
        marker_style = (
            f"display: inline-block; width: 18px; margin-right: 10px; text-align: center; "
            f"vertical-align: middle; font-family: {self.f('latin')}; font-size: {self.t('small_size')}; "
            f"line-height: 1.6; color: {self.c('accent')}; font-weight: 400;"
        )
        content_style = "display: inline-block; max-width: 88%; vertical-align: middle; line-height: 1.6;"
        for index, item in enumerate(items):
            item_spacing = {"top": spacing["top"] if index == 0 else 0, "bottom": spacing["bottom"]}
            rendered.append(
                f'<p style="{self.list_p(item_spacing)}">'
                f'<span style="{marker_style}">○</span>'
                f'<span style="{content_style}">{self.render_inline(str(item.get("text", "")))}</span></p>'
            )
        return rendered

    def render_component_closing_note(self, text: str, layout: Optional[Dict[str, Any]] = None) -> str:
        spacing = spacing_from_layout(layout, 18)
        if self.is_theme("song"):
            style = (
                f"max-width: {self.width}px; margin: {self.margin(spacing['top'], spacing['bottom'])}; "
                f"font-family: {self.f('cjk')}; font-size: {self.t('small_size')}; line-height: 1.8; "
                f"color: {self.c('muted')}; text-align: center; letter-spacing: 0;"
            )
        else:
            style = self.base_p(spacing) + " text-align: center;"
        return f'<p style="{style}">{self.render_inline(text)}</p>'

    def render_component(self, block: Dict[str, Any], layout: Optional[Dict[str, Any]] = None) -> List[str]:
        name = str(block.get("name", ""))
        if name == "lead":
            return [self.render_component_lead(str(block.get("text", "")), layout)]
        if name == "insight":
            return [self.render_component_insight(str(block.get("text", "")), layout)]
        if name == "pullquote":
            return [self.render_component_pullquote(str(block.get("text", "")), layout)]
        if name == "figure":
            return [
                self.render_component_figure(
                    str(block.get("source", "")),
                    str(block.get("alt", "")),
                    str(block.get("caption", "")),
                    layout,
                )
            ]
        if name == "soft-list":
            return self.render_component_soft_list(block.get("items", []), layout)
        if name == "closing-note":
            return [self.render_component_closing_note(str(block.get("text", "")), layout)]
        return [self.render_paragraph(str(block.get("text", "")), layout)]

    def render_link(self, label: str, target: str) -> str:
        safe_target = html.escape(target.strip(), quote=True)
        return f'<a href="{safe_target}" style="{self.link_style()}">{self.render_inline(label)}</a>'

    def apply_recursive_pattern(
        self, text: str, pattern: re.Pattern[str], repl: Any, recursive: bool = True
    ) -> str:
        while True:
            def replace(match: re.Match[str]) -> str:
                inner = match.group(1)
                return repl(self.render_inline(inner) if recursive else inner)

            updated, count = pattern.subn(replace, text)
            text = updated
            if count == 0:
                return text

    def balance_latin_text(self, fragment: str) -> str:
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
                self.latin_text_re.sub(
                    lambda match: f'<span style="{self.latin_inline_style()}">{match.group(0)}</span>',
                    segment,
                )
            )
        return "".join(balanced)

    def render_inline(self, text: str, balance_latin: bool = True) -> str:
        placeholders: List[str] = []

        def stash(fragment: str) -> str:
            token = placeholder_token(len(placeholders))
            placeholders.append(fragment)
            return token

        working = text
        working = re.sub(
            r"`([^`]+)`",
            lambda match: stash(
                f'<span style="{self.inline_code_style()}">{html.escape(match.group(1))}</span>'
            ),
            working,
        )
        working = re.sub(
            r"!\[([^\]]*)\]\(([^)]+)\)",
            lambda match: stash(self.render_image(match.group(1), match.group(2))),
            working,
        )
        working = re.sub(
            r"\[([^\]]+)\]\(([^)]+)\)",
            lambda match: stash(self.render_link(match.group(1), match.group(2))),
            working,
        )

        escaped = html.escape(working).replace("\n", "<br>")
        escaped = self.apply_recursive_pattern(
            escaped,
            re.compile(r"==(.+?)==", re.DOTALL),
            lambda inner: f'<span style="{self.highlight_style()}">{inner}</span>',
        )
        escaped = self.apply_recursive_pattern(
            escaped,
            re.compile(r"(?:\*\*|__)(.+?)(?:\*\*|__)", re.DOTALL),
            lambda inner: f'<span style="{self.strong_style()}">{inner}</span>',
        )
        escaped = self.apply_recursive_pattern(
            escaped,
            re.compile(r"~~(.+?)~~", re.DOTALL),
            lambda inner: f'<span style="{self.strike_style()}">{inner}</span>',
        )
        escaped = self.apply_recursive_pattern(
            escaped,
            re.compile(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", re.DOTALL),
            lambda inner: f'<span style="{self.em_style()}">{inner}</span>',
        )
        escaped = self.apply_recursive_pattern(
            escaped,
            re.compile(r"(?<!_)_(?!_)(.+?)(?<!_)_(?!_)", re.DOTALL),
            lambda inner: f'<span style="{self.em_style()}">{inner}</span>',
        )
        if balance_latin:
            escaped = self.balance_latin_text(escaped)

        for index, fragment in enumerate(placeholders):
            escaped = escaped.replace(placeholder_token(index), fragment)
        return escaped

    def render_heading_inline(self, text: str, size_key: str = "section_title_size", balance_latin: bool = True) -> str:
        rendered = self.render_inline(text, balance_latin=balance_latin)
        if self.is_theme("song"):
            rendered = rendered.replace(
                f"font-size: {self.t('body_size')};",
                f"font-size: {self.t(size_key)};",
            )
        return rendered

    def render_paragraph(self, text: str, layout: Optional[Dict[str, Any]] = None) -> str:
        spacing = spacing_from_layout(layout, self.rhythm("paragraph_gap", 22))
        strong_match = FULL_STRONG_RE.match(text)
        if strong_match:
            content = self.render_inline(strong_match.group(2).strip())
            return (
                f'<p style="{self.base_p(spacing)} font-weight: 700; color: {self.c("ink")};">{content}</p>'
            )
        return f'<p style="{self.base_p(spacing)}">{self.render_inline(text)}</p>'

    def render_heading(self, level: int, text: str, layout: Optional[Dict[str, Any]] = None) -> List[str]:
        spacing = spacing_from_layout(layout, self.rhythm("heading_bottom", 24))
        stripped = text.strip()
        if level == 1:
            return [
                f'<p style="{self.title_p(spacing)}">{self.render_heading_inline(stripped, "title_size")}</p>'
            ]

        numeric_match = NUMERIC_SECTION_RE.match(stripped)
        if numeric_match:
            number = numeric_match.group("num").zfill(2)
            title = numeric_match.group("title").strip()
            if self.is_theme("song"):
                label = self.chinese_section_label(number)
                return [
                    f'<p style="{self.song_section_heading_p(spacing)}">'
                    f'<span style="{self.song_section_meta_span()}">SECTION {html.escape(number)}</span>'
                    f'<span style="{self.song_section_title_span()}">'
                    f'{html.escape(label)}、{self.render_heading_inline(title, "section_title_size")}</span></p>'
                ]
            return [
                f'<p style="{self.section_num_p(spacing["top"])}">{html.escape(number)}</p>',
                f'<p style="{self.section_title_p(spacing["bottom"])}">{self.render_heading_inline(title)}</p>',
            ]

        if self.is_theme("song") and level == 2:
            return [
                f'<p style="{self.song_section_heading_p(spacing)}">'
                f'<span style="{self.song_section_title_span()}">'
                f'{self.render_heading_inline(stripped, "section_title_size")}</span></p>'
            ]

        return [
            f'<p style="{self.subtitle_p(spacing)}">{self.render_heading_inline(stripped, "body_size")}</p>'
        ]

    def render_quote(self, lines: Sequence[str], layout: Optional[Dict[str, Any]] = None) -> str:
        spacing = spacing_from_layout(layout, self.rhythm("quote_breathing", 34))
        cleaned = [line for line in lines if line.strip()]
        quote_kind = "QUOTE"
        border = self.c("line")
        background = self.c("surface")
        text_color = self.c("text")

        if cleaned:
            kind_match = NOTE_RE.match(cleaned[0].strip())
            if kind_match:
                quote_kind = kind_match.group(1).upper()
                remainder = kind_match.group(2).strip()
                cleaned = cleaned[1:]
                if remainder:
                    cleaned.insert(0, remainder)

        if quote_kind == "TIP":
            border = self.c("accent")
        elif quote_kind == "WARNING":
            border = self.c("warning")
            background = self.c("warning_bg")
        elif quote_kind in {"NOTE", "IMPORTANT", "CAUTION"}:
            border = self.c("muted")

        text = merge_lines(cleaned)
        if self.is_theme("song") and quote_kind != "QUOTE":
            labels = {
                "NOTE": "注",
                "IMPORTANT": "要",
                "CAUTION": "慎",
                "TIP": "笺",
                "WARNING": "警",
            }
            label = labels.get(quote_kind, "注")
            label_html = (
                f'<span style="display: inline-block; margin: 0 10px 0 0; padding: 0 0 2px 0; '
                f'font-family: {self.f("cjk")}; font-size: {self.t("small_size")}; line-height: 1; '
                f'font-weight: 700; color: {border}; vertical-align: 0.08em;">'
                f'{html.escape(label)}</span>'
            )
            text = f"{label_html}{self.render_inline(text)}"
        else:
            text = self.render_inline(text)
        return (
            f'<p style="{self.quote_wrap_p(spacing)}">'
            f'<span style="{self.quote_p(border, background, text_color)}">{text}</span>'
            "</p>"
        )

    def render_list(self, items: Sequence[Dict[str, Any]], ordered: bool, layout: Optional[Dict[str, Any]] = None) -> List[str]:
        rendered = []
        content_style = "display: inline-block; max-width: 88%; vertical-align: middle; line-height: 1.6;"
        spacing = spacing_from_layout(layout, 12)
        for index, item in enumerate(items):
            item_text = item["text"]
            task_match = TASK_ITEM_RE.match(item_text)
            if self.is_theme("song") and task_match:
                checked = task_match.group("mark").lower() == "x"
                content = self.render_inline(task_match.group("text"))
                item_spacing = {"top": spacing["top"] if index == 0 else 0, "bottom": spacing["bottom"]}
                rendered.append(
                    f'<p style="{self.list_p(item_spacing)}">'
                    f'<span style="{self.task_box_style(checked)}">{"✓" if checked else ""}</span>'
                    f'<span style="{content_style}">{content}</span></p>'
                )
                continue
            marker = f"{item['number']}." if ordered else "○" if self.is_theme("song") else "•"
            content = self.render_inline(item_text)
            item_spacing = {"top": spacing["top"] if index == 0 else 0, "bottom": spacing["bottom"]}
            rendered.append(
                f'<p style="{self.list_p(item_spacing)}"><span style="{self.marker_style(ordered)}">{html.escape(marker)}</span>'
                f'<span style="{content_style}">{content}</span></p>'
            )
        return rendered

    def render_code(self, text: str, language: str, layout: Optional[Dict[str, Any]] = None) -> List[str]:
        spacing = spacing_from_layout(layout, 32)
        label = html.escape(language.upper() if language else "CODE")
        rule = ""
        if not self.is_theme("song"):
            rule = (
                f'<span style="display: inline-block; width: 28px; border-top: 1px solid {self.c("line")}; '
                'margin: 0 10px 4px 0;"></span>'
            )
        if self.is_theme("song"):
            numbered = []
            for line_number, line in enumerate(text.splitlines() or [""], start=1):
                numbered.append(
                    f'<span style="display: block;">'
                    f'<span style="display: inline-block; width: 24px; margin-right: 14px; '
                    f'color: {self.c("muted")}; text-align: right;">{line_number}</span>'
                    f'{html.escape(line)}</span>'
                )
            return [
                f'<p style="{self.code_meta_p(spacing["top"])}">{label}</p>',
                f'<p style="{self.code_wrap_p(spacing["bottom"])}"><span style="{self.code_p()}">{"".join(numbered)}</span></p>',
            ]
        return [
            f'<p style="{self.code_meta_p(spacing["top"])}">{rule}{label}</p>',
            f'<p style="{self.code_wrap_p(spacing["bottom"])}"><span style="{self.code_p()}">{html.escape(text)}</span></p>',
        ]

    def render_table(self, header: Sequence[str], rows: Sequence[Sequence[str]], layout: Optional[Dict[str, Any]] = None) -> List[str]:
        spacing = spacing_from_layout(layout, 20)
        if self.is_theme("song"):
            total = max(len(header), max((len(row) for row in rows), default=0), 1)
            body_rows = [self.song_table_row(header, total, True, not rows)]
            for row_index, row in enumerate(rows):
                body_rows.append(self.song_table_row(row, total, False, row_index == len(rows) - 1))
            rows_html = "".join(body_rows)
            return [
                f'<p style="{self.table_wrap_p(spacing["bottom"])}">'
                f'<span style="{self.table_card_p()}">'
                f'<span style="display: table; width: 100%; table-layout: fixed; border-collapse: collapse;">'
                f"{rows_html}"
                "</span></span></p>"
            ]
        rule = ""
        if not self.is_theme("song"):
            rule = (
                f'<span style="display: inline-block; width: 28px; border-top: 1px solid {self.c("line")}; '
                'margin: 0 10px 4px 0;"></span>'
            )
        rendered = [
            f'<p style="{self.table_meta_p(spacing["top"])}">{rule}{" × ".join(self.render_inline(cell) for cell in header)}</p>'
        ]
        for row_index, row in enumerate(rows):
            pairs: List[str] = []
            for index, cell in enumerate(row):
                label = header[index] if index < len(header) else f"Column {index + 1}"
                value_style = self.table_value_style(index == len(row) - 1)
                pairs.append(f'<span style="{self.table_label_style()}">{self.render_inline(label)}</span>')
                pairs.append(f'<span style="{value_style}">{self.render_inline(cell)}</span>')
            rendered.append(
                f'<p style="{self.table_wrap_p(spacing["bottom"] if row_index == len(rows) - 1 else 14)}"><span style="{self.table_card_p()}">{"".join(pairs)}</span></p>'
            )
        return rendered

    def render_divider(self, layout: Optional[Dict[str, Any]] = None) -> str:
        spacing = spacing_from_layout(layout, self.rhythm("section_break", 42))
        if self.is_theme("song"):
            return (
                f'<p style="max-width: {self.width}px; margin: {self.margin(spacing["top"], spacing["bottom"])}; '
                'text-align: center; line-height: 1;">'
                f'<span style="display: inline-block; width: 30%; border-top: 1px solid {self.c("line_soft")}; '
                'vertical-align: middle;"></span>'
                f'<span style="display: inline-block; margin: 0 12px; font-family: {self.f("cjk")}; '
                f'font-size: {self.t("body_size")}; line-height: 1; color: {self.c("soft")}; '
                'vertical-align: middle;">※</span>'
                f'<span style="display: inline-block; width: 30%; border-top: 1px solid {self.c("line_soft")}; '
                'vertical-align: middle;"></span>'
                "</p>"
            )
        return (
            f'<p style="max-width: {self.width}px; margin: {self.margin(spacing["top"], spacing["bottom"])}; text-align: center; line-height: 1;">'
            f'<span style="display: inline-block; width: 54px; border-top: 1px solid {self.c("line_soft")}; '
            'vertical-align: middle;"></span>'
            f'<span style="display: inline-block; margin: 0 12px; font-family: {self.f("latin")}; '
            f'font-size: 10px; line-height: 1; color: {self.c("soft")}; letter-spacing: 0.28em; '
            'vertical-align: middle;">··</span>'
            f'<span style="display: inline-block; width: 54px; border-top: 1px solid {self.c("line_soft")}; '
            'vertical-align: middle;"></span>'
            "</p>"
        )

    def render_blocks(self, blocks: Sequence[Dict[str, Any]]) -> str:
        rendered: List[str] = []
        for index, block in enumerate(blocks):
            block_type = block["type"]
            layout = self.plans[index] if index < len(self.plans) else None
            if block_type == "heading":
                rendered.extend(self.render_heading(block["level"], block["text"], layout))
            elif block_type == "paragraph":
                rendered.append(self.render_paragraph(block["text"], layout))
            elif block_type == "quote":
                rendered.append(self.render_quote(block["lines"], layout))
            elif block_type == "list":
                rendered.extend(self.render_list(block["items"], block["ordered"], layout))
            elif block_type == "code":
                rendered.extend(self.render_code(block["text"], block["language"], layout))
            elif block_type == "table":
                rendered.extend(self.render_table(block["header"], block["rows"], layout))
            elif block_type == "divider":
                rendered.append(self.render_divider(layout))
            elif block_type == "component":
                rendered.extend(self.render_component(block, layout))
        return "\n".join(rendered).strip() + "\n"

    def wrap_document(self, title: str, fragment: str) -> str:
        safe_title = html.escape(title)
        return (
            "<!DOCTYPE html>\n"
            '<html lang="zh-CN">\n'
            "<head>\n"
            '  <meta charset="UTF-8" />\n'
            '  <meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
            f"  <title>{safe_title}</title>\n"
            "</head>\n"
            f'<body style="{self.body_style()}">\n'
            f"{fragment}"
            "</body>\n"
            "</html>\n"
        )


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


def render_markdown(
    input_path: Path,
    output_path: Path,
    title: Optional[str],
    theme_id: str,
    fragment_only: bool,
    article_type: Optional[str] = None,
    density: Optional[str] = None,
    tone: Optional[str] = None,
) -> str:
    theme = load_theme(theme_id)
    frontmatter_title, markdown = strip_frontmatter(input_path.read_text(encoding="utf-8"))
    document = render_markdown_text(
        markdown,
        input_path=input_path,
        title=title,
        frontmatter_title=frontmatter_title,
        theme=theme,
        fragment_only=fragment_only,
        article_type=article_type,
        density=density,
        tone=tone,
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(document, encoding="utf-8")
    return document


def render_markdown_text(
    markdown: str,
    *,
    input_path: Path,
    title: Optional[str],
    frontmatter_title: Optional[str],
    theme: Dict[str, Any],
    fragment_only: bool,
    article_type: Optional[str] = None,
    density: Optional[str] = None,
    tone: Optional[str] = None,
) -> str:
    safety_findings = verify_markdown_safety(markdown)
    if safety_findings:
        raise ValueError("; ".join(safety_findings))
    blocks = parse_blocks(markdown)
    unknown_components = [
        str(block.get("name", ""))
        for block in blocks
        if block.get("type") == "unknown_component"
    ]
    if unknown_components:
        allowed = ", ".join(sorted(ALLOWED_KAIROS_COMPONENTS))
        names = ", ".join(sorted(set(unknown_components)))
        raise ValueError(f"Unknown Kairos component(s): {names}. Allowed components: {allowed}.")
    semantics = analyze_blocks(blocks)
    art_direction = select_art_direction(theme, article_type=article_type, density=density, tone=tone)
    plans = build_rhythm_plan(blocks, semantics, theme, art_direction)
    compiled = compile_plan(blocks, plans)
    renderer = Renderer(theme, [item["layout"] for item in compiled])
    fragment = renderer.render_blocks(blocks)
    chosen_title = choose_title(title, frontmatter_title, blocks, input_path)
    return fragment if fragment_only else renderer.wrap_document(chosen_title, fragment)


def print_themes() -> None:
    for theme in available_themes():
        suitable = " / ".join(theme.get("suitable_for", []))
        print(f"{theme['id']}\t{theme.get('name_zh', theme['name'])}\t{suitable}")


def main() -> None:
    args = parse_args()
    if args.list_themes:
        print_themes()
        return

    if not args.input:
        raise SystemExit("--input is required unless --list-themes is used.")

    input_path = Path(args.input).expanduser().resolve()
    output_path = (
        Path(args.output).expanduser().resolve()
        if args.output
        else input_path.with_suffix(".html")
    )

    try:
        document = render_markdown(
            input_path,
            output_path,
            args.title,
            args.theme,
            args.fragment_only,
            article_type=args.article_type,
            density=args.density,
            tone=args.tone,
        )
    except (FileNotFoundError, ValueError, json.JSONDecodeError) as exc:
        raise SystemExit(str(exc)) from exc

    if args.verify:
        theme = load_theme(args.theme)
        _, markdown = strip_frontmatter(input_path.read_text(encoding="utf-8"))
        blocks = parse_blocks(markdown)
        findings = verify_html(document, args.fragment_only)
        findings.extend(verify_editorial_blocks(blocks, theme))
        if findings:
            for finding in findings:
                print(f"VERIFY: {finding}", file=sys.stderr)
            raise SystemExit(1)
        print("Verified inline WeChat HTML constraints.")

    print(f"Rendered {input_path} -> {output_path} with theme '{args.theme}'")


if __name__ == "__main__":
    main()
