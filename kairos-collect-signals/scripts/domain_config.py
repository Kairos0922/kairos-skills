#!/usr/bin/env python3
"""
domain_config.py - 领域配置加载器

约定：
- 领域配置放在 domains/<domain>/
- 策略配置放在 strategies/<strategy>/
- 未提供自定义领域时，回退到内置默认领域 ai-engineering
"""

import json
import os
from typing import Any, Dict, List


SKILL_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_DOMAIN = "ai-engineering"
DEFAULT_STRATEGY = "problem-solving"


def get_domain_dir(domain: str) -> str:
    return os.path.join(SKILL_DIR, "domains", domain)


def get_strategy_dir(strategy: str) -> str:
    return os.path.join(SKILL_DIR, "strategies", strategy)


def load_json(path: str, default: Any) -> Any:
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        return default
    return default


def load_domain_json(
    domain: str,
    filename: str,
    default: Any,
    fallback_domain: str = DEFAULT_DOMAIN,
) -> Any:
    domain_path = os.path.join(get_domain_dir(domain), filename)
    if os.path.exists(domain_path):
        return load_json(domain_path, default)
    if domain != fallback_domain:
        fallback_path = os.path.join(get_domain_dir(fallback_domain), filename)
        if os.path.exists(fallback_path):
            return load_json(fallback_path, default)
    return default


def load_strategy_json(strategy: str, filename: str, default: Any) -> Any:
    strategy_path = os.path.join(get_strategy_dir(strategy), filename)
    return load_json(strategy_path, default)


def deep_merge_dict(base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge_dict(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_profile(domain: str) -> Dict[str, Any]:
    default_profile = {
        "domain": domain,
        "label": domain,
        "description": "",
        "default_target_reader": "公众号作者",
        "article_shapes": {
            "failure": "问题复盘型",
            "tradeoff": "权衡拆解型",
            "scaling_issue": "系统拆解型",
            "unexpected_behavior": "反常识分析型",
        },
        "why_now_templates": {
            "failure": "同类问题正在反复出现，但多数内容只给结论，不解释它为什么必然发生。",
            "tradeoff": "表面收益和隐藏代价正在同时放大，这类题目对公众号读者有真实判断价值。",
            "scaling_issue": "很多方案只在小规模成立，一旦规模放大就会暴露真实瓶颈。",
            "unexpected_behavior": "反直觉现象背后通常隐藏着读者还没看清的条件和边界。",
        },
        "reader_segments": [],
    }
    return load_domain_json(domain, "profile.json", default_profile)


def load_topic_rules(domain: str) -> Dict[str, Any]:
    default_rules = {
        "reader_segments": [],
        "focus_overrides": [],
        "article_shapes": {},
        "why_now_templates": {},
    }
    return load_domain_json(domain, "topic_rules.json", default_rules)


def load_keywords(domain: str) -> Dict[str, Any]:
    return load_domain_json(domain, "keywords.json", {"default_keywords": [], "recency_days": 3})


def load_sources(domain: str) -> Dict[str, Any]:
    return load_domain_json(domain, "sources.json", {"sources": []})


def load_search_queries(domain: str) -> Dict[str, Any]:
    return load_domain_json(domain, "search_queries.json", {"query_sets": {}})


def load_high_quality_authors(domain: str) -> Dict[str, Any]:
    return load_domain_json(
        domain,
        "high_quality_authors.json",
        {"twitter": [], "reddit": [], "meta": {}},
    )


def load_banned_patterns(strategy: str) -> Dict[str, Any]:
    return load_strategy_json(strategy, "banned_patterns.json", {"banned_patterns": []})


def load_strategy_binding(domain: str) -> Dict[str, Any]:
    default_binding = {
        "default_strategy": DEFAULT_STRATEGY,
        "allowed_strategies": [DEFAULT_STRATEGY],
        "strategy_overrides": {},
    }
    return load_domain_json(domain, "strategy_binding.json", default_binding)


def resolve_strategy(domain: str, requested_strategy: str = "") -> str:
    binding = load_strategy_binding(domain)
    strategy = requested_strategy or binding.get("default_strategy", DEFAULT_STRATEGY)
    allowed = binding.get("allowed_strategies", [])
    if allowed and strategy not in allowed:
        raise ValueError(f"strategy '{strategy}' is not allowed for domain '{domain}'")
    return strategy


def load_strategy_config(domain: str, requested_strategy: str = "") -> Dict[str, Any]:
    strategy = resolve_strategy(domain, requested_strategy)
    base_config = load_strategy_json(strategy, "config.json", {})
    binding = load_strategy_binding(domain)
    overrides = binding.get("strategy_overrides", {}).get(strategy, {}).get("config", {})
    return deep_merge_dict(base_config, overrides)


def normalize_keyword_list(values: List[str]) -> List[str]:
    return [value for value in values if isinstance(value, str) and value.strip()]
