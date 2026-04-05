#!/usr/bin/env python3
"""
collect.py - 采集信号并输出 JSON

用法:
    python3 scripts/collect.py --tier 1 --limit 100 --keywords "LangChain RAG"

参数:
    --tier      数据源 Tier 等级 (1 或 2)，默认 1
    --limit     返回信号数量上限，默认 100
    --keywords  关键词过滤（可选），多个关键词用空格分隔
    --filter    运行 filter.py 过滤信号（可选）
"""

import argparse
import json
import os
import subprocess
import sys

# 将 skill 目录加入 path
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

from scripts.collector import SignalCollector


def main():
    parser = argparse.ArgumentParser(description="采集信号")
    parser.add_argument("--tier", type=int, default=1, help="数据源 Tier 等级 (1 或 2)")
    parser.add_argument("--limit", type=int, default=100, help="返回信号数量上限")
    parser.add_argument("--keywords", type=str, default="", help="关键词过滤（可选）")
    parser.add_argument("--filter", action="store_true", help="运行 filter.py 过滤信号")
    args = parser.parse_args()

    collector = SignalCollector()
    signals = collector.collect_all(tier_filter=args.tier)

    # 关键词过滤
    if args.keywords:
        keywords_lower = [k.strip().lower() for k in args.keywords.split() if k.strip()]
        if keywords_lower:
            filtered = []
            for s in signals:
                content_lower = s.content.lower()
                if any(kw in content_lower for kw in keywords_lower):
                    filtered.append(s)
            if filtered:
                signals = filtered

    # 数量限制
    signals = signals[:args.limit]

    # 构建结果
    result = {"signals": [s.to_dict() for s in signals]}

    # 如果需要过滤，保存临时文件并运行 filter.py
    if args.filter:
        temp_input = os.path.join(SKILL_DIR, ".kairos-temp", "signals-collect.json")
        temp_output = os.path.join(SKILL_DIR, ".kairos-temp", "signals-filtered.json")

        # 确保临时目录存在
        os.makedirs(os.path.dirname(temp_input), exist_ok=True)

        # 保存采集的信号
        with open(temp_input, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"信号已保存至: {temp_input}", file=sys.stderr)

        # 运行 filter.py
        filter_script = os.path.join(SKILL_DIR, "scripts", "filter.py")
        try:
            subprocess.run(
                [sys.executable, filter_script, "--input", temp_input, "--output", temp_output],
                check=True
            )

            # 读取过滤后的结果
            with open(temp_output, "r", encoding="utf-8") as f:
                filtered_result = json.load(f)

            # 输出过滤后的结果
            print(json.dumps(filtered_result, ensure_ascii=False, indent=2))

            # 清理临时文件
            os.remove(temp_input)
            os.remove(temp_output)

        except subprocess.CalledProcessError as e:
            print(f"过滤失败: {e}", file=sys.stderr)
            sys.exit(1)
        except FileNotFoundError as e:
            print(f"过滤脚本不存在: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # 直接输出原始结果
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
