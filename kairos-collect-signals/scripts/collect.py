#!/usr/bin/env python3
"""
collect.py - 采集信号并输出 JSON

用法:
    python3 scripts/collect.py --tier 1 --limit 100 --keywords "LangChain RAG"

参数:
    --tier      数据源 Tier 等级 (1 或 2)，默认 1
    --limit     返回信号数量上限，默认 100
    --keywords  关键词过滤（可选），多个关键词用空格分隔
    --strategy  可选：过滤时使用的策略目录名，留空则使用领域默认策略
    --filter    运行 filter.py 过滤信号（可选）
    --input     从已有 JSON 文件读取信号（跳过采集），用于 evals
    --output    输出到指定文件路径（代替 stdout）
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
from scripts.domain_config import DEFAULT_DOMAIN, resolve_strategy


def main():
    parser = argparse.ArgumentParser(description="采集信号")
    parser.add_argument("--tier", type=int, default=1, help="数据源 Tier 等级 (1 或 2)")
    parser.add_argument("--limit", type=int, default=100, help="返回信号数量上限")
    parser.add_argument("--keywords", type=str, default="", help="关键词过滤（可选）")
    parser.add_argument("--domain", type=str, default=DEFAULT_DOMAIN, help="领域配置名")
    parser.add_argument("--strategy", type=str, default="", help="可选：过滤时使用的策略目录名，留空则使用领域默认策略")
    parser.add_argument("--filter", action="store_true", help="运行 filter.py 过滤信号")
    parser.add_argument("--input", type=str, default="", help="从已有 JSON 文件读取信号（跳过采集）")
    parser.add_argument("--output", type=str, default="", help="输出到指定文件路径（代替 stdout）")
    args = parser.parse_args()

    # 如果指定了 --input，从文件读取信号（跳过采集），直接进入输出
    if args.input:
        if not os.path.exists(args.input):
            print(f"错误：--input 文件不存在: {args.input}", file=sys.stderr)
            sys.exit(1)
        with open(args.input, "r", encoding="utf-8") as f:
            data = json.load(f)
        signals = data.get("signals", [])
        result = {"signals": signals}
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"信号已从文件读取并写入: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    collector = SignalCollector(domain=args.domain)
    signals = collector.collect_all(tier_filter=args.tier)
    resolved_strategy = resolve_strategy(args.domain, args.strategy)

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
                [
                    sys.executable,
                    filter_script,
                    "--domain",
                    args.domain,
                    "--strategy",
                    resolved_strategy,
                    "--input",
                    temp_input,
                    "--output",
                    temp_output,
                ],
                check=True
            )

            # 读取过滤后的结果
            with open(temp_output, "r", encoding="utf-8") as f:
                filtered_result = json.load(f)

            # 输出过滤后的结果
            if args.output:
                output_dir = os.path.dirname(args.output)
                if output_dir:
                    os.makedirs(output_dir, exist_ok=True)
                with open(args.output, "w", encoding="utf-8") as f:
                    json.dump(filtered_result, f, ensure_ascii=False, indent=2)
                print(f"过滤后信号已写入: {args.output}")
            else:
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
        if args.output:
            output_dir = os.path.dirname(args.output)
            if output_dir:
                os.makedirs(output_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"信号已写入: {args.output}")
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
