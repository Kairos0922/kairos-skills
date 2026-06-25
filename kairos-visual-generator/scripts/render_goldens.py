"""
Render golden examples from HTML to PNG using Playwright.

Usage:
    python3 scripts/render_goldens.py
    python3 scripts/render_goldens.py --folder editorial-magazine
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

GOLDENS_DIR = Path(__file__).parent.parent / "goldens"
SHOWCASE_DIR = Path(__file__).parent.parent / "assets" / "showcase"


def _ensure_playwright():
    """Import sync_playwright, auto-installing Playwright + Chromium on first use."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing playwright...", file=sys.stderr)
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright
    return sync_playwright

# Map folder names to HTML files and output PNG names
EXAMPLES = {
    "editorial-magazine": ("editorial-cover.html", "editorial-magazine.png"),
    "swiss-consulting": ("swiss-mechanism.html", "swiss-consulting.png"),
    "mondrian-art": ("mondrian-poster.html", "mondrian-art.png"),
    "ticket-boarding-pass": ("boarding-pass.html", "ticket-boarding-pass.png"),
}


def render_golden(folder: str, browser) -> bool:
    """Render a single golden example to PNG."""
    if folder not in EXAMPLES:
        print(f"SKIP: Unknown folder '{folder}'")
        return False

    html_file, png_name = EXAMPLES[folder]
    html_path = GOLDENS_DIR / folder / html_file
    png_path = SHOWCASE_DIR / png_name

    if not html_path.exists():
        print(f"SKIP: {html_path} not found")
        return False

    page = browser.new_page(viewport={"width": 1200, "height": 1600})
    page.goto(f"file://{html_path}")
    page.wait_for_load_state("networkidle")

    # Screenshot the card element (first child of body)
    card = page.locator("body > div").first
    card.screenshot(path=str(png_path))

    page.close()
    print(f"OK: {png_name}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Render golden examples to PNG")
    parser.add_argument("--folder", help="Render specific folder only")
    args = parser.parse_args()

    SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)

    sync_playwright = _ensure_playwright()
    with sync_playwright() as p:
        browser = p.chromium.launch()

        if args.folder:
            render_golden(args.folder, browser)
        else:
            for folder in EXAMPLES:
                render_golden(folder, browser)

        browser.close()

    print(f"\nDone! Files saved to: {SHOWCASE_DIR}")


if __name__ == "__main__":
    main()
