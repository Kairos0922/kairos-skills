#!/usr/bin/env python3
"""
kairos-serenity 配置管理工具 (Class C: 状态完整性)
用法:
  python3 config.py validate            # 校验 JSON 结构
  python3 config.py list                # 列出所有持仓
  python3 config.py add <code> ...      # 安全添加持仓
  python3 config.py update <code> ...   # 更新持仓字段
  python3 config.py remove <code>       # 删除持仓
  python3 config.py backup              # 手动备份
"""

import json, sys, os, shutil, argparse
from datetime import datetime, timezone

CONFIG_PATH = os.path.expanduser("~/.kairos/kairos-serenity-config.json")

# Schema: holding 条目必填字段
REQUIRED_FIELDS = ["type", "code", "name", "market", "amount", "method", "status"]
VALID_MARKETS = ["A", "QDII", "US", "HK", "JP", "TW", "KR", "EU"]
VALID_TYPES = ["fund", "stock", "etf"]

# ---- 工具函数 ----
def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {"holdings": {}, "watchlist": {}, "preferences": {}}
    with open(CONFIG_PATH) as f:
        return json.load(f)

def backup_config():
    """写前备份"""
    if not os.path.exists(CONFIG_PATH):
        return
    bak = CONFIG_PATH + ".bak"
    shutil.copy2(CONFIG_PATH, bak)
    print(f"📦 已备份到 {bak}")

def save_config(data):
    """原子写入：临时文件 → 校验 → rename"""
    tmp = CONFIG_PATH + ".tmp"
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(tmp, "w") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    # 写后读回校验
    with open(tmp) as f:
        json.load(f)  # 抛异常则中断
    os.rename(tmp, CONFIG_PATH)

def validate_holding(code, data):
    """校验单个 holding 条目"""
    errors = []
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"缺少必填字段: {field}")
    if data.get("type") not in VALID_TYPES:
        errors.append(f"type 无效: {data.get('type')}，应为 {VALID_TYPES}")
    if data.get("market") not in VALID_MARKETS:
        errors.append(f"market 无效: {data.get('market')}，应为 {VALID_MARKETS}")
    if data.get("code") != code:
        errors.append(f"code 不匹配: {data.get('code')} != {code}")
    return errors

# ---- 命令 ----
def cmd_validate():
    """校验整个配置文件"""
    try:
        cfg = load_config()
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ 配置文件损坏或不存在: {e}")
        sys.exit(1)

    errors = []
    # 检查顶层键
    for key in ["holdings", "preferences"]:
        if key not in cfg:
            errors.append(f"缺少顶层键: {key}")
    if "holdings" not in cfg:
        print(f"❌ 配置校验失败 ({len(errors)}个错误):")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    # 检查每个 holding
    for code, h in cfg.get("holdings", {}).items():
        errs = validate_holding(code, h)
        for e in errs:
            errors.append(f"holdings.{code}: {e}")

    # 检查重复键（JSON 不允许，但如果被 Edit 工具损坏可能出现）
    with open(CONFIG_PATH) as f:
        raw = f.read()
    # 简单检测：计算 "holdings" 出现次数
    import re
    holdings_keys = re.findall(r'"holdings"\s*:', raw)
    if len(holdings_keys) > 1:
        errors.append("检测到多个 'holdings' 键——JSON 结构损坏")

    if errors:
        print(f"❌ 配置校验失败 ({len(errors)}个错误):")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)
    else:
        holdings_count = len(cfg.get("holdings", {}))
        print(f"✅ 配置校验通过 ({holdings_count}个持仓)")
        for code, h in cfg.get("holdings", {}).items():
            print(f"   {code}: {h.get('name','?')} [{h.get('status','?')}]")

def cmd_list():
    """列出所有持仓"""
    cfg = load_config()
    holdings = cfg.get("holdings", {})
    if not holdings:
        print("📭 无持仓")
        return
    print(f"📊 持仓列表 ({len(holdings)}个):")
    print(f"{'代码':<10} {'名称':<30} {'市场':<8} {'金额':<15} {'状态':<12}")
    print("-" * 75)
    for code, h in holdings.items():
        print(f"{code:<10} {h.get('name','?')[:28]:<30} {h.get('market','?'):<8} "
              f"{h.get('amount','?'):<15} {h.get('status','?'):<12}")

    wl = cfg.get("watchlist", {})
    if wl:
        print(f"\n👀 观望列表 ({len(wl)}个):")
        for code, h in wl.items():
            print(f"   {code}: {h.get('name','?')}")

def cmd_add(args):
    """安全添加持仓"""
    cfg = load_config()
    code = args.code
    if code in cfg.get("holdings", {}):
        print(f"⚠️ {code} 已存在，使用 update 命令修改")
        sys.exit(1)

    holding = {
        "type": args.type or "fund",
        "code": code,
        "name": args.name or code,
        "market": args.market or "QDII",
        "amount": args.amount or "未设置",
        "method": args.method or "定投",
        "status": args.status or "active",
    }

    errs = validate_holding(code, holding)
    if errs:
        print(f"❌ 校验失败:")
        for e in errs:
            print(f"   - {e}")
        sys.exit(1)

    # 从 watchlist 移除（如果存在）
    if code in cfg.get("watchlist", {}):
        del cfg["watchlist"][code]
        print(f"📤 从观望列表移除 {code}")

    backup_config()
    cfg.setdefault("holdings", {})[code] = holding
    save_config(cfg)
    print(f"✅ 已添加: {code} {holding['name']} [{holding['market']}] {holding['amount']}")

def cmd_update(args):
    """更新持仓字段"""
    cfg = load_config()
    code = args.code
    if code not in cfg.get("holdings", {}):
        print(f"❌ {code} 不存在，使用 add 命令添加")
        sys.exit(1)

    h = cfg["holdings"][code]
    updates = {}
    if args.name: updates["name"] = args.name
    if args.amount: updates["amount"] = args.amount
    if args.status: updates["status"] = args.status
    if args.method: updates["method"] = args.method
    if args.market: updates["market"] = args.market

    if not updates:
        print("⚠️ 无更新字段")
        sys.exit(0)

    backup_config()
    h.update(updates)
    # 校验更新后的结果
    errs = validate_holding(code, h)
    if errs:
        # 恢复备份
        shutil.copy2(CONFIG_PATH + ".bak", CONFIG_PATH)
        print(f"❌ 校验失败，已恢复备份:")
        for e in errs:
            print(f"   - {e}")
        sys.exit(1)

    save_config(cfg)
    print(f"✅ 已更新: {code} {h['name']}")
    for k, v in updates.items():
        print(f"   {k}: {v}")

def cmd_remove(args):
    """删除持仓"""
    cfg = load_config()
    code = args.code
    if code not in cfg.get("holdings", {}):
        print(f"❌ {code} 不存在")
        sys.exit(1)

    h = cfg["holdings"][code]
    backup_config()
    del cfg["holdings"][code]
    save_config(cfg)
    print(f"✅ 已删除: {code} {h.get('name','?')}")
    if args.to_watchlist:
        cfg = load_config()  # 重新加载（已 save）
        cfg.setdefault("watchlist", {})[code] = {
            "type": h.get("type", "fund"),
            "code": code,
            "name": h.get("name", code),
            "market": h.get("market", "?"),
            "note": "从持仓移入观望",
            "status": "watching",
        }
        save_config(cfg)
        print(f"   📥 已加入观望列表")

def cmd_backup():
    """手动备份"""
    backup_config()
    print("✅ 备份完成")

# ---- CLI ----
def main():
    parser = argparse.ArgumentParser(description="kairos-serenity 配置管理")
    sub = parser.add_subparsers(dest="cmd", help="命令")

    sub.add_parser("validate", help="校验配置文件结构")
    sub.add_parser("list", help="列出所有持仓")
    sub.add_parser("backup", help="手动备份配置文件")

    p_add = sub.add_parser("add", help="添加持仓")
    p_add.add_argument("code", help="基金/股票代码")
    p_add.add_argument("--type", choices=VALID_TYPES)
    p_add.add_argument("--name")
    p_add.add_argument("--market", choices=VALID_MARKETS)
    p_add.add_argument("--amount")
    p_add.add_argument("--method")
    p_add.add_argument("--status")

    p_up = sub.add_parser("update", help="更新持仓")
    p_up.add_argument("code", help="基金/股票代码")
    p_up.add_argument("--name")
    p_up.add_argument("--amount")
    p_up.add_argument("--status")
    p_up.add_argument("--method")
    p_up.add_argument("--market", choices=VALID_MARKETS)

    p_rm = sub.add_parser("remove", help="删除持仓")
    p_rm.add_argument("code", help="基金/股票代码")
    p_rm.add_argument("--to-watchlist", action="store_true", help="移入观望列表")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        sys.exit(0)

    try:
        {
            "validate": cmd_validate,
            "list": cmd_list,
            "add": lambda: cmd_add(args),
            "update": lambda: cmd_update(args),
            "remove": lambda: cmd_remove(args),
            "backup": cmd_backup,
        }[args.cmd]()
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"❌ 配置文件错误: {e}")
        print(f"   💡 从备份恢复: cp {CONFIG_PATH}.bak {CONFIG_PATH}")
        sys.exit(1)

if __name__ == "__main__":
    main()
