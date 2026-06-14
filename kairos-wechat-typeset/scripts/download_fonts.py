#!/usr/bin/env python3
"""Download and verify fonts for kairos-wechat-typeset."""

import hashlib
import json
import sys
import urllib.request
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parents[1] / "assets" / "fonts"

FONTS = [
    {
        "id": "noto-sans-sc-regular",
        "name": "Noto Sans SC",
        "category": "sans-serif",
        "weight": "400",
        "style": "normal",
        "cjk": True,
        "license": "SIL OFL 1.1",
        "source": "https://cdn.jsdelivr.net/fontsource/fonts/noto-sans-sc@latest/chinese-simplified-400-normal.woff2",
        "dest": "sans-serif/noto-sans-sc/NotoSansSC-Regular.woff2",
    },
    {
        "id": "noto-sans-sc-medium",
        "name": "Noto Sans SC",
        "category": "sans-serif",
        "weight": "500",
        "style": "normal",
        "cjk": True,
        "license": "SIL OFL 1.1",
        "source": "https://cdn.jsdelivr.net/fontsource/fonts/noto-sans-sc@latest/chinese-simplified-500-normal.woff2",
        "dest": "sans-serif/noto-sans-sc/NotoSansSC-Medium.woff2",
    },
    {
        "id": "noto-serif-sc-regular",
        "name": "Noto Serif SC",
        "category": "serif",
        "weight": "400",
        "style": "normal",
        "cjk": True,
        "license": "SIL OFL 1.1",
        "source": "https://cdn.jsdelivr.net/fontsource/fonts/noto-serif-sc@latest/chinese-simplified-400-normal.woff2",
        "dest": "serif/noto-serif-sc/NotoSerifSC-Regular.woff2",
    },
    {
        "id": "noto-serif-sc-semibold",
        "name": "Noto Serif SC",
        "category": "serif",
        "weight": "600",
        "style": "normal",
        "cjk": True,
        "license": "SIL OFL 1.1",
        "source": "https://cdn.jsdelivr.net/fontsource/fonts/noto-serif-sc@latest/chinese-simplified-600-normal.woff2",
        "dest": "serif/noto-serif-sc/NotoSerifSC-SemiBold.woff2",
    },
    {
        "id": "inter-regular",
        "name": "Inter",
        "category": "sans-serif",
        "weight": "400",
        "style": "normal",
        "cjk": False,
        "license": "SIL OFL 1.1",
        "source": "https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-400-normal.woff2",
        "dest": "sans-serif/inter/Inter-Regular.woff2",
    },
    {
        "id": "inter-medium",
        "name": "Inter",
        "category": "sans-serif",
        "weight": "500",
        "style": "normal",
        "cjk": False,
        "license": "SIL OFL 1.1",
        "source": "https://cdn.jsdelivr.net/fontsource/fonts/inter@latest/latin-500-normal.woff2",
        "dest": "sans-serif/inter/Inter-Medium.woff2",
    },
    {
        "id": "playfair-display-regular",
        "name": "Playfair Display",
        "category": "serif",
        "weight": "400",
        "style": "normal",
        "cjk": False,
        "license": "SIL OFL 1.1",
        "source": "https://cdn.jsdelivr.net/fontsource/fonts/playfair-display@latest/latin-400-normal.woff2",
        "dest": "serif/playfair-display/PlayfairDisplay-Regular.woff2",
    },
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def download_font(font: dict) -> bool:
    dest_path = ASSETS_DIR / font["dest"]
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    if dest_path.exists():
        print(f"  [skip] {font['dest']} (already exists)")
        return True

    print(f"  [download] {font['id']} -> {font['dest']}")
    try:
        urllib.request.urlretrieve(font["source"], str(dest_path))
    except Exception as e:
        print(f"  [error] Failed to download {font['id']}: {e}", file=sys.stderr)
        return False

    print(f"  [ok] {font['dest']}")
    return True


def update_registry():
    registry_path = ASSETS_DIR / "fonts.json"
    if registry_path.exists():
        existing = json.loads(registry_path.read_text(encoding="utf-8"))
    else:
        existing = {"fonts": []}

    existing_ids = {f["id"] for f in existing["fonts"]}

    for font in FONTS:
        dest_path = ASSETS_DIR / font["dest"]
        if not dest_path.exists():
            continue

        entry = {
            "id": font["id"],
            "name": font["name"],
            "category": font["category"],
            "weight": font["weight"],
            "style": font["style"],
            "designer": "Google" if "noto" in font["id"] else ("Rasmus Andersson" if "inter" in font["id"] else "Claus Eggers Sørensen"),
            "license": font["license"],
            "cjk": font["cjk"],
            "path": font["dest"],
            "format": "woff2",
        }

        if font["id"] in existing_ids:
            existing["fonts"] = [
                entry if f["id"] == font["id"] else f for f in existing["fonts"]
            ]
        else:
            existing["fonts"].append(entry)
            existing_ids.add(font["id"])

    registry_path.write_text(
        json.dumps(existing, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"\nRegistry updated: {registry_path}")


def main():
    print("Downloading fonts for kairos-wechat-typeset...\n")
    all_ok = True
    for font in FONTS:
        if not download_font(font):
            all_ok = False

    if all_ok:
        update_registry()
        print("\nAll fonts downloaded successfully.")
    else:
        print("\nSome fonts failed to download.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
