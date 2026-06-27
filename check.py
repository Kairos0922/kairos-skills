#!/usr/bin/env python3
"""Kairos Skills 仓库检查器。

自动发现所有 skill 目录并验证它们。加一个新 skill 不需要改本文件——
丢一个含 SKILL.md 的目录进来即可。

对每个 skill 做两件事:
1. 基线检查（与 skill 形态无关，人人都要过）：
   - 存在 SKILL.md，且 frontmatter 含 name + description
   - 不含私有绝对路径 / 密钥痕迹
2. 若 skill 目录下有可执行的 validate.sh，运行它（skill 自己的深度验证）。

用法:
    python3 check.py            # 检查所有 skill
    python3 check.py --smoke    # 只做基线检查，跳过各 skill 的 validate.sh
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# 扫描这些模式，命中即判为不可移植 / 不该提交的内容。
FORBIDDEN = [
    re.compile(r"/Users/"),
    re.compile(r"/home/[a-z]"),
    re.compile(r"\bAPI_KEY\b"),
    re.compile(r"\bSECRET\b"),
    re.compile(r"\bPASSWORD\b"),
]
# 这些后缀的文本文件才扫描私有路径/密钥。
SCAN_SUFFIXES = {".py", ".md", ".json", ".sh", ".css", ".txt", ".yml", ".yaml"}
SKIP_DIRS = {"__pycache__", ".git", "node_modules", "assets", "goldens", "fixtures"}


def find_skills() -> list[Path]:
    """一个 skill = 直接含 SKILL.md 的顶级目录。"""
    return sorted(p.parent for p in ROOT.glob("*/SKILL.md"))


def parse_frontmatter(text: str) -> dict | None:
    """极简 YAML frontmatter 解析，只取顶层 key，够用即可。"""
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    keys = {}
    for line in text[3:end].splitlines():
        m = re.match(r"^([a-zA-Z_][\w-]*):", line)
        if m:
            keys[m.group(1)] = True
    return keys


def check_baseline(skill: Path) -> list[str]:
    errors = []
    skill_md = skill / "SKILL.md"
    fm = parse_frontmatter(skill_md.read_text(encoding="utf-8"))
    if fm is None:
        errors.append("SKILL.md 缺少 YAML frontmatter")
    else:
        for key in ("name", "description"):
            if key not in fm:
                errors.append(f"SKILL.md frontmatter 缺少 '{key}'")

    for path in skill.rglob("*"):
        if not path.is_file() or path.suffix not in SCAN_SUFFIXES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(skill).parts):
            continue
        content = path.read_text(encoding="utf-8", errors="ignore")
        for pat in FORBIDDEN:
            if pat.search(content):
                rel = path.relative_to(ROOT)
                errors.append(f"{rel} 命中禁止模式 /{pat.pattern}/")
    return errors


def run_validate_sh(skill: Path) -> tuple[bool, str]:
    script = skill / "validate.sh"
    if not script.exists():
        return True, "无 validate.sh，跳过深度验证"
    proc = subprocess.run(
        ["bash", "validate.sh"], cwd=skill, capture_output=True, text=True
    )
    ok = proc.returncode == 0
    return ok, (proc.stdout + proc.stderr).strip()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--smoke", action="store_true", help="只做基线检查")
    args = parser.parse_args()

    skills = find_skills()
    if not skills:
        print("未发现任何 skill（顶级目录下无 SKILL.md）")
        return 1

    failed = False
    for skill in skills:
        name = skill.name
        errors = check_baseline(skill)
        if errors:
            failed = True
            print(f"✗ {name} 基线检查未过:")
            for e in errors:
                print(f"    - {e}")
            continue

        if args.smoke:
            print(f"✓ {name} 基线通过")
            continue

        ok, out = run_validate_sh(skill)
        if ok:
            print(f"✓ {name} 通过")
        else:
            failed = True
            print(f"✗ {name} validate.sh 失败:")
            for line in out.splitlines():
                print(f"    {line}")

    print()
    print("检查未通过。" if failed else f"全部 {len(skills)} 个 skill 通过。")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
