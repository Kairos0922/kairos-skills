"""
Platform routing: usage alias normalization + aspect ratio mapping.

Deterministic code — no AI judgment involved.
"""

# Usage alias → canonical usage mapping
USAGE_ALIASES: dict[str, list[str]] = {
    "X 封面": ["X 封面", "Twitter 封面", "X header", "X封面", "twitter封面"],
    "公众号封面": ["公众号封面", "微信封面", "微信公众号", "微信公众号封面"],
    "PPT 封面": ["PPT 封面", "演示封面", "slides 封面", "PPT封面", "ppt封面"],
    "商业封面": ["商业封面", "商业报告封面", "报告封面"],
    "信息图": ["信息图", "infographic", "信息卡片"],
    "咨询分析页": ["咨询分析页", "分析页", "咨询页"],
    "方法论图": ["方法论图", "方法论", "框架图"],
    "流程图": ["流程图", "步骤图", "工作流图"],
    "矩阵图": ["矩阵图", "四象限", "matrix"],
    "海报": ["海报", "poster", "视觉海报"],
    "作品集封面": ["作品集封面", "portfolio", "作品封面"],
    "小红书封面": ["小红书", "小红书封面", "xiaohongshu"],
    "行程卡": ["行程卡", "行程单", "旅行卡", "itinerary", "行程"],
    "清单卡": ["清单卡", "checklist", "购物清单", "对比清单", "清单"],
    "预算卡": ["预算卡", "budget", "财务卡", "开支明细", "预算"],
    "日程卡": ["日程卡", "schedule", "时间表", "日程表", "日程"],
    "机票": ["机票", "boarding pass", "登机牌", "飞机票"],
    "收据": ["收据", "receipt", "小票", "购物小票"],
    "火车票": ["火车票", "train ticket", "高铁票"],
}

# Canonical usage → aspect ratio
USAGE_RATIO_MAP: dict[str, str] = {
    "X 封面": "5:2",
    "海报": "3:4",
    "公众号封面": "2.35:1",
    "作品集封面": "4:5",
    "PPT 封面": "16:9",
    "商业封面": "16:9",
    "商业报告封面": "16:9",
    "信息图": "4:5",
    "咨询分析页": "4:5",
    "方法论图": "4:5",
    "流程图": "16:9",
    "矩阵图": "1:1",
    "小红书封面": "3:4",
    "行程卡": "3:4",
    "清单卡": "4:5",
    "预算卡": "4:5",
    "日程卡": "3:4",
    "机票": "3:1",
    "收据": "1:2",
    "火车票": "2:1",
}

DEFAULT_RATIO = "4:5"

# Usage → density class (cover vs infographic)
USAGE_DENSITY_CLASS: dict[str, str] = {
    "X 封面": "cover",
    "海报": "cover",
    "公众号封面": "cover",
    "作品集封面": "cover",
    "PPT 封面": "cover",
    "商业封面": "cover",
    "商业报告封面": "cover",
    "小红书封面": "cover",
    "信息图": "infographic",
    "咨询分析页": "infographic",
    "方法论图": "infographic",
    "流程图": "infographic",
    "矩阵图": "infographic",
    "行程卡": "infographic",
    "清单卡": "infographic",
    "预算卡": "infographic",
    "日程卡": "infographic",
    "机票": "infographic",
    "收据": "infographic",
    "火车票": "infographic",
}


def normalize_usage(raw_input: str) -> str:
    """Normalize user-provided usage string to canonical form.

    Returns canonical usage name, or empty string if no match.
    """
    raw_lower = raw_input.strip().lower()
    for canonical, aliases in USAGE_ALIASES.items():
        for alias in aliases:
            if alias.lower() == raw_lower:
                return canonical
    return ""


def get_ratio(usage: str) -> str:
    """Get the optimal aspect ratio for a given usage."""
    return USAGE_RATIO_MAP.get(usage, DEFAULT_RATIO)


def get_density_class(usage: str) -> str:
    """Get the density class (cover/infographic) for a given usage."""
    return USAGE_DENSITY_CLASS.get(usage, "cover")


def detect_language(text: str) -> str:
    """Detect language from text characters.

    Returns 'chinese', 'english', or 'mixed'.
    """
    if not text:
        return "chinese"

    chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
    total_alpha = sum(1 for c in text if c.isalpha())

    if total_alpha == 0:
        return "chinese"

    ratio = chinese_chars / total_alpha
    if ratio > 0.7:
        return "chinese"
    elif ratio < 0.3:
        return "english"
    else:
        return "mixed"
