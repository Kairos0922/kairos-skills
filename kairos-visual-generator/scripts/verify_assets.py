#!/usr/bin/env python3
"""Verify that rendering pipeline has no external CDN dependencies.

Scans all HTML, CSS, JSON, and Python files for CDN references.
Excludes known-safe files: download_fonts.py, README.md badges.
"""

import re
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]

CDN_PATTERNS = [
    re.compile(r"https?://cdn\.jsdelivr\.net"),
    re.compile(r"https?://fonts\.googleapis\.com"),
    re.compile(r"https?://fonts\.gstatic\.com"),
    re.compile(r"https?://placehold\.co"),
]

SCAN_EXTENSIONS = {".html", ".css", ".json", ".py", ".md"}

EXCLUDE_FILES = {"download_fonts.py", "README.md"}


def scan_file(path: Path) -> list[tuple[int, str, str]]:
    """Scan a file for CDN references. Returns list of (line_number, pattern, line_content)."""
    findings = []
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, PermissionError):
        return findings

    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern in CDN_PATTERNS:
            if pattern.search(line):
                findings.append((line_num, pattern.pattern, line.strip()[:120]))
                break

    return findings


def main():
    print(f"Scanning {SKILL_ROOT} for external CDN references...\n")

    all_findings = []
    scanned = 0

    for path in SKILL_ROOT.rglob("*"):
        if path.is_dir():
            continue
        if path.suffix not in SCAN_EXTENSIONS:
            continue
        if path.name in EXCLUDE_FILES:
            continue
        if "__pycache__" in str(path):
            continue
        if ".git" in str(path):
            continue

        scanned += 1
        findings = scan_file(path)
        if findings:
            rel_path = path.relative_to(SKILL_ROOT)
            for line_num, pattern, line_content in findings:
                all_findings.append((str(rel_path), line_num, pattern, line_content))

    print(f"Scanned {scanned} files.\n")

    if all_findings:
        print(f"ERROR: Found {len(all_findings)} external CDN reference(s):\n")
        for file_path, line_num, pattern, content in all_findings:
            print(f"  {file_path}:{line_num}")
            print(f"    Pattern: {pattern}")
            print(f"    Content: {content}")
            print()
        sys.exit(1)
    else:
        print("OK: No external CDN references found. Skill is fully offline-capable.")
        sys.exit(0)


if __name__ == "__main__":
    main()
