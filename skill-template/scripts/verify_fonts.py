#!/usr/bin/env python3
"""Verify all declared font files exist and are readable."""

import json
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
FONTS_DIR = SKILL_ROOT / "assets" / "fonts"


def main():
    registry_path = FONTS_DIR / "fonts.json"
    if not registry_path.exists():
        print("ERROR: Registry not found: {}".format(registry_path), file=sys.stderr)
        sys.exit(1)

    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    fonts = registry.get("fonts", [])

    print("Checking {} font entries...\n".format(len(fonts)))

    all_ok = True
    for font in fonts:
        font_path = FONTS_DIR / font["path"]
        if not font_path.exists():
            print("  MISSING: {} -> {}".format(font["id"], font["path"]))
            all_ok = False
            continue

        size = font_path.stat().st_size
        if size == 0:
            print("  EMPTY: {} -> {}".format(font["id"], font["path"]))
            all_ok = False
            continue

        try:
            with open(font_path, "rb") as f:
                f.read(16)
            print("  OK: {} ({:,} bytes)".format(font["id"], size))
        except Exception as e:
            print("  READ ERROR: {} -> {}".format(font["id"], e))
            all_ok = False

    print()
    if all_ok:
        print("All font files verified.")
        sys.exit(0)
    else:
        print("Some font files are missing or invalid.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
