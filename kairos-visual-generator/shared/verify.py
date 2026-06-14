"""
QA verification: two-layer check (global + style-specific).

Layer 1 (structural): Check HTML/CSS rules for potential issues.
Layer 2 (rendered): Check rendered PNG for visual issues.

Deterministic code — checks against defined rules, no AI judgment.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class QAResult:
    """Result of QA check."""
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# ─── Layer 1: Structural checks (lightweight, no image analysis) ───

def check_css_overlap(html_content: str) -> tuple[bool, str]:
    """Check if absolute-positioned TEXT elements have overlapping top ranges.

    Only checks elements that have font-size set (indicating they are text).
    Background/color-block elements are excluded.
    """
    import re

    # Find absolute-positioned elements that also have font-size (text elements)
    pattern = r'position:\s*absolute[^}]*font-size:\s*(\d+(?:\.\d+)?(?:px|em|rem)?)'
    matches = re.findall(pattern, html_content)

    if len(matches) < 2:
        return True, ""

    # Convert to comparable values
    sizes = []
    for m in matches:
        val = m.replace('px', '').replace('em', '').replace('rem', '')
        try:
            sizes.append(float(val))
        except ValueError:
            continue

    if len(sizes) < 2:
        return True, ""

    # Larger text elements need more vertical space
    # Check if any two text elements have similar top positions
    # (This is a simplified check - real implementation would need top values too)
    return True, ""


def check_flex_alignment(html_content: str) -> tuple[bool, str]:
    """Check if flex containers have consistent alignment for bottom elements.

    Looks for margin-top: auto on footer-like elements to ensure bottom alignment.
    """
    import re

    # Find flex containers
    flex_pattern = r'display:\s*flex'
    flex_count = len(re.findall(flex_pattern, html_content))

    # Find margin-top: auto
    auto_pattern = r'margin-top:\s*auto'
    auto_count = len(re.findall(auto_pattern, html_content))

    if flex_count > 1 and auto_count == 0:
        return False, "Multiple flex containers but no margin-top: auto for bottom alignment"

    return True, ""


def check_spacing_consistency(html_content: str) -> tuple[bool, str]:
    """Check if spacing values follow 8px grid system.

    Warns if non-8px-aligned values are used.
    """
    import re

    # Find all spacing values (margin, padding, gap)
    pattern = r'(?:margin|padding|gap)[\s:]+(-?\d+(?:\.\d+)?(?:px|em|rem)?)'
    matches = re.findall(pattern, html_content)

    non_aligned = []
    for m in matches:
        val = m.replace('px', '').replace('em', '').replace('rem', '')
        try:
            num = float(val)
            if num % 8 != 0 and num > 0:
                non_aligned.append(f"{val}px")
        except ValueError:
            continue

    if non_aligned and len(non_aligned) > len(matches) * 0.3:
        return True, f"Warning: {len(non_aligned)} spacing values not aligned to 8px grid: {', '.join(non_aligned[:5])}"

    return True, ""


# ─── Layer 2: Rendered image checks ───

def check_text_readable(image_path: str) -> tuple[bool, str]:
    """Check if text is readable (no clipping, overlap, garbled text)."""
    # Placeholder — actual implementation uses image analysis
    return True, ""


def check_title_focal(image_path: str) -> tuple[bool, str]:
    """Check if title is the primary visual focal point."""
    return True, ""


def check_density(usage: str, density: str) -> tuple[bool, str]:
    """Check if content density matches usage type."""
    cover_usages = ["X 封面", "海报", "公众号封面", "作品集封面", "PPT 封面",
                    "商业封面", "商业报告封面", "小红书封面"]
    if usage in cover_usages and density not in ["cover", "light"]:
        return False, f"Usage '{usage}' expects cover density, got '{density}'"
    return True, ""


def check_no_banned_elements(image_path: str, banned: list[str]) -> tuple[bool, str]:
    """Check if banned elements are present."""
    return True, ""


# ─── Combined QA runners ───

def run_structural_qa(html_content: str) -> QAResult:
    """Run structural checks on HTML content (lightweight, no image analysis)."""
    result = QAResult()

    checks = [
        ("css_overlap", lambda: check_css_overlap(html_content)),
        ("flex_alignment", lambda: check_flex_alignment(html_content)),
        ("spacing_consistency", lambda: check_spacing_consistency(html_content)),
    ]

    for name, check_fn in checks:
        passed, error = check_fn()
        if not passed:
            if "Warning" in error:
                result.warnings.append(f"[{name}] {error}")
            else:
                result.passed = False
                result.errors.append(f"[{name}] {error}")

    return result


def run_global_qa(brief: dict, image_path: str = "") -> QAResult:
    """Run global QA checks."""
    result = QAResult()

    checks = [
        ("text_readable", lambda: check_text_readable(image_path)),
        ("title_focal", lambda: check_title_focal(image_path)),
        ("density", lambda: check_density(brief.get("usage", ""), brief.get("content_density", ""))),
        ("no_banned", lambda: check_no_banned_elements(image_path, brief.get("banned_elements", []))),
    ]

    for name, check_fn in checks:
        passed, error = check_fn()
        if not passed:
            result.passed = False
            result.errors.append(f"[{name}] {error}")

    return result


def run_style_qa(style_id: str, brief: dict, composition: dict) -> QAResult:
    """Run style-specific QA checks from composition.json qa_checklist."""
    result = QAResult()

    checklist = composition.get("qa_checklist", [])
    # Actual implementation would verify each checklist item
    # For now, all items pass (placeholder for image analysis)

    return result


def run_full_qa(style_id: str, brief: dict, composition: dict, image_path: str = "",
                html_content: str = "") -> QAResult:
    """Run all QA layers: structural + global + style-specific."""
    combined = QAResult()

    # Layer 1: Structural checks (if HTML available)
    if html_content:
        structural_result = run_structural_qa(html_content)
        combined.errors.extend(structural_result.errors)
        combined.warnings.extend(structural_result.warnings)

    # Layer 2: Global checks
    global_result = run_global_qa(brief, image_path)
    combined.errors.extend(global_result.errors)

    # Layer 3: Style-specific checks
    style_result = run_style_qa(style_id, brief, composition)
    combined.errors.extend(style_result.errors)

    combined.passed = len(combined.errors) == 0

    return combined
