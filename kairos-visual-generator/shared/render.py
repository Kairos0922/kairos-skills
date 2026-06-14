"""
Render pipeline: deterministic HTML/CSS → PNG generation.

All steps are deterministic — AI does not participate in rendering.
"""

import json
import re
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


SKILL_ROOT = Path(__file__).resolve().parents[1]
FONTS_CSS_PATH = SKILL_ROOT / "assets" / "fonts" / "fonts.css"

# Output format constants
OUTPUT_FORMAT = "PNG-32"  # 32位无损，24位RGB + 8位alpha
OUTPUT_FORMAT_WEBP = "WebP"  # 可选，用户系统支持时使用


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


RATIO_DIMENSIONS = {
    "4:5": (1080, 1350),
    "1:1": (1080, 1080),
    "3:4": (1080, 1440),
    "16:9": (1600, 900),
    "21:9": (2100, 840),
    "5:2": (1500, 600),
    "2.35:1": (1920, 817),
    "9:16": (1080, 1920),
    "4:3": (1440, 1080),
}

RATIO_SCALEDOWN = {
    "4:5": 0.556,
    "1:1": 0.556,
    "3:4": 0.52,
    "16:9": 0.375,
    "21:9": 0.32,
    "5:2": 0.375,
    "2.35:1": 0.375,
    "9:16": 0.3,
    "4:3": 0.45,
}


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


def load_local_font_css() -> str:
    """Load the locally generated @font-face CSS."""
    if FONTS_CSS_PATH.exists():
        return FONTS_CSS_PATH.read_text(encoding="utf-8")
    return ""


def _esc(text: str) -> str:
    """HTML-escape text."""
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def _font_family_display_zh(tokens: dict) -> str:
    return tokens.get("typography", {}).get(
        "display_zh", '"Noto Sans SC", "PingFang SC", sans-serif'
    )


def _font_family_display_en(tokens: dict) -> str:
    return tokens.get("typography", {}).get(
        "display_en", '"Inter", "Helvetica Neue", sans-serif'
    )


def _display_weight(tokens: dict) -> int:
    return tokens.get("typography", {}).get("display_weight", 540)


def _body_weight(tokens: dict) -> int:
    return tokens.get("typography", {}).get("body_weight", 420)


def _body_size(tokens: dict) -> int:
    return tokens.get("typography", {}).get("body_size", 19)


def _grid_margin(tokens: dict) -> str:
    return tokens.get("grid", {}).get("margin", "80px")


def _grid_gutter(tokens: dict) -> str:
    return tokens.get("grid", {}).get("gutter", "24px")


def _display_size_for_ratio(brief: dict, tokens: dict) -> int:
    ratio = brief.get("ratio", "4:5")
    scale_map = {
        "4:5": [56, 64, 72, 80],
        "1:1": [48, 56, 64, 72],
        "3:4": [58, 68, 78, 88],
        "16:9": [42, 48, 56, 64],
        "21:9": [36, 42, 48, 56],
        "5:2": [36, 42, 48, 56],
        "2.35:1": [32, 38, 44, 50],
        "9:16": [38, 44, 50, 58],
        "4:3": [44, 52, 60, 68],
    }
    sizes = scale_map.get(ratio, [56, 64, 72, 80])
    density = brief.get("content_density", "cover")
    if density == "cover":
        return sizes[3]
    if density == "light":
        return sizes[2]
    if density == "standard":
        return sizes[1]
    return sizes[0]


def _subtitle_size_for_ratio(brief: dict) -> int:
    ratio = brief.get("ratio", "4:5")
    scale_map = {
        "4:5": [22, 24, 28, 32],
        "1:1": [20, 22, 24, 28],
        "3:4": [22, 24, 28, 32],
        "16:9": [18, 20, 22, 24],
        "21:9": [16, 18, 20, 22],
        "5:2": [16, 18, 20, 22],
        "2.35:1": [14, 16, 18, 20],
        "9:16": [16, 18, 20, 22],
        "4:3": [20, 22, 24, 28],
    }
    sizes = scale_map.get(ratio, [22, 24, 28, 32])
    density = brief.get("content_density", "cover")
    if density == "cover":
        return sizes[2]
    if density == "light":
        return sizes[1]
    return sizes[0]


def _body_size_for_ratio(brief: dict, tokens: dict) -> int:
    base = _body_size(tokens)
    ratio = brief.get("ratio", "4:5")
    scale = RATIO_SCALEDOWN.get(ratio, 0.556)
    return max(14, int(base * scale))


def _canvas_dimensions(ratio: str) -> tuple[int, int]:
    return RATIO_DIMENSIONS.get(ratio, (1080, 1350))


def _scaled_dimensions(ratio: str) -> tuple[int, int]:
    w, h = _canvas_dimensions(ratio)
    scale = RATIO_SCALEDOWN.get(ratio, 0.556)
    return int(w * scale), int(h * scale)


def _split_text_lines(text: str, max_chars: int = 12) -> list[str]:
    """Split CJK-heavy text into display-friendly lines."""
    if len(text) <= max_chars:
        return [text]
    mid = len(text) // 2
    left = text[:mid]
    right = text[mid:]
    if len(left) > max_chars and len(right) > max_chars:
        third = len(text) // 3
        return [text[:third], text[third:third*2], text[third*2:]]
    return [left, right]


def _wrap_body_text(text: str, max_chars: int = 28) -> str:
    """Wrap body text for card display."""
    if len(text) <= max_chars:
        return text
    lines = []
    while text:
        if len(text) <= max_chars:
            lines.append(text)
            break
        cut = max_chars
        while cut > 0 and text[cut - 1] not in "，。、；：！？ ":
            cut -= 1
        if cut == 0:
            cut = max_chars
        lines.append(text[:cut])
        text = text[cut:]
    return "<br>".join(lines)


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
    Generates a self-contained HTML document with local @font-face.
    """
    ratio = brief.get("ratio", "4:5")
    w, h = _scaled_dimensions(ratio)
    style_id = brief.get("style_id", "swiss")
    theme_name = brief.get("theme_id", "")

    font_css = load_local_font_css()

    css_var_block = "    :root {\n"
    for var_name, value in css_vars.items():
        css_var_block += f"      {var_name}: {value};\n"
    css_var_block += "    }"

    ink = css_vars.get("--v-primary", css_vars.get("--ink", "#0a0a0b"))
    paper = css_vars.get("--v-bg", css_vars.get("--paper", "#f1efea"))
    muted = css_vars.get("--v-muted", css_vars.get("--muted", "#6f767d"))
    accent = css_vars.get("--v-accent", css_vars.get("--accent", "#002FA7"))
    line_color = css_vars.get("--v-line", css_vars.get("--line", "rgba(10,10,11,0.16)"))

    font_zh = _font_family_display_zh(tokens)
    font_en = _font_family_display_en(tokens)
    dw = _display_weight(tokens)
    bw = _body_weight(tokens)
    display_size = _display_size_for_ratio(brief, tokens)
    subtitle_size = _subtitle_size_for_ratio(brief)
    body_sz = _body_size_for_ratio(brief, tokens)
    margin = _grid_margin(tokens)
    gutter = _grid_gutter(tokens)

    core_word = brief.get("core_word", "")
    title_full = brief.get("title_full", "")
    subtitle = brief.get("subtitle", "")
    text_reconstruction = brief.get("text_reconstruction", "")
    skeleton_id = skeleton.get("id", "S01")
    skeleton_name = skeleton.get("name", "Custom")

    title_lines = _split_text_lines(core_word, max_chars=6 if len(core_word) > 8 else 10)
    title_html = "<br>".join(_esc(line) for line in title_lines)

    subtitle_text = subtitle or title_full
    body_text = _wrap_body_text(text_reconstruction, max_chars=int(w * 0.055))
    body_text_html = body_text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    body_text_html = body_text_html.replace("&lt;br&gt;", "<br>")

    modules = brief.get("modules", [])
    if not modules and text_reconstruction:
        parts = [p.strip() for p in re.split(r"[。；，]", text_reconstruction) if p.strip()]
        modules = [{"title": "", "content": p} for p in parts[:4]]

    modules_html = ""
    if modules:
        module_count = min(len(modules), 4)
        grid_cols = min(module_count, 4)
        modules_html = f"""
      <div class="modules" style="display: grid; grid-template-columns: repeat({grid_cols}, 1fr); gap: {gutter}; margin-bottom: 16px;">
"""
        for m in modules[:module_count]:
            m_title = _esc(m.get("title", ""))
            m_content = _esc(m.get("content", ""))
            modules_html += f"""        <div class="module" style="padding: 12px; border-top: 2px solid {accent};">
          <div class="module-title" style="font-size: 11px; color: {ink}; font-weight: 600; margin-bottom: 6px;">{m_title}</div>
          <div class="module-content" style="font-size: 9px; color: {muted}; line-height: 1.4;">{m_content}</div>
        </div>
"""
        modules_html += "      </div>\n"

    tags = brief.get("tags", [])
    tags_html = ""
    if tags:
        tag_items = " · ".join(_esc(t) for t in tags[:4])
        font_en_escaped = font_en.replace('"', "&quot;")
        tags_html = f"""
    <div class="header-label" style="font-family: {font_en_escaped}; font-size: 9px; color: {accent}; letter-spacing: 0.2em; text-transform: uppercase; font-weight: 500; margin-bottom: 6px;">{tag_items}</div>"""

    footer_left = style_id.upper().replace("-", " ")
    footer_right = brief.get("context", "CONFIDENTIAL")

    canvas_bg = "#e8e8e8"
    if texture.get("background") == "paper":
        canvas_bg = "#e8e4dc"

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <style>
{font_css}

{css_var_block}

    * {{ margin: 0; padding: 0; box-sizing: border-box; }}

    body {{
      background: {canvas_bg};
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      padding: 40px;
    }}

    .card {{
      width: {w}px;
      height: {h}px;
      background: {paper};
      position: relative;
      display: flex;
      flex-direction: column;
      font-family: {font_zh};
      overflow: hidden;
    }}

    .header {{
      padding: 28px 36px 20px;
      border-bottom: 1px solid {line_color};
    }}

    .main-content {{
      flex: 1;
      display: flex;
      flex-direction: column;
      padding: 24px 36px;
      justify-content: center;
    }}

    .hero-title {{
      font-size: {display_size}px;
      color: {ink};
      font-weight: {dw};
      line-height: 1.1;
      margin-bottom: 16px;
    }}

    .hero-subtitle {{
      font-size: {subtitle_size}px;
      color: {muted};
      font-weight: {max(300, bw - 100)};
      line-height: 1.3;
      margin-bottom: 24px;
    }}

    .hero-body {{
      font-size: {body_sz}px;
      color: {muted};
      font-weight: {bw};
      line-height: 1.5;
      max-width: 85%;
    }}

    .implication {{
      padding: 12px;
      background: rgba({_hex_to_rgb(accent)}, 0.04);
      border-left: 2px solid {accent};
      margin-bottom: 8px;
    }}

    .implication-text {{
      font-size: 11px;
      color: {ink};
      font-weight: 500;
      line-height: 1.4;
    }}

    .footer {{
      padding: 12px 36px;
      border-top: 1px solid {line_color};
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .footer-left {{
      font-family: {font_en};
      font-size: 8px;
      color: {muted};
      letter-spacing: 0.15em;
      text-transform: uppercase;
    }}

    .footer-right {{
      font-family: {font_en};
      font-size: 8px;
      color: {muted};
    }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
{tags_html}
      <h1 class="hero-title">{title_html}</h1>
    </div>

    <div class="main-content">
      <div class="hero-subtitle">{_esc(subtitle_text)}</div>
      <div class="hero-body">{body_text_html}</div>
{modules_html}
    </div>

    <div class="footer">
      <span class="footer-left">{_esc(footer_left)}</span>
      <span class="footer-right">{_esc(footer_right)}</span>
    </div>
  </div>
</body>
</html>"""

    return html


def _hex_to_rgb(hex_color: str) -> str:
    """Convert #RRGGBB to R,G,B."""
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return "0,0,0"
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return f"{r},{g},{b}"


def render_to_png(html: str, ratio: str, output_path: str) -> str:
    """Render HTML to PNG using Playwright browser screenshot.

    Returns path to generated PNG.
    """
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        raise RuntimeError(
            "Playwright is required for PNG rendering. "
            "Install with: pip install playwright && playwright install chromium"
        )

    w, h = _canvas_dimensions(ratio)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": w + 200, "height": h + 200})
        page.set_content(html, wait_until="networkidle")
        page.wait_for_timeout(500)

        card = page.query_selector(".card")
        if card:
            card.screenshot(path=output_path)
        else:
            page.screenshot(path=output_path, full_page=True)

        browser.close()

    return output_path


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


def render_card(brief: dict, styles_dir: Path, output_dir: Optional[Path] = None) -> str:
    """Full render pipeline: Brief → PNG.

    All steps are deterministic.
    """
    if output_dir is None:
        output_dir = Path.home() / ".visual-generator" / brief.get("core_word", "output")
    output_dir.mkdir(parents=True, exist_ok=True)

    style = load_style(brief["style_id"], styles_dir)
    composition = style["composition"]

    themes_dir = style["dir"] / "themes"
    tokens = load_theme_tokens(brief["theme_id"], themes_dir)

    css_mapping = tokens.get("css_mapping", {})
    css_vars = build_css_variables(tokens, css_mapping)

    skeletons = composition.get("layout_skeletons", [])
    skeleton = next(
        (s for s in skeletons if s["id"] == brief.get("layout_skeleton")),
        skeletons[0] if skeletons else {},
    )

    html = compose_html(
        skeleton=skeleton,
        tokens=tokens,
        css_vars=css_vars,
        brief=brief,
        typography=tokens.get("typography", {}),
        grid=tokens.get("grid", {}),
        texture=tokens.get("texture", {}),
    )

    html_path = output_dir / "output.html"
    html_path.write_text(html, encoding="utf-8")

    png_path = str(output_dir / "output.png")
    render_to_png(html, brief.get("ratio", "4:5"), png_path)

    qa_result = run_qa(png_path, brief, composition, style["dir"])
    if not qa_result["passed"]:
        raise RuntimeError(f"QA failed: {qa_result['errors']}")

    return png_path
