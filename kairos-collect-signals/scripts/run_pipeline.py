#!/usr/bin/env python3
"""
run_pipeline.py - One-shot pipeline runner for OpenClaw cron

This script runs the full pipeline in a single Python invocation:
collect -> dedup -> filter -> analyze -> (optional) cleanup

It avoids shell chaining so OpenClaw exec allowlist can run it safely.
"""

import argparse
import json
import os
import sys
from typing import List

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

from scripts.collector import SignalCollector
from scripts.dedup import dedup_signals
from scripts.filter import filter_signals
from scripts.analyze import analyze_signals_for_domain
from scripts.domain_config import DEFAULT_DOMAIN, resolve_strategy


def ensure_dir(path: str) -> None:
    if path:
        os.makedirs(path, exist_ok=True)


def keyword_filter(signals: List[dict], keywords: List[str]) -> List[dict]:
    if not keywords:
        return signals
    keywords_lower = [k.strip().lower() for k in keywords if k.strip()]
    if not keywords_lower:
        return signals
    filtered = []
    for signal in signals:
        content = signal.get("content", "").lower()
        if any(kw in content for kw in keywords_lower):
            filtered.append(signal)
    return filtered


def main() -> None:
    parser = argparse.ArgumentParser(description="Run full kairos-collect-signals pipeline in one command")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help="领域配置名")
    parser.add_argument("--tier", type=int, default=1, help="数据源 Tier 等级 (1 或 2)")
    parser.add_argument("--limit", type=int, default=100, help="信号数量上限")
    parser.add_argument("--keywords", type=str, default="", help="关键词过滤（可选）")
    parser.add_argument("--strategy", type=str, default="", help="可选：策略目录名，留空则使用领域默认策略")
    parser.add_argument("--output", type=str, default="", help="选题报告输出路径")
    parser.add_argument("--keep-temp", action="store_true", help="保留 .kairos-temp 中间结果")
    parser.add_argument("--quiet", action="store_true", help="不输出报告到 stdout")
    args = parser.parse_args()

    temp_dir = os.path.join(SKILL_DIR, ".kairos-temp")
    ensure_dir(temp_dir)

    signals_path = os.path.join(temp_dir, "signals.json")
    deduped_path = os.path.join(temp_dir, "signals-deduped.json")
    filtered_path = os.path.join(temp_dir, "signals-filtered.json")
    report_path = args.output or os.path.join(temp_dir, "topic-report.md")

    collector = SignalCollector(domain=args.domain)
    signals = collector.collect_all(tier_filter=args.tier)
    signals_dicts = [signal.to_dict() for signal in signals]

    if args.keywords:
        signals_dicts = keyword_filter(signals_dicts, args.keywords.split())

    if args.limit and args.limit > 0:
        signals_dicts = signals_dicts[: args.limit]

    with open(signals_path, "w", encoding="utf-8") as f:
        json.dump({"signals": signals_dicts}, f, ensure_ascii=False, indent=2)

    deduped = dedup_signals(signals_dicts)
    with open(deduped_path, "w", encoding="utf-8") as f:
        json.dump({"signals": deduped}, f, ensure_ascii=False, indent=2)

    resolved_strategy = resolve_strategy(args.domain, args.strategy)
    filtered, rejection_stats = filter_signals(deduped, domain=args.domain, strategy=resolved_strategy)
    with open(filtered_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "signals": filtered,
                "meta": {
                    "rejection_stats": rejection_stats,
                    "domain": args.domain,
                    "strategy": resolved_strategy,
                },
            },
            f,
            ensure_ascii=False,
            indent=2,
        )

    result = analyze_signals_for_domain(filtered, resolved_strategy, args.domain)
    output_dir = os.path.dirname(report_path)
    ensure_dir(output_dir)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(result.get("report_markdown", ""))

    if not args.quiet:
        print(result.get("report_markdown", ""))

    if not args.keep_temp:
        try:
            import shutil

            shutil.rmtree(temp_dir)
        except Exception:
            pass


if __name__ == "__main__":
    main()

