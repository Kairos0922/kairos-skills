#!/usr/bin/env python3
"""
discover_sources.py - 使用 Tavily 搜索发现官方博客 / feed 候选地址

用法:
    python3 scripts/discover_sources.py --domain ai-engineering --output /tmp/discovered-sources.json
"""

import argparse
import json
import os
import sys
from datetime import datetime
from urllib import request

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

from scripts.domain_config import DEFAULT_DOMAIN, load_search_queries
from scripts.runtime_env import get_required_env

TAVILY_URL = "https://api.tavily.com/search"


def tavily_search(query: str, max_results: int = 5) -> dict:
    payload = {
        "query": query,
        "api_key": get_required_env("TAVILY_API_KEY"),
        "max_results": max_results,
        "search_depth": "basic",
    }
    req = request.Request(
        TAVILY_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read())


def main() -> None:
    parser = argparse.ArgumentParser(description="发现官方博客 / feed 候选地址")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help="领域配置名")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    query_sets = load_search_queries(args.domain).get("query_sets", {})
    targets = query_sets.get("official-blog-targets", [])

    results = []
    for target in targets:
        query = f"{target} official engineering blog rss OR atom"
        data = tavily_search(query, max_results=5)
        results.append(
            {
                "target": target,
                "query": query,
                "results": data.get("results", []),
            }
        )

    output_data = {
        "domain": args.domain,
        "generated_at": datetime.now().isoformat(),
        "candidates": results,
    }
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"候选来源已写入: {args.output}")
