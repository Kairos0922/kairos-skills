"""
Render pipeline: deterministic HTML/CSS → PNG generation.

All steps are deterministic — AI does not participate in rendering.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass
class RenderConfig:
    """Configuration for rendering."""
    style_id: str
    theme_id: str
    skeleton_id: str
    ratio: str
    tokens: dict
    css_mapping: dict
    brief: dict


def load_style(style_id: str, styles_dir: Path) -> dict:
    """Load style configuration from styles directory."""
    style_dir = styles_dir / style_id
    if not style_dir.exists():
        raise FileNotFoundError(f"Style '{style_id}' not found at {style_dir}")

    with open(style_dir / "composition.json", "r", encoding="utf-8") as f:
        composition = json.load(f)

    return {"id": style_id, "dir": style_dir, "composition": composition}


def load_theme_tokens(theme_id: str, themes_dir: Path) -> dict:
    """Load theme token file."""
    token_path = themes_dir / f"{theme_id}.json"
    if not token_path.exists():
        raise FileNotFoundError(f"Theme '{theme_id}' not found at {token_path}")

    with open(token_path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_css_variables(tokens: dict, css_mapping: dict) -> dict[str, str]:
    """Build CSS variables from token values and css_mapping.

    Returns dict of CSS variable name → resolved value.
    """
    color_map = tokens.get("color_map", {})
    result = {}

    for css_var, token_key in css_mapping.items():
        if token_key in color_map:
            result[css_var] = color_map[token_key]
        else:
            result[css_var] = token_key

    return result


def compose_html(
    skeleton: dict,
    tokens: dict,
    css_vars: dict[str, str],
    brief: dict,
    typography: dict,
    grid: dict,
    texture: dict,
) -> str:
    """Compose HTML/CSS from skeleton and tokens.

    Deterministic — no AI judgment involved.
    """
    # This is a placeholder for the actual HTML generation logic.
    # Real implementation would use the skeleton structure, typography,
    # grid, and texture rules to generate precise HTML/CSS.
    return "<!-- rendered HTML will be generated here -->"


def render_to_png(html: str, ratio: str) -> str:
    """Render HTML to PNG using browser screenshot.

    Returns path to generated PNG.
    """
    # Placeholder — actual implementation uses Playwright or similar
    return "output.png"


def run_qa(image_path: str, brief: dict, composition: dict, style_dir: Path) -> dict:
    """Run QA checks on rendered output.

    Returns {"passed": bool, "errors": list, "warnings": list}.
    """
    from shared.verify import run_full_qa

    result = run_full_qa(
        style_id=brief.get("style_id", ""),
        brief=brief,
        composition=composition,
        image_path=image_path,
    )

    return {"passed": result.passed, "errors": result.errors, "warnings": result.warnings}


def render_card(brief: dict, styles_dir: Path) -> str:
    """Full render pipeline: Brief → PNG.

    All steps are deterministic.
    """
    # 1. Load style
    style = load_style(brief["style_id"], styles_dir)
    composition = style["composition"]

    # 2. Load theme tokens
    themes_dir = style["dir"] / "themes"
    tokens = load_theme_tokens(brief["theme_id"], themes_dir)

    # 3. Build CSS variables from css_mapping
    css_mapping = tokens.get("css_mapping", {})
    css_vars = build_css_variables(tokens, css_mapping)

    # 4. Select skeleton
    skeletons = composition.get("layout_skeletons", [])
    skeleton = next(
        (s for s in skeletons if s["id"] == brief.get("layout_skeleton")),
        skeletons[0] if skeletons else {},
    )

    # 5. Generate HTML/CSS
    html = compose_html(
        skeleton=skeleton,
        tokens=tokens,
        css_vars=css_vars,
        brief=brief,
        typography=tokens.get("typography", {}),
        grid=tokens.get("grid", {}),
        texture=tokens.get("texture", {}),
    )

    # 6. Render to PNG
    png_path = render_to_png(html, brief.get("ratio", "4:5"))

    # 7. QA
    qa_result = run_qa(png_path, brief, composition, style["dir"])
    if not qa_result["passed"]:
        raise RuntimeError(f"QA failed: {qa_result['errors']}")

    return png_path
