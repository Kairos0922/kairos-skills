#!/usr/bin/env python3
"""
dedup.py - 信号去重脚本

基于内容哈希对信号去重，保留最新发布的信号。

用法:
    python3 scripts/dedup.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/signals-deduped.json
"""

import argparse
import hashlib
import json
import sys
import os
from datetime import datetime
from typing import Any, Dict, List


def compute_content_hash(signal: Dict[str, Any]) -> str:
    """计算信号内容哈希（基于标题+来源）"""
    content = signal.get("content", "")
    source = signal.get("source", {})
    source_name = source.get("platform", "") + source.get("url", "")
    text = content + source_name
    return hashlib.md5(text.encode("utf-8")).hexdigest()


def parse_datetime(dt_str: str) -> datetime:
    """解析日期时间字符串"""
    if not dt_str:
        return datetime.min
    formats = [
        "%Y-%m-%dT%H:%M:%S%z",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d",
    ]
    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue
    return datetime.min


def dedup_signals(signals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """去重：基于内容哈希，保留最新发布的信号"""
    seen: Dict[str, Dict[str, Any]] = {}

    for signal in signals:
        content_hash = compute_content_hash(signal)
        published_at = signal.get("published_at", "")

        if content_hash not in seen:
            seen[content_hash] = signal
        else:
            # 比较发布时间，保留最新的
            existing_time = parse_datetime(seen[content_hash].get("published_at", ""))
            new_time = parse_datetime(published_at)
            if new_time > existing_time:
                seen[content_hash] = signal

    return list(seen.values())


def main():
    parser = argparse.ArgumentParser(description="信号去重")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    # 读取输入文件
    if not os.path.exists(args.input):
        print(f"错误：输入文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    signals = data.get("signals", [])
    if not signals:
        print("警告：输入信号为空", file=sys.stderr)

    # 去重
    deduped = dedup_signals(signals)
    original_count = len(signals)
    deduped_count = len(deduped)

    print(f"去重完成：{original_count} -> {deduped_count} (去除 {original_count - deduped_count} 条)")

    # 写入输出文件
    output_data = {
        "signals": deduped,
        "meta": {
            "original_count": original_count,
            "deduped_count": deduped_count,
            "dedup_time": datetime.now().isoformat()
        }
    }

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"去重结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
