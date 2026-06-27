#!/usr/bin/env bash
# kairos-wechat-typeset 深度验证。由仓库根的 check.py 自动调用，也可单独运行。
set -euo pipefail

python3 scripts/check_all.py
python3 scripts/verify_fonts.py
python3 scripts/verify_assets.py
python3 -m json.tool themes/registry.json >/dev/null
python3 scripts/render.py --list-themes >/dev/null
