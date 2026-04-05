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

# 将 skill 目录加入 path
SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)


# =============================================================================
# BANNED PATTERNS - 正则匹配，匹配则直接拒绝
# =============================================================================
BANNED_PATTERNS = [
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

# 白名单来源（允许进入候选列表）
WHITELIST_SOURCES = {
    # 官方技术博客
    "OpenAI Blog", "Anthropic Blog", "Google DeepMind Blog", "Stripe Blog",
    # 顶级开发者博客
    "Andrej Karpathy Blog", "Simon Willison Blog", "Tomasz Tunguz Blog",
    # 学术论文
    "ArXiv cs.AI", "ArXiv cs.CL", "ArXiv cs.LG",
    # 知名技术媒体
    "The Verge Tech", "Ars Technica", "Wired",
    # 其他高质量博客
    "HuggingFace Blog",
}

# 黑名单来源（直接拒绝）
BLACKLIST_SOURCES = {
    # 聚合类内容
    "程序员日报", "开发者头条", "知乎日报",
    "今日头条", "腾讯新闻", "网易新闻",
    # 资讯类翻译
    "机器翻译", "翻译自", "转载",
}

# 高质量作者列表（从 high_quality_authors.json 加载）
HIGH_QUALITY_AUTHORS: Dict[str, List[str]] = {}


def load_high_quality_authors() -> None:
    """加载高质量作者列表"""
    global HIGH_QUALITY_AUTHORS
    try:
        authors_path = os.path.join(SKILL_DIR, "references", "high_quality_authors.json")
        if os.path.exists(authors_path):
            with open(authors_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # 合并 twitter 和 reddit 用户名
                for platform_data in data.values():
                    if isinstance(platform_data, list):
                        for author in platform_data:
                            if isinstance(author, dict):
                                username = author.get("username", "")
                                if username:
                                    platform = author.get("platform", "unknown")
                                    HIGH_QUALITY_AUTHORS.setdefault(platform, []).append(username.lower())
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
GATE_TOTAL_MIN = 3.0


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

    # 检查黑名单
    if platform in BLACKLIST_SOURCES:
        return False, f"黑名单来源: {platform}"

    # 检查白名单
    if platform in WHITELIST_SOURCES:
        return True, "白名单来源"

    # 检查高质量作者（twitter/reddit）
    author = source.get("author", "").lower()
    for platform, authors in HIGH_QUALITY_AUTHORS.items():
        if author in authors:
            return True, f"高质量{platform}作者: {author}"

    # 如果来源是 HN/GitHub Trending，允许（它们有社区筛选）
    if platform in ["Hacker News", "GitHub Trending"]:
        return True, "社区筛选来源"

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
    author = source.get("author", "")

    # 初始化分数
    scores = {gate: 0.5 for gate in QUALITY_GATES}

    # 1. firsthand_experience - 官方博客/个人博客/ArXiv 较高
    if platform in WHITELIST_SOURCES:
        scores["firsthand_experience"] = 0.8
        scores["depth_analysis"] = 0.8
    if "实测" in content or "我们" in content or "I " in content[:100]:
        scores["firsthand_experience"] = max(scores["firsthand_experience"], 0.8)
    if author and author not in ["", "unknown"]:
        scores["firsthand_experience"] = max(scores["firsthand_experience"], 0.7)
    if any(kw in content.lower() for kw in ["data", "result", "experiment", "benchmark", "test"]):
        scores["firsthand_experience"] = max(scores["firsthand_experience"], 0.7)

    # 2. unique_perspective - 原创内容较高
    if any(kw in content for kw in ["我认为", "I think", "my view", "our approach"]):
        scores["unique_perspective"] = 0.8
    if platform in ["Hacker News", "GitHub Trending"]:
        scores["unique_perspective"] = 0.6
    if "综述" in content or "整理" in content or "翻译" in content:
        scores["unique_perspective"] = 0.3

    # 3. depth_analysis - 技术博客/ArXiv 较高
    if "arxiv" in platform.lower() or "research" in platform.lower():
        scores["depth_analysis"] = 0.9
    if any(kw in content.lower() for kw in ["algorithm", "architecture", "performance", "latency", "accuracy"]):
        scores["depth_analysis"] = max(scores["depth_analysis"], 0.7)
    if len(content) > 500:
        scores["depth_analysis"] = max(scores["depth_analysis"], 0.6)

    # 4. practical_value - 工具类/教程类较高，但排除 fluff
    if any(kw in content for kw in ["how to", "tutorial", "guide", "教程", "指南"]):
        if not any(kw in title for kw in ["入门", "新手", "从零开始"]):
            scores["practical_value"] = 0.8
    if any(kw in content for kw in ["code", "implementation", "开源", "github"]):
        scores["practical_value"] = max(scores["practical_value"], 0.7)

    # 降低 fluff 类内容的分数
    fluff_keywords = ["一文读懂", "全面解读", "快速入门", "必备神器"]
    if any(kw in title for kw in fluff_keywords):
        for gate in scores:
            scores[gate] *= 0.5

    total = sum(scores.values())

    # 检查是否通过门控
    passes = all(scores[gate] >= GATE_MIN_SCORE for gate in QUALITY_GATES) and total >= GATE_TOTAL_MIN

    return passes, scores, total


def filter_signals(signals: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], Dict[str, int]]:
    """
    对信号列表应用所有过滤规则。

    Returns:
        (filtered_signals, rejection_stats)
    """
    if not HIGH_QUALITY_AUTHORS:
        load_high_quality_authors()

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
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 JSON 文件路径")
    args = parser.parse_args()

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
    filtered_signals, stats = filter_signals(signals)
    filtered_count = len(filtered_signals)

    # 输出统计
    print(f"\n过滤结果：")
    print(f"  原始信号: {original_count}")
    print(f"  过滤后: {filtered_count}")
    print(f"  去除详情:")
    print(f"    - Banned Pattern: {stats['banned_pattern']}")
    print(f"    - 来源未授权: {stats['source_not_whitelisted']}")
    print(f"    - 质量门控未通过: {stats['quality_gate_failed']}")

    # 保存结果
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    output_data = {
        "signals": filtered_signals,
        "meta": {
            "original_count": original_count,
            "filtered_count": filtered_count,
            "rejection_stats": stats,
            "filter_time": __import__("datetime").datetime.now().isoformat()
        }
    }

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n过滤结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
