#!/usr/bin/env python3
"""
filter.py - 信号过滤脚本

应用以下规则过滤信号：
1. Banned Patterns（正则匹配）
2. Source Whitelist/Blacklist
3. Quality Gates

用法:
    python3 scripts/filter.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/signals-filtered.json

Quality Gates (LLM 判断):
    每个 >= 0.5 且总分 >= 3.0 才通过:
    - firsthand_experience: 作者是否有亲身测试/实验/数据
    - unique_perspective: 是否有差异化视角
    - depth_analysis: 是否有技术深度
    - practical_value: 是否可落地
"""

import argparse
import json
import os
import re
import sys
from typing import Any, Dict, List, Optional, Tuple

from scripts.domain_config import DEFAULT_DOMAIN, DEFAULT_STRATEGY
from scripts.domain_config import load_banned_patterns as load_strategy_banned_patterns
from scripts.domain_config import load_high_quality_authors as load_domain_high_quality_authors
from scripts.domain_config import resolve_strategy
from scripts.domain_config import load_sources as load_domain_sources

# 将 skill 目录加入 path
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)


# =============================================================================
# BANNED PATTERNS - 正则匹配，匹配则直接拒绝
# =============================================================================
FALLBACK_BANNED_PATTERNS = [
    {
        "name": "hot_news",
        "pattern": r"^.*(刚刚|重磅|突发|震惊|炸裂).*(发布|上线|推出|宣布).*$",
        "description": "热点炒作类标题"
    },
    {
        "name": "predictions",
        "pattern": r"^.*(十大|预测|展望|趋势).*\d{4}年|来年.*趋势|必火.*$",
        "description": "预测类标题"
    },
    {
        "name": "generic_overview",
        "pattern": r"^.*(一文读懂|全面解读|快速入门|分钟学会|一张图读懂).*$",
        "description": "二道贩子概述"
    },
    {
        "name": "anxiety_marketing",
        "pattern": r"^.*(AI取代.*职业|将被淘汰|即将消失|逆天|颠覆认知|太卷了).*$",
        "description": "焦虑营销"
    },
    {
        "name": "translation_fluff",
        "pattern": r"^.*(让我们深入|值得注意的是|本文将探讨|翻译自).*$",
        "description": "机器翻译泛滥"
    },
    {
        "name": "tool_list",
        "pattern": r"^.*(工具推荐|必备神器|10款.*工具|超级好用.*工具).*$",
        "description": "工具推荐堆砌"
    },
    {
        "name": "tutorial_fluff",
        "pattern": r"^.*(从零开始|新手必看|入门教程|上手指南|小白.*必学).*$",
        "description": "入门教程泛滥"
    },
    {
        "name": "ai_generated",
        "pattern": r"^.*(首先|其次|最后|总之).{0,15}(我们可以看到|研究表明).*$",
        "description": "AI生成特征"
    },
    {
        "name": "clickbait",
        "pattern": r"^.*(竟然|居然|万万没想到|99%的人都不知道|绝了).*$",
        "description": "标题党特征"
    }
]


# =============================================================================
# SOURCE WHITELIST & BLACKLIST
# =============================================================================

# 黑名单来源（直接拒绝）
BLACKLIST_SOURCES = {
    # 聚合类内容
    "程序员日报", "开发者头条", "知乎日报",
    "今日头条", "腾讯新闻", "网易新闻",
    # 资讯类翻译
    "机器翻译", "翻译自", "转载",
}

# 高质量作者列表（从 domains/<domain>/high_quality_authors.json 加载）
HIGH_QUALITY_AUTHORS: Dict[str, List[str]] = {}

# 运行时加载配置
BANNED_PATTERNS: List[Dict[str, str]] = []
WHITELIST_SOURCES: set = set()


def normalize_source_name(name: str) -> str:
    return name.strip().lower()


def load_banned_patterns(strategy: str) -> None:
    """加载策略级 banned patterns 配置"""
    global BANNED_PATTERNS
    data = load_strategy_banned_patterns(strategy)
    BANNED_PATTERNS = data.get("banned_patterns", [])

    if not BANNED_PATTERNS:
        BANNED_PATTERNS = FALLBACK_BANNED_PATTERNS


def load_whitelist_sources(domain: str) -> None:
    """加载领域白名单来源（domains/<domain>/sources.json）"""
    global WHITELIST_SOURCES
    loaded = set()
    try:
        data = load_domain_sources(domain)
        for src in data.get("sources", []):
            if not src.get("enabled", True):
                continue
            name = src.get("name", "")
            if name:
                loaded.add(normalize_source_name(name))
    except Exception:
        pass

    WHITELIST_SOURCES = loaded


def load_high_quality_authors(domain: str) -> None:
    """加载领域级高质量作者列表"""
    global HIGH_QUALITY_AUTHORS
    HIGH_QUALITY_AUTHORS = {}
    try:
        data = load_domain_high_quality_authors(domain)
        for platform_name, platform_data in data.items():
            if not isinstance(platform_data, list):
                continue
            for author in platform_data:
                if not isinstance(author, dict):
                    continue
                username = author.get("username", "")
                if username:
                    HIGH_QUALITY_AUTHORS.setdefault(platform_name.lower(), []).append(username.lower())
    except Exception:
        pass


# =============================================================================
# QUALITY GATES
# =============================================================================

QUALITY_GATES = [
    "firsthand_experience",  # 是否有作者亲身测试/实验/数据
    "unique_perspective",     # 是否有差异化视角
    "depth_analysis",         # 是否有技术深度
    "practical_value",        # 是否可落地
]

# 每个门控的最小分数
GATE_MIN_SCORE = 0.5
# 总分最低要求
GATE_TOTAL_MIN = 2.8

FIRSTHAND_MARKERS = [
    "实测", "测试了", "benchmark", "实验", "数据", "结果", "排查", "复盘",
    "我们", "我", "踩坑", "生产环境", "case study", "postmortem",
]
UNIQUE_MARKERS = [
    "我认为", "our approach", "we found", "关键原因", "根因", "教训",
    "tradeoff", "权衡", "失败", "异常", "踩坑", "反直觉",
]
DEPTH_MARKERS = [
    "algorithm", "architecture", "performance", "latency", "accuracy",
    "memory", "p99", "吞吐量", "延迟", "准确率", "内存", "根因", "机制",
    "转化率", "留存", "退款率", "复购率", "客单价", "毛利", "客诉", "完播率",
]
PRACTICAL_MARKERS = [
    "code", "implementation", "开源", "github", "排查", "复盘",
    "部署", "生产环境", "优化", "回滚", "监控", "benchmark",
    "上线", "运营", "活动", "社群", "课程", "直播间", "用户", "转化",
]
CASE_STUDY_MARKERS = ["踩坑", "复盘", "排查", "教训", "故障", "事故", "生产环境"]


def check_banned_patterns(title: str, content: str = "") -> Tuple[bool, Optional[str]]:
    """
    检查是否匹配 banned patterns。

    Returns:
        (is_banned, pattern_name)
    """
    text = title + " " + content[:500]
    for bp in BANNED_PATTERNS:
        try:
            if re.match(bp["pattern"], text):
                return True, bp["name"]
        except re.error:
            continue
    return False, None


def check_source_whitelist(signal: Dict[str, Any]) -> Tuple[bool, str]:
    """
    检查来源是否在白名单中。

    Returns:
        (is_allowed, reason)
    """
    source = signal.get("source", {})
    platform = source.get("platform", "")
    collector = source.get("collector", "")
    platform_norm = normalize_source_name(platform)
    collector_norm = normalize_source_name(collector) if collector else ""

    # 检查黑名单
    if platform_norm in {normalize_source_name(s) for s in BLACKLIST_SOURCES}:
        return False, f"黑名单来源: {platform}"

    # 检查白名单
    if platform_norm in WHITELIST_SOURCES:
        return True, "白名单来源"
    if collector_norm and collector_norm in WHITELIST_SOURCES:
        return True, f"白名单采集器: {collector}"

    # 检查高质量作者（twitter/reddit 等）
    author = source.get("author", "").lower()
    for platform_name, authors in HIGH_QUALITY_AUTHORS.items():
        if author in authors:
            return True, f"高质量{platform_name}作者: {author}"

    return False, f"未授权来源: {platform}"


def score_quality_gates(signal: Dict[str, Any]) -> Tuple[bool, Dict[str, float], float]:
    """
    对信号进行质量门控评分。

    注意：这是基于规则的简单评分。完整的 LLM 判断需要在 angle generation 阶段完成。
    这里用启发式规则给出一个初步评分。

    Returns:
        (passes_gates, gate_scores, total_score)
    """
    content = signal.get("content", "")
    title = signal.get("content", "").split("\n")[0] if signal.get("content") else ""
    source = signal.get("source", {})
    platform = source.get("platform", "")
    collector = source.get("collector", "")
    platform_norm = normalize_source_name(platform)
    collector_norm = normalize_source_name(collector) if collector else ""
    author = source.get("author", "")

    # 初始化分数
    scores = {gate: 0.5 for gate in QUALITY_GATES}

    content_lower = content.lower()
    has_number = bool(re.search(r"\d", content))

    # 1. firsthand_experience - 官方博客/个人博客/ArXiv 较高
    if platform_norm in WHITELIST_SOURCES or (collector_norm and collector_norm in WHITELIST_SOURCES):
        scores["firsthand_experience"] = 0.8
        scores["depth_analysis"] = 0.8
    if any(marker.lower() in content_lower for marker in FIRSTHAND_MARKERS) or "I " in content[:100]:
        scores["firsthand_experience"] = max(scores["firsthand_experience"], 0.8)
    if author and author not in ["", "unknown"]:
        scores["firsthand_experience"] = max(scores["firsthand_experience"], 0.7)
    if any(kw in content_lower for kw in ["data", "result", "experiment", "benchmark", "test"]):
        scores["firsthand_experience"] = max(scores["firsthand_experience"], 0.7)
    if has_number and any(marker.lower() in content_lower for marker in FIRSTHAND_MARKERS):
        scores["firsthand_experience"] = max(scores["firsthand_experience"], 0.9)

    # 2. unique_perspective - 原创内容较高
    if any(marker.lower() in content_lower for marker in UNIQUE_MARKERS):
        scores["unique_perspective"] = 0.75
    if platform_norm in {normalize_source_name("Hacker News"), normalize_source_name("GitHub Trending")}:
        scores["unique_perspective"] = 0.6
    if has_number and any(marker in content for marker in CASE_STUDY_MARKERS):
        scores["unique_perspective"] = max(scores["unique_perspective"], 0.8)
    if has_number and any(token in content_lower for token in ["benchmark", "性能", "吞吐量", "延迟", "准确率", "只有"]):
        scores["unique_perspective"] = max(scores["unique_perspective"], 0.7)
    if "综述" in content or "整理" in content or "翻译" in content:
        scores["unique_perspective"] = 0.3

    # 3. depth_analysis - 技术博客/ArXiv 较高
    if "arxiv" in platform.lower() or "research" in platform.lower():
        scores["depth_analysis"] = 0.9
    if any(marker.lower() in content_lower for marker in DEPTH_MARKERS):
        scores["depth_analysis"] = max(scores["depth_analysis"], 0.75)
    if len(content) > 500 or (has_number and any(marker.lower() in content_lower for marker in DEPTH_MARKERS)):
        scores["depth_analysis"] = max(scores["depth_analysis"], 0.6)

    # 4. practical_value - 不只奖励教程，也奖励复盘、排障、部署、优化
    if any(kw in content for kw in ["how to", "tutorial", "guide", "教程", "指南"]):
        if not any(kw in title for kw in ["入门", "新手", "从零开始"]):
            scores["practical_value"] = 0.8
    if any(marker.lower() in content_lower for marker in PRACTICAL_MARKERS):
        scores["practical_value"] = max(scores["practical_value"], 0.7)
    if has_number and any(marker in content for marker in CASE_STUDY_MARKERS):
        scores["practical_value"] = max(scores["practical_value"], 0.85)
    if has_number and any(token in content_lower for token in ["benchmark", "性能", "吞吐量", "延迟", "准确率", "测试了"]):
        scores["practical_value"] = max(scores["practical_value"], 0.7)

    # 降低 fluff 类内容的分数
    fluff_keywords = ["一文读懂", "全面解读", "快速入门", "必备神器"]
    if any(kw in title for kw in fluff_keywords):
        for gate in scores:
            scores[gate] *= 0.5

    # 生产问题/复盘类信号通常直接对应高质量问题导向选题，适当整体加权
    if any(marker in content for marker in CASE_STUDY_MARKERS):
        scores["unique_perspective"] = max(scores["unique_perspective"], 0.7)
        scores["practical_value"] = max(scores["practical_value"], 0.8)

    total = sum(scores.values())

    # 检查是否通过门控
    passes = all(scores[gate] >= GATE_MIN_SCORE for gate in QUALITY_GATES) and total >= GATE_TOTAL_MIN

    return passes, scores, total


def filter_signals(
    signals: List[Dict[str, Any]],
    domain: str = DEFAULT_DOMAIN,
    strategy: str = DEFAULT_STRATEGY,
) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    对信号列表应用所有过滤规则。

    Returns:
        (filtered_signals, rejection_stats)
    """
    resolved_strategy = resolve_strategy(domain, strategy)
    load_banned_patterns(resolved_strategy)
    load_whitelist_sources(domain)
    load_high_quality_authors(domain)

    filtered = []
    stats = {
        "banned_pattern": 0,
        "source_not_whitelisted": 0,
        "quality_gate_failed": 0,
    }

    for signal in signals:
        content = signal.get("content", "")
        title = content.split("\n")[0] if content else ""

        # 规则 1: Banned Patterns
        is_banned, pattern_name = check_banned_patterns(title, content)
        if is_banned:
            stats["banned_pattern"] += 1
            continue

        # 规则 2: Source Whitelist
        is_allowed, reason = check_source_whitelist(signal)
        if not is_allowed:
            stats["source_not_whitelisted"] += 1
            continue

        # 规则 3: Quality Gates
        passes_gates, gate_scores, total_score = score_quality_gates(signal)
        if not passes_gates:
            stats["quality_gate_failed"] += 1
            continue

        # 添加门控分数到信号
        filtered_signal = signal.copy()
        filtered_signal["gate_scores"] = gate_scores
        filtered_signal["quality_score"] = total_score / len(QUALITY_GATES)

        filtered.append(filtered_signal)

    return filtered, stats


def main():
    parser = argparse.ArgumentParser(description="信号过滤")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help="领域配置名")
    parser.add_argument("--strategy", default="", help="可选：策略目录名，留空则使用领域默认策略")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

    # 加载配置
    resolved_strategy = resolve_strategy(args.domain, args.strategy)
    load_banned_patterns(resolved_strategy)
    load_whitelist_sources(args.domain)
    load_high_quality_authors(args.domain)

    # 确保输入文件存在
    if not os.path.exists(args.input):
        print(f"错误：输入文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    # 读取输入
    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    signals = data.get("signals", [])
    original_count = len(signals)

    print(f"开始过滤：共 {original_count} 条信号")

    # 过滤
    filtered_signals, stats = filter_signals(signals, domain=args.domain, strategy=args.strategy)
    filtered_count = len(filtered_signals)

    # 输出统计
    print(f"\n过滤结果：")
    print(f"  原始信号: {original_count}")
    print(f"  过滤后: {filtered_count}")
    print(f"  去除详情:")
    print(f"    - Banned Pattern: {stats['banned_pattern']}")
    print(f"    - 来源未授权: {stats['source_not_whitelisted']}")
    print(f"    - 质量门控未通过: {stats['quality_gate_failed']}")
    print(f"  使用策略: {resolved_strategy}")

    # 保存结果
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    output_data = {
        "signals": filtered_signals,
        "meta": {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "rejection_stats": stats,
            "filter_time": __import__("datetime").datetime.now().isoformat(),
            "domain": args.domain,
            "strategy": resolved_strategy,
        }
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n过滤结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
