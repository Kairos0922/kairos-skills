#!/usr/bin/env bash
# kairos-visual-generator 深度验证。由仓库根的 check.py 自动调用，也可单独运行。
set -euo pipefail

python3 scripts/verify_design_system.py
python3 scripts/verify_fonts.py
python3 scripts/verify_assets.py
python3 -m json.tool styles/registry.json >/dev/null
