#!/usr/bin/env python3
"""
run_evals.py - 运行 kairos-collect-signals 的本地回归测试

用法:
    python3 scripts/run_evals.py
    python3 scripts/run_evals.py --output /tmp/kairos-eval-report.json
"""

import argparse
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from typing import Any, Dict, List

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

from scripts.analyze import analyze_signals_for_domain
from scripts.domain_config import DEFAULT_DOMAIN
from scripts.collector import SignalCollector
from scripts.source_adapters.registry import get_adapter


RSS_FIXTURE = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{title}</title>
    <link>{link}</link>
    <description>test feed</description>
    <item>
      <title>{item_title}</title>
      <link>{item_link}</link>
      <description>{description}</description>
      <pubDate>{pub_date}</pubDate>
      <author>{author}</author>
    </item>
  </channel>
</rss>
"""


def has_signal(result: Dict[str, Any], signal_id: str) -> bool:
    return any(signal.get("id") == signal_id for signal in result.get("signals", []))


def write_feed(path: str, title: str, item_title: str, description: str, author: str) -> None:
    pub_date = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")
    with open(path, "w", encoding="utf-8") as f:
        f.write(
            RSS_FIXTURE.format(
                title=title,
                link="https://example.com/feed",
                item_title=item_title,
                item_link="https://example.com/item",
                description=description,
                pub_date=pub_date,
                author=author,
            )
        )


def run_adapter_smoke_test() -> Dict[str, Any]:
    expected_types = ["rss", "github", "github-search", "reddit", "tavily", "x"]
    for source_type in expected_types:
        get_adapter(source_type)

    with tempfile.TemporaryDirectory(prefix="kairos-source-adapters-") as temp_dir:
        feed_paths = {
            "rss": os.path.join(temp_dir, "rss.xml"),
            "github": os.path.join(temp_dir, "github.xml"),
            "reddit": os.path.join(temp_dir, "reddit.xml"),
            "x": os.path.join(temp_dir, "x.xml"),
        }
        write_feed(feed_paths["rss"], "RSS Feed", "AI Agent benchmark improved", "AI Agent benchmark with latency data", "author-rss")
        write_feed(feed_paths["github"], "GitHub Feed", "AI Agent issue analysis", "AI Agent production debugging notes", "author-github")
        write_feed(feed_paths["reddit"], "Reddit Feed", "AI Agent retention tradeoff", "AI Agent tradeoff with refund rate", "author-reddit")
        write_feed(feed_paths["x"], "X Feed", "AI Agent workflow recap", "AI Agent production recap with metrics", "author-x")

        sources_path = os.path.join(temp_dir, "sources.json")
        with open(sources_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "sources": [
                        {"name": "RSS Source", "url": feed_paths["rss"], "type": "rss", "tier": 1, "enabled": True},
                        {"name": "GitHub Source", "url": feed_paths["github"], "type": "github", "tier": 1, "enabled": True},
                        {"name": "Reddit Source", "url": feed_paths["reddit"], "type": "reddit", "tier": 1, "enabled": True},
                        {"name": "X Source", "url": feed_paths["x"], "type": "x", "tier": 1, "enabled": True},
                    ]
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        collector = SignalCollector(domain="ai-engineering", sources_path=sources_path)
        signals = collector.collect_all(tier_filter=1)
        platforms = {signal.source["platform"] for signal in signals}
        expected_platforms = {"RSS Source", "GitHub Source", "Reddit Source", "X Source"}

        errors: List[str] = []
        if len(signals) != 4:
            errors.append(f"expected 4 adapter signals, got {len(signals)}")
        if platforms != expected_platforms:
            errors.append(f"unexpected platforms: {sorted(platforms)}")

        return {
            "passed": not errors,
            "errors": errors,
            "adapter_types": expected_types,
            "signals_collected": len(signals),
            "platforms": sorted(platforms),
        }


def validate_case(case: Dict[str, Any], result: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    case_id = case["id"]

    if case_id == 1:
        for key in ["signals", "tensions", "causal_chains", "patterns", "candidate_topics"]:
            if not result.get(key):
                errors.append(f"{key} should be non-empty")
        report = result.get("report_markdown", "")
        if not report:
            errors.append("report_markdown should be non-empty")
        for token in ["来源：", "时间：", "网址："]:
            if token not in report:
                errors.append(f"report_markdown should include {token}")
        if "http" not in report:
            errors.append("report_markdown should include source URL when available")
        for topic in result.get("candidate_topics", []):
            for field in [
                "topic", "problem_statement", "why_now", "core_insight", "angle",
                "target_reader", "evidence", "article_shape", "source_tension_id", "domain",
                "source_platform", "source_published_at", "source_url"
            ]:
                if not topic.get(field):
                    errors.append(f"candidate_topic missing {field}")
    elif case_id in {2, 3, 4, 7, 9}:
        target_signal_id = case["signals"][0]["id"] if case.get("signals") else ""
        if has_signal(result, target_signal_id):
            errors.append(f"filtered signals should not contain {target_signal_id}")
        if result.get("tensions"):
            errors.append("tensions should be empty")
        if result.get("candidate_topics"):
            errors.append("candidate_topics should be empty")
    elif case_id == 5:
        signals = result.get("signals", [])
        if not signals:
            errors.append("signals should be non-empty")
        for signal in signals:
            score = signal.get("quality_score")
            if score is None or score < 0 or score > 1:
                errors.append("quality_score should be between 0 and 1")
    elif case_id == 6:
        for key in ["signals", "tensions", "candidate_topics"]:
            if result.get(key):
                errors.append(f"{key} should be empty")
        report = result.get("report_markdown", "")
        if "本轮没有形成可写选题" not in report:
            errors.append("empty case should still render a natural-language report")
    elif case_id == 8:
        if not has_signal(result, "sig-008"):
            errors.append("sig-008 should survive filtering")
        signals = result.get("signals", [])
        if signals and signals[0].get("gate_scores", {}).get("firsthand_experience", 0) < 0.5:
            errors.append("firsthand_experience should be >= 0.5")
        if not result.get("tensions"):
            errors.append("tensions should be non-empty")
    elif case_id == 10:
        if not has_signal(result, "sig-010"):
            errors.append("sig-010 should survive filtering")
        for key in ["tensions", "causal_chains", "candidate_topics"]:
            if not result.get(key):
                errors.append(f"{key} should be non-empty")
    elif case_id == 11:
        if not has_signal(result, "sig-011"):
            errors.append("sig-011 should survive filtering")
        for key in ["tensions", "causal_chains", "candidate_topics"]:
            if not result.get(key):
                errors.append(f"{key} should be non-empty")
        topics = result.get("candidate_topics", [])
        if topics and not any(
            token in topics[0].get("topic", "").lower()
            for token in ["反馈闭环", "reward hacking", "评估漂移"]
        ):
            errors.append("candidate topic should mention feedback loop failure or reward hacking")
    elif case_id == 12:
        if not has_signal(result, "sig-012"):
            errors.append("sig-012 should survive filtering")
        for key in ["tensions", "candidate_topics"]:
            if not result.get(key):
                errors.append(f"{key} should be non-empty")
        topics = result.get("candidate_topics", [])
        if topics and not any(
            token in topics[0].get("topic", "")
            for token in ["直播间", "退款率翻倍"]
        ):
            errors.append("candidate topic should stay concrete for operations tradeoff")
    elif case_id == 13:
        if not has_signal(result, "sig-013"):
            errors.append("sig-013 should survive filtering")
        for key in ["tensions", "candidate_topics"]:
            if not result.get(key):
                errors.append(f"{key} should be non-empty")
        topics = result.get("candidate_topics", [])
        if topics and not any(
            token in topics[0].get("topic", "")
            for token in ["知识星球", "续费率", "留存"]
        ):
            errors.append("candidate topic should stay concrete for content product tradeoff")
    elif case_id == 14:
        if not has_signal(result, "sig-014"):
            errors.append("sig-014 should survive filtering via domain high_quality_authors")
        for key in ["tensions", "candidate_topics"]:
            if not result.get(key):
                errors.append(f"{key} should be non-empty")
    elif case_id == 15:
        if not has_signal(result, "sig-015"):
            errors.append("sig-015 should survive filtering with domain default strategy")
        if result.get("meta", {}).get("strategy") != "problem-solving":
            errors.append("domain default strategy should resolve to problem-solving")
        for key in ["tensions", "candidate_topics"]:
            if not result.get(key):
                errors.append(f"{key} should be non-empty")
        report = result.get("report_markdown", "")
        if "来源：" not in report or "时间：" not in report:
            errors.append("report should include source and time in natural language")
    else:
        errors.append(f"unsupported eval case id: {case_id}")

    return errors


def run_cases(evals_path: str) -> Dict[str, Any]:
    with open(evals_path, "r", encoding="utf-8") as f:
        evals_data = json.load(f)

    report_cases: List[Dict[str, Any]] = []
    passed_count = 0
    for case in evals_data.get("evals", []):
        domain = case.get("domain", DEFAULT_DOMAIN)
        strategy = case.get("strategy", "")
        result = analyze_signals_for_domain(case.get("signals", []), strategy, domain)
        errors = validate_case(case, result)
        passed = not errors
        if passed:
            passed_count += 1
        report_cases.append({
            "id": case["id"],
            "name": case["name"],
            "passed": passed,
            "errors": errors,
            "summary": {
                "signals": len(result.get("signals", [])),
                "tensions": len(result.get("tensions", [])),
                "causal_chains": len(result.get("causal_chains", [])),
                "patterns": len(result.get("patterns", [])),
                "candidate_topics": len(result.get("candidate_topics", [])),
            },
        })

    adapter_smoke = run_adapter_smoke_test()

    total = len(report_cases) + 1
    failed = (len(report_cases) - passed_count) + (0 if adapter_smoke["passed"] else 1)
    passed = total - failed

    return {
        "skill_name": evals_data.get("skill_name"),
        "passed": passed,
        "failed": failed,
        "total": total,
        "cases": report_cases,
        "adapter_smoke_test": adapter_smoke,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="运行本地 evals")
    parser.add_argument(
        "--evals",
        default=os.path.join(SKILL_DIR, "evals", "evals.json"),
        help="evals.json 路径",
    )
    parser.add_argument("--output", default="", help="可选：将报告写入 JSON 文件")
    args = parser.parse_args()

    report = run_cases(args.evals)

    if args.output:
        output_dir = os.path.dirname(args.output)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"评估报告已写入: {args.output}")
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
