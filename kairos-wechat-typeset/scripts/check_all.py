#!/usr/bin/env python3
"""Run kairos-wechat-typeset validation commands."""

from __future__ import annotations

import argparse
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    name: str
    command: List[str]
    group: str


CHECKS = [
    Check("registered themes", ["python3", "scripts/render.py", "--list-themes"], "smoke"),
    Check("versioned workflow smoke", ["python3", "scripts/typeset.py", "--check"], "smoke"),
    Check(
        "image plan contract",
        [
            "python3",
            "scripts/verify_image_plan.py",
            "--input",
            "fixtures/image-plan.sample.json",
            "--theme",
            "tech",
        ],
        "smoke",
    ),
    Check("song html verify", ["python3", "scripts/verify.py", "--input", "goldens/song-style.html"], "theme"),
    Check(
        "song visual audit",
        [
            "python3",
            "scripts/audit_visual.py",
            "--input",
            "goldens/song-style.html",
            "--allowed-font-size",
            "12px",
            "--allowed-font-size",
            "14px",
            "--allowed-font-size",
            "16px",
            "--allowed-font-size",
            "25px",
            "--allowed-font-size",
            "28px",
            "--max-margin-px",
            "48",
        ],
        "theme",
    ),
    Check(
        "wending html verify",
        [
            "python3",
            "scripts/verify.py",
            "--input",
            "goldens/wending-style.html",
            "--source",
            "fixtures/wending-style-system.md",
            "--theme",
            "wending",
        ],
        "theme",
    ),
    Check(
        "wending visual audit",
        [
            "python3",
            "scripts/audit_visual.py",
            "--input",
            "goldens/wending-style.html",
            "--allowed-font-size",
            "14px",
            "--allowed-font-size",
            "16px",
            "--allowed-font-size",
            "18px",
            "--allowed-font-size",
            "22px",
            "--allowed-font-size",
            "28px",
            "--allowed-font-size",
            "32px",
            "--allowed-font-size",
            "42px",
            "--max-margin-px",
            "48",
        ],
        "theme",
    ),
    Check(
        "tech html verify",
        [
            "python3",
            "scripts/verify.py",
            "--input",
            "goldens/tech-style.html",
            "--source",
            "fixtures/tech-style-system.md",
            "--theme",
            "tech",
        ],
        "theme",
    ),
    Check(
        "tech visual audit",
        [
            "python3",
            "scripts/audit_visual.py",
            "--input",
            "goldens/tech-style.html",
            "--allowed-font-size",
            "12px",
            "--allowed-font-size",
            "13px",
            "--allowed-font-size",
            "14px",
            "--allowed-font-size",
            "16px",
            "--allowed-font-size",
            "18px",
            "--allowed-font-size",
            "22px",
            "--allowed-font-size",
            "28px",
            "--allowed-font-size",
            "32px",
            "--max-margin-px",
            "48",
        ],
        "theme",
    ),
    Check(
        "wisme html verify",
        [
            "python3",
            "scripts/verify.py",
            "--input",
            "goldens/wisme-style.html",
            "--source",
            "fixtures/wisme-style-system.md",
            "--theme",
            "wisme",
        ],
        "theme",
    ),
    Check(
        "wisme visual audit",
        [
            "python3",
            "scripts/audit_visual.py",
            "--input",
            "goldens/wisme-style.html",
            "--allowed-font-size",
            "10px",
            "--allowed-font-size",
            "11px",
            "--allowed-font-size",
            "12px",
            "--allowed-font-size",
            "13px",
            "--allowed-font-size",
            "15px",
            "--allowed-font-size",
            "16px",
            "--allowed-font-size",
            "18px",
            "--allowed-font-size",
            "24px",
            "--allowed-font-size",
            "32px",
            "--max-margin-px",
            "48",
        ],
        "theme",
    ),
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run kairos-wechat-typeset validation commands.")
    parser.add_argument("--smoke", action="store_true", help="Run only fast product smoke checks.")
    parser.add_argument("--themes", action="store_true", help="Run only theme golden checks.")
    return parser.parse_args()


def selected_checks(args: argparse.Namespace) -> Iterable[Check]:
    if args.smoke:
        return [check for check in CHECKS if check.group == "smoke"]
    if args.themes:
        return [check for check in CHECKS if check.group == "theme"]
    return CHECKS


def main() -> None:
    args = parse_args()
    checks = list(selected_checks(args))
    failures = 0
    for index, check in enumerate(checks, start=1):
        print(f"[{index}/{len(checks)}] {check.name}", flush=True)
        print("  " + " ".join(check.command), flush=True)
        result = subprocess.run(check.command, cwd=ROOT, check=False)
        if result.returncode:
            failures += 1
            print(f"  failed with exit code {result.returncode}", file=sys.stderr)
        else:
            print("  ok", flush=True)
    if failures:
        raise SystemExit(f"{failures} validation check(s) failed.")
    print(f"All {len(checks)} validation check(s) passed.")


if __name__ == "__main__":
    main()
