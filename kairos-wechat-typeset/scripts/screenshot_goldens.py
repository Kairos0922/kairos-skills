#!/usr/bin/env python3
"""Screenshot golden HTML files into showcase PNGs using Playwright."""

from __future__ import annotations

import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
GOLDENS_DIR = SKILL_ROOT / "goldens"
SHOWCASE_DIR = SKILL_ROOT / "assets" / "showcase"

THEMES = ["song", "wending", "tech", "wisme"]

VIEWPORT_WIDTH = 430
DEVICE_SCALE = 2
TOP_CROP = 0
BOTTOM_CROP = 0


def main() -> int:
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("Installing playwright...", file=sys.stderr)
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright", "-q"])
        subprocess.check_call([sys.executable, "-m", "playwright", "install", "chromium"])
        from playwright.sync_api import sync_playwright

    SHOWCASE_DIR.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()

        for theme in THEMES:
            html_path = GOLDENS_DIR / f"{theme}-style.html"
            png_path = SHOWCASE_DIR / f"{theme}-preview.png"

            if not html_path.exists():
                print(f"SKIP: {html_path} not found")
                continue

            page = browser.new_page(
                viewport={"width": VIEWPORT_WIDTH, "height": 900},
                device_scale_factor=DEVICE_SCALE,
            )
            page.goto(f"file://{html_path.resolve()}")
            page.wait_for_load_state("networkidle")

            # Get full page height
            body_height = page.evaluate("document.body.scrollHeight")

            # Screenshot the full body
            page.set_viewport_size({"width": VIEWPORT_WIDTH, "height": body_height})
            page.screenshot(
                path=str(png_path),
                full_page=True,
                type="png",
            )

            actual_height = png_path.stat().st_size
            print(f"OK: {png_path.name} ({actual_height // 1024}KB, {body_height}px tall)")

            page.close()

        browser.close()

    print(f"\nDone. {len(THEMES)} showcase PNGs saved to {SHOWCASE_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
