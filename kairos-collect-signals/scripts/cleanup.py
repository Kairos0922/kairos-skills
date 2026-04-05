#!/usr/bin/env python3
"""
cleanup.py - 临时文件清理脚本

删除 ./.kairos-temp/ 目录及其所有内容。

用法:
    python3 scripts/cleanup.py
"""

import shutil
import os
import sys


def main():
    # 获取 skill 根目录
    SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    TEMP_DIR = os.path.join(SKILL_DIR, ".kairos-temp")

    if not os.path.exists(TEMP_DIR):
        print(f"临时目录不存在，无需清理: {TEMP_DIR}")
        sys.exit(0)

    try:
        shutil.rmtree(TEMP_DIR)
        print(f"已清理临时目录: {TEMP_DIR}")
    except Exception as e:
        print(f"清理失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
