#!/usr/bin/env python3
"""
analyze.py - 从 signals 生成内部结构化分析，并输出自然语言选题报告

这是一个确定性启发式分析器，用于：
1. 为 skill 提供可重复执行的本地回归测试入口
2. 在没有额外推理支持时，提供基础的结构化分析结果
3. 对外输出自然语言选题报告，而不是 JSON 数据

用法:
    python3 scripts/analyze.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/topic-report.md
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, SKILL_DIR)

from scripts.domain_config import DEFAULT_DOMAIN, load_keywords as load_domain_keywords
from scripts.domain_config import load_profile, load_strategy_config, load_topic_rules, resolve_strategy
from scripts.filter import filter_signals


FAILURE_MARKERS = ["失败", "下降", "泄漏", "错误", "故障", "踩坑", "崩溃", "爆表", "失效"]
TRADEOFF_MARKERS = ["权衡", "tradeoff", "但是", "但", "however", "成本", "准确率", "延迟"]
SCALING_MARKERS = ["延迟", "p99", "吞吐量", "内存", "扩展", "scaling", "规模", "并发"]
UNEXPECTED_MARKERS = ["异常", "unexpected", "反直觉", "不稳定", "偏差"]
CASE_MARKERS = ["复盘", "排查", "教训", "生产环境", "实测", "benchmark"]
FEEDBACK_LOOP_MARKERS = [
    "self-improving ai agent", "self improving agent", "self-improvement loop",
    "reflection loop", "reflective agent", "agent evaluator", "evaluator",
    "verifier", "critic model", "reward hacking", "self-play", "self refinement",
    "self-correction", "recursive improvement", "autonomous improvement",
    "feedback loop", "closed loop", "自动优化", "自我优化", "自反馈",
]
FEEDBACK_LOOP_FAILURE_MARKERS = [
    "reward hacking", "overfit", "drift", "collapse", "oscillation", "regression",
    "self-reinforcing", "hallucination loop", "评估漂移", "奖励投机", "自我强化错误",
    "回归", "退化", "偏航", "振荡",
]
POSITIVE_OUTCOME_MARKERS = ["提升", "增长", "上涨", "增加", "改善", "更高", "翻倍"]
NEGATIVE_OUTCOME_MARKERS = ["下降", "下滑", "恶化", "翻倍", "暴涨", "流失", "回落", "退化", "跑偏", "失效", "腰斩"]
METRIC_MARKERS = [
    "成功率", "准确率", "转化率", "留存", "退款率", "复购率", "客单价",
    "毛利", "点击率", "打开率", "完播率", "投诉率", "活跃率", "成本",
    "利润", "延迟", "吞吐量", "qps", "p99",
]
FOCUS_PATTERNS = [
    r"我们把(?P<focus>[^，。:：]{2,30}?)(?:上线|放到|接入|用于|做成)",
    r"我们让(?P<focus>[^，。:：]{2,30}?)(?:连续|开始|恢复|日更|周更|迭代|运行)",
    r"我们在(?P<focus>[^，。:：]{2,24}?)(?:里|中|上)?(?:踩坑|复盘|排查|测试|实测|发现|验证|优化|上线)",
    r"把(?P<focus>[^，。:：]{2,24}?)(?:从|做成|接入|放到|上线到)",
    r"(?P<focus>[^，。:：]{2,24}?)(?:策略|机制|系统|流程|活动|功能)(?:失效|跑偏|翻车|退化|回归|崩溃)",
    r"(?P<focus>[^，。:：]{2,24}?)(?:成功率|准确率|转化率|留存|退款率|复购率|客单价|毛利|点击率|打开率|完播率|投诉率|活跃率|成本|利润|延迟|吞吐量)",
]
SCENE_LABEL_MARKERS = [
    "直播间", "社群", "课程", "门店", "知识星球", "私域", "电商", "生产环境",
    "多跳问题", "A100", "基准测试", "反馈闭环",
]
GENERIC_READER_SEGMENTS = [
    ("直播间", "运营负责人"),
    ("转化率", "运营负责人"),
    ("退款率", "运营负责人"),
    ("投放", "增长负责人"),
    ("知识星球", "内容主理人"),
    ("续费率", "内容主理人"),
    ("留存", "内容产品负责人"),
    ("课程", "知识产品负责人"),
    ("毛利", "业务负责人"),
    ("复购率", "业务负责人"),
]
KEYWORDS_CACHE: Dict[str, List[str]] = {}
PROFILE_CACHE: Dict[str, Dict[str, Any]] = {}
TOPIC_RULES_CACHE: Dict[str, Dict[str, Any]] = {}


def get_keywords(domain: str) -> List[str]:
    if domain not in KEYWORDS_CACHE:
        KEYWORDS_CACHE[domain] = load_domain_keywords(domain).get("default_keywords", [])
    return KEYWORDS_CACHE[domain]


def get_profile(domain: str) -> Dict[str, Any]:
    if domain not in PROFILE_CACHE:
        PROFILE_CACHE[domain] = load_profile(domain)
    return PROFILE_CACHE[domain]


def get_topic_rules(domain: str) -> Dict[str, Any]:
    if domain not in TOPIC_RULES_CACHE:
        TOPIC_RULES_CACHE[domain] = load_topic_rules(domain)
    return TOPIC_RULES_CACHE[domain]


def infer_focus_keyword(content: str, keywords: List[str], domain: str) -> str:
    rules = get_topic_rules(domain)
    lowered = content.lower()
    for rule in rules.get("focus_overrides", []):
        if any(token.lower() in lowered for token in rule.get("contains_any", [])):
            focus = rule.get("focus", "")
            if focus:
                return focus
    if is_feedback_loop_signal(content):
        return "反馈闭环系统"
    for keyword in sorted(keywords, key=len, reverse=True):
        if keyword.lower() in content.lower():
            return keyword
    generic_focus = extract_generic_focus(content)
    if generic_focus:
        return generic_focus
    for fallback in ["LangChain", "RAG", "Flash Attention", "AI Agent", "LLM"]:
        if fallback.lower() in content.lower():
            return fallback
    return "这个问题"


def clean_focus_candidate(candidate: str) -> str:
    cleaned = candidate.strip(" ：:，。、“”\"'")
    cleaned = re.sub(r"^(我们|我|团队|业务|项目|系统|这套|这个|该)", "", cleaned)
    cleaned = re.sub(r"^\d+\s*", "", cleaned)
    cleaned = re.sub(r"(里|中|上|下|问题|场景|项目|业务)$", "", cleaned)
    cleaned = re.sub(r"^(下单|用户|指标|数据|结果|7日|7 日|30天|14天)$", "", cleaned)
    cleaned = cleaned.strip(" ：:，。、“”\"'")
    if len(cleaned) < 2:
        return ""
    return cleaned[:20]


def extract_generic_focus(content: str) -> str:
    for pattern in FOCUS_PATTERNS:
        match = re.search(pattern, content)
        if match:
            candidate = clean_focus_candidate(match.group("focus"))
            if candidate:
                return candidate
    first_clause = re.split(r"[，。:：；]", content)[0]
    for marker in METRIC_MARKERS:
        idx = first_clause.find(marker)
        if idx > 1:
            candidate = clean_focus_candidate(first_clause[:idx])
            if candidate:
                return candidate
    return ""


def is_feedback_loop_signal(content: str) -> bool:
    lowered = content.lower()
    return any(marker in lowered for marker in FEEDBACK_LOOP_MARKERS)


def classify_tension_type(content: str) -> Optional[str]:
    lowered = content.lower()
    has_positive = any(marker in content for marker in POSITIVE_OUTCOME_MARKERS)
    has_negative = any(marker in content for marker in NEGATIVE_OUTCOME_MARKERS)
    if is_feedback_loop_signal(content) and any(marker in lowered for marker in FEEDBACK_LOOP_FAILURE_MARKERS):
        return "failure"
    if is_feedback_loop_signal(content) and any(token in lowered for token in ["tradeoff", "成本", "latency", "延迟", "verifier cost"]):
        return "tradeoff"
    if ("但" in content or "但是" in content or "却" in content) and has_positive and has_negative:
        return "tradeoff"
    if any(marker in content for marker in FAILURE_MARKERS):
        return "failure"
    if any(marker.lower() in lowered for marker in ["tradeoff"]) or "权衡" in content:
        return "tradeoff"
    if ("只有" in content and "有效" in content) or any(token in content for token in ["效果下降", "准确率下降"]):
        return "failure"
    if any(marker in content for marker in SCALING_MARKERS):
        return "scaling_issue"
    if any(marker in content for marker in UNEXPECTED_MARKERS):
        return "unexpected_behavior"
    return None


def estimate_tension_strength(content: str, tension_type: str) -> float:
    strength = 0.58
    if re.search(r"\d", content):
        strength += 0.08
    if any(marker in content for marker in CASE_MARKERS):
        strength += 0.08
    if is_feedback_loop_signal(content):
        strength += 0.08
    if tension_type in {"failure", "tradeoff"}:
        strength += 0.08
    if ("但" in content or "但是" in content or "却" in content) and any(marker in content for marker in POSITIVE_OUTCOME_MARKERS):
        strength += 0.05
    if any(marker in content for marker in FAILURE_MARKERS):
        strength += 0.06
    if any(marker in content.lower() for marker in FEEDBACK_LOOP_FAILURE_MARKERS):
        strength += 0.06
    return min(0.95, round(strength, 2))


def build_expectation(content: str, tension_type: str, focus: str) -> str:
    if focus == "反馈闭环系统":
        if tension_type == "failure":
            return "反馈闭环系统应该通过反馈持续提升，而不是在闭环里放大错误。"
        if tension_type == "tradeoff":
            return "反馈闭环系统的迭代收益不该被 verifier 成本或评估漂移吞掉。"
        if tension_type == "scaling_issue":
            return "反馈闭环系统在迭代轮次增加后仍应保持稳定与收敛。"
    if tension_type == "failure":
        return f"{focus}应该稳定工作，而不是在关键场景里失效。"
    if tension_type == "tradeoff":
        return f"{focus}的收益不该以隐藏成本或副作用为代价。"
    if tension_type == "scaling_issue":
        return f"{focus}在规模扩大后仍应维持可接受的性能。"
    return f"{focus}应该按预期表现，而不是出现异常偏差。"


def extract_metric_phrases(content: str) -> Dict[str, str]:
    positive_pattern = (
        r"((?:成功率|准确率|转化率|下单转化率|留存|退款率|复购率|续费率|客单价|毛利|点击率|打开率|完播率|投诉率|活跃率|成本|利润|延迟|吞吐量)"
        r"[^，。；]{0,10}?(?:提升|增长|上涨|增加|改善|翻倍)[^，。；]{0,8}?\d+(?:\.\d+)?%?)"
    )
    negative_pattern = (
        r"((?:成功率|准确率|转化率|下单转化率|留存|退款率|复购率|续费率|客单价|毛利|点击率|打开率|完播率|投诉率|活跃率|成本|利润|延迟|吞吐量)"
        r"[^，。；]{0,10}?(?:下降|下滑|恶化|暴涨|流失|回落|退化|翻倍|腰斩)[^，。；]{0,8}?\d*(?:\.\d+)?%?)"
    )
    positive = re.search(positive_pattern, content, re.IGNORECASE)
    negative = re.search(negative_pattern, content, re.IGNORECASE)
    return {
        "positive": positive.group(1) if positive else "",
        "negative": negative.group(1) if negative else "",
    }


def derive_reality(content: str) -> str:
    snippet = re.sub(r"\s+", " ", content).strip()
    return snippet[:140]


def detect_tensions(signals: List[Dict[str, Any]], strategy_config: Dict[str, Any]) -> List[Dict[str, Any]]:
    return detect_tensions_for_domain(signals, strategy_config, DEFAULT_DOMAIN)


def detect_tensions_for_domain(
    signals: List[Dict[str, Any]],
    strategy_config: Dict[str, Any],
    domain: str,
) -> List[Dict[str, Any]]:
    min_strength = strategy_config.get("tension_filter", {}).get("min_strength", 0.6)
    keywords = get_keywords(domain)
    tensions: List[Dict[str, Any]] = []
    for signal in signals:
        content = signal.get("content", "")
        tension_type = classify_tension_type(content)
        if not tension_type:
            continue
        strength = estimate_tension_strength(content, tension_type)
        if strength < min_strength:
            continue
        focus = infer_focus_keyword(content, keywords, domain)
        tensions.append({
            "signal_id": signal.get("id", ""),
            "expectation": build_expectation(content, tension_type, focus),
            "reality": derive_reality(content),
            "tension_type": tension_type,
            "tension_strength": strength,
            "evidence": derive_reality(content),
        })
    return tensions


def build_mechanism(tension: Dict[str, Any], signal: Dict[str, Any], focus: str) -> Dict[str, Any]:
    tension_type = tension["tension_type"]
    content_lower = signal.get("content", "").lower()
    if focus == "反馈闭环系统" and tension_type == "failure":
        mechanism = "系统用自己的评估器或反馈轨道驱动更新时，错误奖励会被反复放大，最终把优化方向带偏。"
        constraints = "常见于 evaluator 不稳定、奖励定义粗糙、反馈链缺少外部校验的闭环系统。"
        chain = [
            "系统依据自评或代理指标决定下一轮改进方向",
            "错误反馈或奖励漏洞进入优化回路",
            "系统持续强化看似更高分但实际更差的行为",
        ]
    elif focus == "反馈闭环系统" and tension_type == "tradeoff":
        mechanism = "为了让系统持续自我优化而引入 verifier、memory、reflection，会把延迟和成本一并推高。"
        constraints = "当每轮优化都依赖额外评估与回放时，这个权衡很难消失。"
        chain = [
            "团队加入 reflection 或 verifier 提升系统质量",
            "每轮任务都叠加评估和重写开销",
            "质量增益被延迟与成本压力部分抵消",
        ]
    elif tension_type == "failure":
        mechanism = f"{focus}在真实约束下暴露了设计假设与生产条件不一致的问题。"
        constraints = "触发条件通常包括生产流量、复杂输入或资源边界。"
        chain = [
            "设计假设过于理想化",
            "真实流量或复杂场景触发隐藏约束",
            "系统出现失败、泄漏或效果下降",
        ]
    elif tension_type == "tradeoff":
        mechanism = f"{focus}的局部优化挤占了另一项关键指标，形成结构性权衡。"
        constraints = "当性能、成本、准确率不能同时最优时，该权衡会持续存在。"
        chain = [
            "团队优先优化单一指标",
            "被忽略的指标持续恶化",
            "整体系统收益低于预期",
        ]
    elif tension_type == "scaling_issue":
        mechanism = f"{focus}在规模扩大时放大了资源竞争和系统瓶颈。"
        constraints = "通常出现在高并发、大上下文或长链路调用场景。"
        chain = [
            "请求规模或上下文长度增长",
            "瓶颈资源开始排队或争用",
            "延迟、吞吐量或稳定性恶化",
        ]
    else:
        mechanism = f"{focus}的输出受隐含变量影响，导致表现偏离预期。"
        constraints = "当输入分布或环境条件变化时更容易触发。"
        chain = [
            "系统依赖未显式建模的条件",
            "条件变化导致行为偏移",
            "出现异常或反直觉结果",
        ]
    inevitable = tension_type in {"failure", "tradeoff", "scaling_issue"}
    return {
        "tension_id": tension["signal_id"],
        "mechanism": mechanism,
        "constraints": constraints,
        "causal_chain": chain,
        "inevitable": inevitable,
    }


def derive_causal_chains(
    tensions: List[Dict[str, Any]],
    signals_by_id: Dict[str, Dict[str, Any]],
    domain: str,
) -> List[Dict[str, Any]]:
    keywords = get_keywords(domain)
    chains: List[Dict[str, Any]] = []
    for tension in tensions:
        signal = signals_by_id.get(tension["signal_id"], {})
        focus = infer_focus_keyword(signal.get("content", ""), keywords, domain)
        chains.append(build_mechanism(tension, signal, focus))
    return chains


def abstract_patterns(causal_chains: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    patterns: List[Dict[str, Any]] = []
    for chain in causal_chains:
        mechanism = chain["mechanism"]
        if "错误奖励" in mechanism or "优化方向带偏" in mechanism:
            pattern = "任何依赖自评或代理指标自我优化的系统，只要反馈失真，就会把错误持续放大。"
            applicability = "自优化工作流、推荐/投放/策略优化系统、agent、自动 prompt/strategy 优化。"
            boundary = "只有在存在稳定外部评估和回滚机制时，这种放大效应才会被抑制。"
        elif "verifier、memory、reflection" in mechanism or "延迟和成本" in mechanism:
            pattern = "任何通过额外评估器换取系统自我提升的流程，都会面临质量收益与成本延迟的结构性权衡。"
            applicability = "verifier、critic model、multi-step reflection、memory replay、运营反馈闭环。"
            boundary = "只有当 verifier 成本可摊薄且收益显著时，这个权衡才值得接受。"
        elif "权衡" in mechanism:
            pattern = "任何只优化单一指标的系统，都会在被忽略指标上积累代价。"
            applicability = "性能优化、模型调参、系统架构权衡。"
            boundary = "仅在指标之间存在真实耦合时成立。"
        elif "规模扩大" in mechanism or "瓶颈" in mechanism:
            pattern = "任何在小规模可行的方案，放大到生产规模后都会暴露资源瓶颈。"
            applicability = "高并发、长上下文、复杂工作流。"
            boundary = "当瓶颈已被显式削峰或隔离时不成立。"
        elif "设计假设" in mechanism:
            pattern = "任何脱离真实约束建立的设计假设，都会在生产环境中以失败形式暴露。"
            applicability = "真实用户输入、生产流量、资源边界。"
            boundary = "前提是系统经过了覆盖这些约束的验证。"
        else:
            pattern = "任何依赖隐含条件的系统，在条件变化后都会产生异常行为。"
            applicability = "多变量输入、复杂推理链、环境敏感流程。"
            boundary = "若关键条件已被显式建模并约束，则风险降低。"
        patterns.append({
            "pattern": pattern,
            "applicability": applicability,
            "boundary": boundary,
            "source_tension_id": chain["tension_id"],
        })
    return patterns


def extract_metric_snippet(content: str) -> str:
    metric_phrases = extract_metric_phrases(content)
    if metric_phrases["negative"]:
        return metric_phrases["negative"]
    if metric_phrases["positive"]:
        return metric_phrases["positive"]
    match = re.search(r"(\d+(?:\.\d+)?\s*(?:ms|s|%|tokens?|qps|倍|次))", content, re.IGNORECASE)
    if match:
        return match.group(1)
    for marker in [
        "内存泄漏", "token 爆表", "响应延迟", "多跳问题", "准确率下降", "吞吐量",
        "reward hacking", "评估漂移", "verifier 成本", "退款率翻倍", "留存下滑",
        "客诉暴涨", "活跃率下滑",
    ]:
        if marker.lower() in content.lower():
            return marker
    return "关键问题"


def extract_failure_hook(content: str) -> str:
    for pattern in [
        r"(成功率下降\s*\d+(?:\.\d+)?%)",
        r"(准确率下降\s*\d+(?:\.\d+)?%)",
        r"(转化率下降\s*\d+(?:\.\d+)?%)",
        r"(续费率下降\s*\d+(?:\.\d+)?%)",
        r"(留存下滑\s*\d+(?:\.\d+)?%)",
        r"(退款率翻倍)",
        r"(投诉率暴涨)",
        r"(下降\s*\d+(?:\.\d+)?%)",
    ]:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1)
    metric_phrases = extract_metric_phrases(content)
    if metric_phrases["negative"]:
        return metric_phrases["negative"]
    for marker in [
        "reward hacking", "评估漂移", "evaluator drift", "内存泄漏", "token 爆表",
        "响应延迟", "退款率翻倍", "客诉暴涨", "活跃率下滑",
    ]:
        if marker.lower() in content.lower():
            return marker
    return extract_metric_snippet(content)


def extract_positive_hook(content: str) -> str:
    metric_phrases = extract_metric_phrases(content)
    if metric_phrases["positive"]:
        return metric_phrases["positive"]
    return extract_metric_snippet(content)


def infer_context_label(content: str) -> str:
    if is_feedback_loop_signal(content):
        return "反馈闭环"
    for marker in SCENE_LABEL_MARKERS:
        if marker.lower() in content.lower():
            return marker
    return "关键场景"


def infer_target_reader(content: str, domain: str) -> str:
    for keyword, reader in GENERIC_READER_SEGMENTS:
        if keyword.lower() in content.lower():
            return reader
    profile = get_profile(domain)
    lowered = content.lower()
    for segment in profile.get("reader_segments", []):
        if any(keyword.lower() in lowered for keyword in segment.get("keywords", [])):
            return segment.get("target_reader", profile.get("default_target_reader", "公众号读者"))
    return profile.get("default_target_reader", "公众号读者")


def infer_article_shape(tension_type: str, domain: str) -> str:
    rules = get_topic_rules(domain)
    profile = get_profile(domain)
    shapes = rules.get("article_shapes", {})
    if tension_type in shapes:
        return shapes[tension_type]
    return profile.get("article_shapes", {}).get(tension_type, "问题拆解型")


def build_why_now(tension_type: str, domain: str) -> str:
    rules = get_topic_rules(domain)
    profile = get_profile(domain)
    templates = rules.get("why_now_templates", {})
    if tension_type in templates:
        return templates[tension_type]
    return profile.get("why_now_templates", {}).get(tension_type, "这个问题已经具备公众号写作价值。")


def build_problem_statement(focus: str, tension: Dict[str, Any]) -> str:
    if tension["tension_type"] == "tradeoff":
        return f"为什么{focus}的局部优化会把收益转化成另一项关键指标的代价？"
    if tension["tension_type"] == "scaling_issue":
        return f"为什么{focus}在规模扩大后会暴露之前看不见的瓶颈？"
    if tension["tension_type"] == "unexpected_behavior":
        return f"为什么{focus}会出现看似偶发、实则有结构原因的异常行为？"
    return f"为什么{focus}会在关键场景中失效，而且这种失效不是偶发事件？"


def build_evidence(signal: Dict[str, Any], tension: Dict[str, Any], mechanism: str) -> List[str]:
    evidence = [tension["evidence"]]
    source = signal.get("source", {})
    platform = source.get("platform")
    published_at = signal.get("published_at", "")
    url = source.get("url", "")
    if platform:
        evidence.append(f"来源: {platform}")
    evidence.append(f"时间: {published_at or '未提供'}")
    if url:
        evidence.append(f"网址: {url}")
    evidence.append(f"机制: {mechanism}")
    return evidence


def generate_topic(
    pattern: Dict[str, Any],
    signal: Dict[str, Any],
    tension: Dict[str, Any],
    mechanism: str,
    domain: str,
) -> Dict[str, Any]:
    content = signal.get("content", "")
    keywords = get_keywords(domain)
    focus = infer_focus_keyword(content, keywords, domain)
    metric = extract_metric_snippet(content)
    failure_hook = extract_failure_hook(content)
    positive_hook = extract_positive_hook(content)
    context_label = infer_context_label(content)
    tension_type = tension["tension_type"]
    target_reader = infer_target_reader(content, domain)
    article_shape = infer_article_shape(tension_type, domain)
    why_now = build_why_now(tension_type, domain)
    problem_statement = build_problem_statement(focus, tension)

    if focus == "反馈闭环系统" and tension_type == "failure":
        topic = f"反馈闭环系统 为什么会在{context_label}里跑偏: 一次围绕 {failure_hook} 的机制复盘"
        core_insight = "只靠系统自评驱动优化，会把错误奖励和伪进步一起放大。"
    elif focus == "反馈闭环系统" and tension_type == "tradeoff":
        topic = f"反馈闭环系统 值不值得做: 从 {metric} 看 reflection 与 verifier 的隐藏成本"
        core_insight = "让系统自我优化并不免费，额外评估回路会把成本和延迟结构性抬高。"
    elif tension_type == "failure":
        topic = f"{focus} 为什么会在{context_label}里失效: 一次围绕 {failure_hook} 的排查复盘"
        core_insight = "真实约束会把被忽略的系统假设放大成显性故障。"
    elif tension_type == "tradeoff":
        topic = f"{focus} 明明把{positive_hook}做上去了，为什么结果却是{failure_hook}"
        core_insight = "局部优化带来的收益，往往会在另一项关键指标上回收成本。"
    elif tension_type == "scaling_issue":
        topic = f"{focus} 一上规模就变慢: 从 {metric} 看系统瓶颈是怎么出现的"
        core_insight = "小规模成立的方案，放大到生产后会受到资源竞争和链路放大的惩罚。"
    else:
        topic = f"{focus} 为什么会出现反直觉结果: 从 {metric} 重新理解系统边界"
        core_insight = "异常行为往往不是偶发，而是隐含条件未被建模。"

    return {
        "topic": topic,
        "problem_statement": problem_statement,
        "why_now": why_now,
        "core_insight": core_insight,
        "angle": tension["reality"],
        "target_reader": target_reader,
        "evidence": build_evidence(signal, tension, mechanism),
        "article_shape": article_shape,
        "type": "problem_solving",
        "source_tension_id": tension["signal_id"],
        "domain": domain,
        "source_platform": signal.get("source", {}).get("platform", "") or "未提供",
        "source_published_at": signal.get("published_at", "") or "未提供",
        "source_url": signal.get("source", {}).get("url", "") or "未提供",
    }


def generate_candidate_topics(
    patterns: List[Dict[str, Any]],
    tensions: List[Dict[str, Any]],
    signals_by_id: Dict[str, Dict[str, Any]],
    mechanisms_by_tension_id: Dict[str, str],
    domain: str,
) -> List[Dict[str, Any]]:
    tensions_by_id = {tension["signal_id"]: tension for tension in tensions}
    topics: List[Dict[str, Any]] = []
    for pattern in patterns:
        source_tension_id = pattern["source_tension_id"]
        tension = tensions_by_id.get(source_tension_id)
        signal = signals_by_id.get(source_tension_id)
        if not tension or not signal:
            continue
        if tension["tension_type"] not in {"failure", "tradeoff", "scaling_issue"}:
            continue
        mechanism = mechanisms_by_tension_id.get(source_tension_id, "")
        topics.append(generate_topic(pattern, signal, tension, mechanism, domain))
    return topics


def analyze_signals(raw_signals: List[Dict[str, Any]], strategy: str = "") -> Dict[str, Any]:
    return analyze_signals_for_domain(raw_signals, strategy, DEFAULT_DOMAIN)


def render_topic_card_markdown(index: int, topic: Dict[str, Any]) -> str:
    evidence_lines = "\n".join(f"- {item}" for item in topic.get("evidence", []))
    source_platform = topic.get("source_platform") or "未提供"
    source_time = topic.get("source_published_at") or "未提供"
    source_url = topic.get("source_url") or "未提供"

    return "\n".join([
        f"## 选题 {index}",
        f"选题题面：{topic.get('topic', '')}",
        f"要回答的问题：{topic.get('problem_statement', '')}",
        f"为什么现在值得写：{topic.get('why_now', '')}",
        f"核心洞察：{topic.get('core_insight', '')}",
        f"建议切口：{topic.get('angle', '')}",
        f"目标读者：{topic.get('target_reader', '')}",
        f"文章形态：{topic.get('article_shape', '')}",
        f"来源：{source_platform}",
        f"时间：{source_time}",
        f"网址：{source_url}",
        "支撑依据：",
        evidence_lines or "- 无",
    ])


def render_report_markdown(result: Dict[str, Any]) -> str:
    meta = result.get("meta", {})
    candidate_topics = result.get("candidate_topics", [])
    lines = [
        "# 微信公众号选题报告",
        f"领域：{meta.get('domain', '')}",
        f"策略：{meta.get('strategy', '')}",
        f"扫描信号数：{meta.get('total_signals', 0)}",
        f"过滤后信号数：{meta.get('signals_filtered', 0)}",
        f"形成选题数：{meta.get('candidate_topics_count', 0)}",
        "",
    ]

    if not candidate_topics:
        rejected = meta.get("rejected_reasons", {})
        lines.extend([
            "本轮没有形成可写选题。",
            f"- banned pattern：{rejected.get('banned_pattern', 0)}",
            f"- 来源未授权：{rejected.get('source_not_whitelisted', 0)}",
            f"- 质量门控未通过：{rejected.get('quality_gate_failed', 0)}",
        ])
        return "\n".join(lines).strip() + "\n"

    lines.append("以下是本轮可写的选题：")
    lines.append("")
    for index, topic in enumerate(candidate_topics, start=1):
        lines.append(render_topic_card_markdown(index, topic))
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def analyze_signals_for_domain(raw_signals: List[Dict[str, Any]], strategy: str, domain: str) -> Dict[str, Any]:
    resolved_strategy = resolve_strategy(domain, strategy)
    strategy_config = load_strategy_config(domain, strategy)
    filtered_signals, rejection_stats = filter_signals(raw_signals, domain=domain, strategy=resolved_strategy)
    signals_by_id = {signal.get("id", ""): signal for signal in filtered_signals}
    tensions = detect_tensions_for_domain(filtered_signals, strategy_config, domain)
    causal_chains = derive_causal_chains(tensions, signals_by_id, domain)
    patterns = abstract_patterns(causal_chains)
    mechanisms_by_tension_id = {chain["tension_id"]: chain["mechanism"] for chain in causal_chains}
    candidate_topics = generate_candidate_topics(patterns, tensions, signals_by_id, mechanisms_by_tension_id, domain)
    result = {
        "signals": filtered_signals,
        "tensions": tensions,
        "causal_chains": causal_chains,
        "patterns": patterns,
        "candidate_topics": candidate_topics,
        "meta": {
            "total_signals": len(raw_signals),
            "signals_filtered": len(filtered_signals),
            "tensions_count": len(tensions),
            "causal_chains_count": len(causal_chains),
            "patterns_count": len(patterns),
            "candidate_topics_count": len(candidate_topics),
            "rejected_reasons": rejection_stats,
            "analysis_time": datetime.now().isoformat(),
            "strategy": resolved_strategy,
            "domain": domain,
        },
    }
    result["report_markdown"] = render_report_markdown(result)
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="信号结构化分析")
    parser.add_argument("--input", required=True, help="输入 JSON 文件路径")
    parser.add_argument("--output", required=True, help="输出 Markdown 报告路径")
    parser.add_argument("--strategy", default="", help="可选：策略目录名，留空则使用领域默认策略")
    parser.add_argument("--domain", default=DEFAULT_DOMAIN, help="领域配置名")
    args = parser.parse_args()

    if not os.path.exists(args.input):
        print(f"错误：输入文件不存在: {args.input}", file=sys.stderr)
        sys.exit(1)

    with open(args.input, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = analyze_signals_for_domain(data.get("signals", []), args.strategy, args.domain)

    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(result["report_markdown"])

    print(f"分析结果已保存至: {args.output}")


if __name__ == "__main__":
    main()
