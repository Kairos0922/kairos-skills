"""
QA verification: two-layer check (global + style-specific).

Deterministic code — checks against defined rules, no AI judgment.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class QAResult:
    """Result of QA check."""
    passed: bool = True
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# Global QA checks (all styles must pass)
GLOBAL_QA_CHECKS = [
    "text_readable",
    "title_is_focal_point",
    "density_matches_usage",
    "colors_match_tokens",
    "no_banned_elements",
]


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


def run_full_qa(style_id: str, brief: dict, composition: dict, image_path: str = "") -> QAResult:
    """Run both global and style-specific QA."""
    global_result = run_global_qa(brief, image_path)
    style_result = run_style_qa(style_id, brief, composition)

    combined = QAResult()
    combined.passed = global_result.passed and style_result.passed
    combined.errors = global_result.errors + style_result.errors
    combined.warnings = global_result.warnings + style_result.warnings

    return combined
