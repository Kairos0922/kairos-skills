#!/usr/bin/env python3
"""Verify an agent-authored image plan for kairos-wechat-typeset."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional, Sequence


ROOT = Path(__file__).resolve().parents[1]
THEMES_DIR = ROOT / "themes"
ALLOWED_VISUAL_TYPES = {
    "concept_diagram",
    "process_diagram",
    "comparison_diagram",
    "evidence_figure",
    "atmosphere_still",
}
ALLOWED_NECESSITY = {"high", "medium"}
ALLOWED_STATUS = {"planned", "prompt_only", "generated"}
DEFAULT_ASPECT_RATIO = "16:9"
TEXT_BAN_RE = re.compile(
    r"(no\s+readable\s+text|no\s+text|without\s+readable\s+text|无文字|不包含可读文字|不要文字|不生成文字)",
    re.IGNORECASE,
)
ABSOLUTE_PATH_RE = re.compile(r"^([A-Za-z]:[\\/]|/|~)")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Verify kairos-wechat-typeset image-plan.json.")
    parser.add_argument("--input", required=True, help="Path to image-plan.json.")
    parser.add_argument("--theme", help="Expected registered theme id.")
    parser.add_argument("--max-images", type=int, default=5, help="Maximum allowed images. Defaults to 5.")
    parser.add_argument(
        "--allow-non-default-ratio",
        action="store_true",
        help="Allow image aspect ratios other than 16:9.",
    )
    return parser.parse_args()


def load_theme(theme_id: str) -> Optional[Dict[str, Any]]:
    path = THEMES_DIR / f"{theme_id}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def text(value: Any) -> str:
    return str(value or "").strip()


def list_text(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]


def require_text(
    findings: List[str],
    item: Mapping[str, Any],
    field: str,
    label: str,
    minimum: int = 8,
) -> str:
    value = text(item.get(field))
    if len(value) < minimum:
        findings.append(f"{label} must include a meaningful '{field}' field.")
    return value


def verify_plan(plan: Dict[str, Any], expected_theme: Optional[str], max_images: int, allow_ratio: bool) -> List[str]:
    findings: List[str] = []
    if not isinstance(plan, dict):
        return ["Image plan must be a JSON object."]

    theme_id = text(plan.get("theme"))
    if expected_theme and theme_id != expected_theme:
        findings.append(f"Plan theme is '{theme_id}', expected '{expected_theme}'.")
    if not theme_id:
        findings.append("Plan must include a top-level 'theme'.")
        theme: Dict[str, Any] = {}
    else:
        loaded = load_theme(theme_id)
        if loaded is None:
            findings.append(f"Theme '{theme_id}' is not a registered theme JSON file.")
            theme = {}
        else:
            theme = loaded

    default_ratio = text(plan.get("default_aspect_ratio")) or DEFAULT_ASPECT_RATIO
    if default_ratio != DEFAULT_ASPECT_RATIO and not allow_ratio:
        findings.append("Top-level default_aspect_ratio must be 16:9 unless --allow-non-default-ratio is used.")

    images = plan.get("images")
    if not isinstance(images, list):
        findings.append("Plan must include an 'images' array.")
        return findings

    if len(images) > max_images:
        findings.append(f"Image plan contains {len(images)} images; keep the plan at or below {max_images}.")

    if not images:
        reason = text(plan.get("reason"))
        if len(reason) < 12:
            findings.append("A zero-image plan must include a clear top-level 'reason'.")
        return findings

    direction = theme.get("image_direction", {}) if isinstance(theme, dict) else {}
    preferred_types = set(list_text(direction.get("preferred_visual_types")))
    forbidden_terms = set(list_text(direction.get("forbidden")))

    for index, item in enumerate(images, start=1):
        if not isinstance(item, dict):
            findings.append(f"Image item {index} must be an object.")
            continue
        label = f"Image item {index}"

        image_id = require_text(findings, item, "id", label, minimum=4)
        item_theme = text(item.get("theme"))
        if item_theme and item_theme != theme_id:
            findings.append(f"{label} '{image_id}' theme is '{item_theme}', expected '{theme_id}'.")
        require_text(findings, item, "insert_after", label, minimum=4)
        require_text(findings, item, "purpose", label, minimum=10)
        require_text(findings, item, "why_needed", label, minimum=16)
        require_text(findings, item, "theme_fit", label, minimum=12)
        require_text(findings, item, "alt", label, minimum=6)
        require_text(findings, item, "caption", label, minimum=8)

        necessity = text(item.get("necessity"))
        if necessity not in ALLOWED_NECESSITY:
            findings.append(f"{label} '{image_id}' must use necessity high or medium; low-value images are rejected.")

        visual_type = text(item.get("visual_type"))
        if visual_type not in ALLOWED_VISUAL_TYPES:
            allowed = ", ".join(sorted(ALLOWED_VISUAL_TYPES))
            findings.append(f"{label} '{image_id}' has invalid visual_type '{visual_type}'. Allowed: {allowed}.")
        elif preferred_types and visual_type not in preferred_types:
            preferred = ", ".join(sorted(preferred_types))
            findings.append(f"{label} '{image_id}' uses visual_type '{visual_type}', outside theme preferred types: {preferred}.")

        aspect_ratio = text(item.get("aspect_ratio")) or default_ratio
        if aspect_ratio != DEFAULT_ASPECT_RATIO and not allow_ratio:
            findings.append(f"{label} '{image_id}' aspect_ratio must be 16:9 unless --allow-non-default-ratio is used.")

        status = text(item.get("status")) or "planned"
        if status not in ALLOWED_STATUS:
            findings.append(f"{label} '{image_id}' has invalid status '{status}'.")

        prompt = require_text(findings, item, "prompt", label, minimum=40)
        if prompt and not TEXT_BAN_RE.search(prompt):
            findings.append(f"{label} '{image_id}' prompt must forbid readable text inside the image.")

        avoid = list_text(item.get("avoid"))
        if not avoid:
            findings.append(f"{label} '{image_id}' must include a non-empty 'avoid' list.")
        elif forbidden_terms and not any(term in forbidden_terms for term in avoid):
            findings.append(f"{label} '{image_id}' avoid list should include at least one theme forbidden visual move.")

        if visual_type == "evidence_figure":
            require_text(findings, item, "source_note", label, minimum=12)

        asset_path = text(item.get("asset_path"))
        if status == "generated":
            if not asset_path:
                findings.append(f"{label} '{image_id}' status is generated but asset_path is missing.")
            elif ABSOLUTE_PATH_RE.search(asset_path):
                findings.append(f"{label} '{image_id}' asset_path should be a portable relative path or URL.")
        elif asset_path:
            findings.append(f"{label} '{image_id}' has asset_path but status is not generated.")

    return findings


def main() -> None:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    plan = json.loads(input_path.read_text(encoding="utf-8"))
    findings = verify_plan(plan, args.theme, args.max_images, args.allow_non_default_ratio)
    if findings:
        for finding in findings:
            print(f"VERIFY: {finding}", file=sys.stderr)
        raise SystemExit(1)
    print(f"Verified image plan: {input_path}")


if __name__ == "__main__":
    main()
