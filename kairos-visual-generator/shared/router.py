"""
Style router: two-layer routing (explicit keyword > semantic inference).

Deterministic code — AI handles uncertainty in intake.py, not here.
"""

from __future__ import annotations

import json
from pathlib import Path

# Layer 1: explicit style keywords → style ID
EXPLICIT_STYLE_KEYWORDS: dict[str, list[str]] = {
    "mondrian": ["蒙德里安", "De Stijl", "de stijl", "Bauhaus", "bauhaus", "色块风格", "原色风格", "现代主义海报"],
    "swiss": ["麦肯锡", "咨询风", "Swiss", "swiss", "McKinsey", "mckinsey", "BCG", "Bain"],
    "editorial": ["杂志风", "编辑风", "墨水风", "editorial", "Editorial", "衬线风"],
    "ticket": ["票据风", "收据风", "机票", "火车票", "行程卡", "清单卡", "预算卡", "日程卡", "ticket", "receipt", "boarding pass"],
}

# Layer 2: content semantic keywords → style ID
SEMANTIC_STYLE_KEYWORDS: dict[str, list[str]] = {
    "swiss": ["增长", "转化", "漏斗", "策略", "方法论", "框架", "指标", "运营", "商业",
              "AI", "产品", "技术", "系统", "效率", "数据", "模型", "流程"],
    "editorial": ["文化", "机构", "叙事", "评论", "人文", "反思", "深度", "观点",
                  "人物", "组织", "趋势", "洞察", "思想", "哲学"],
    "mondrian": ["设计", "艺术", "建筑", "构成", "创意", "视觉", "品牌", "美学",
                 "蒙德里安", "色彩", "平面", "海报"],
    "ticket": ["行程", "日程", "清单", "预算", "时间轴", "对比", "收据", "发票",
               "清单", "购物", "旅行", "倒计时", "里程碑", "项目计划"],
}

# Minimum keyword matches for high confidence
HIGH_CONFIDENCE_THRESHOLD = 3


def resolve_style(user_input: str, registered_styles: list[dict]) -> tuple[str | None, int]:
    """Resolve style from user input.

    Returns:
        (style_id, confidence) where confidence is 0-100.
        style_id is None when no match found (caller should ask user).
    """
    text = user_input.strip()

    # Layer 1: explicit keyword match (highest priority)
    for style_id, keywords in EXPLICIT_STYLE_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                return style_id, 100

    # Layer 2: semantic keyword inference
    scores: dict[str, int] = {}
    for style_id, keywords in SEMANTIC_STYLE_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text)
        if score > 0:
            scores[style_id] = score

    if not scores:
        return None, 0

    best_style = max(scores, key=scores.get)
    best_score = scores[best_style]

    # Calculate confidence: 0-100 based on match count
    confidence = min(best_score * 25, 100)  # 1 match = 25%, 3+ = 75%+

    if confidence < HIGH_CONFIDENCE_THRESHOLD * 25:
        # Low confidence — caller should ask user
        return best_style, confidence

    return best_style, confidence


def load_registry(styles_dir: Path) -> list[dict]:
    """Load styles registry from styles/registry.json."""
    registry_path = styles_dir / "registry.json"
    with open(registry_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("styles", [])
