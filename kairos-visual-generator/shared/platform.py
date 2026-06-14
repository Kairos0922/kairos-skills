"""
Platform routing: usage alias normalization + aspect ratio mapping.

Deterministic code — no AI judgment involved.
"""

# ─── Content type → natural ratio (highest priority) ───
# These ratios reflect real-world artifact proportions.
# AI should determine content_type first, then code selects the ratio.
CONTENT_NATURAL_RATIOS: dict[str, str] = {
    "boarding-pass": "3:1",     # 横向宽幅（登机牌）
    "receipt": "1:2",           # 窄长竖版（收据/小票）
    "train-ticket": "2:1",      # 横向（火车票）
    "invoice": "4:5",           # 竖版（发票）
    "magazine-cover": "3:4",    # 竖版（杂志封面）
    "x-header": "5:2",          # 横向宽幅（X/Twitter header）
    "poster": "1:1",            # 方版（海报）
    "postcard": "3:2",          # 横版（明信片）
    "xiaohongshu-video": "9:16", # 竖版（小红书视频笔记封面）
}

# ─── Usage alias → canonical usage mapping ───
USAGE_ALIASES: dict[str, list[str]] = {
    "X 封面": ["X 封面", "Twitter 封面", "X header", "X封面", "twitter封面"],
    "公众号封面": ["公众号封面", "微信封面", "微信公众号", "微信公众号封面"],
    "公众号次条封面": ["公众号次条", "次条封面", "多图文封面"],
    "公众号朋友圈封面": ["朋友圈封面", "聊天分享封面", "微信朋友圈"],
    "公众号贴图": ["公众号贴图", "小绿书"],
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
    "小红书方形封面": ["小红书方形封面", "小红书方形"],
    "小红书横版封面": ["小红书横版封面", "小红书横版", "小红书风景封面"],
    "小红书视频封面": ["小红书视频封面", "视频笔记封面", "小红书视频"],
    "小红书正文配图": ["小红书正文配图", "小红书配图"],
    "小红书主页背景": ["小红书主页背景", "小红书背景"],
    "行程卡": ["行程卡", "行程单", "旅行卡", "itinerary", "行程"],
    "清单卡": ["清单卡", "checklist", "购物清单", "对比清单", "清单"],
    "预算卡": ["预算卡", "budget", "财务卡", "开支明细", "预算"],
    "日程卡": ["日程卡", "schedule", "时间表", "日程表", "日程"],
    "机票": ["机票", "boarding pass", "登机牌", "飞机票"],
    "收据": ["收据", "receipt", "小票", "购物小票"],
    "火车票": ["火车票", "train ticket", "高铁票"],
}

# ─── Canonical usage → aspect ratio (fallback when no content_type) ───
USAGE_RATIO_MAP: dict[str, str] = {
    "X 封面": "5:2",
    "海报": "3:4",
    "公众号封面": "2.35:1",
    "公众号次条封面": "1:1",
    "公众号朋友圈封面": "1:1",
    "公众号贴图": "3:4",
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
    "小红书方形封面": "1:1",
    "小红书横版封面": "4:3",
    "小红书视频封面": "9:16",
    "小红书正文配图": "3:4",
    "小红书主页背景": "4:3",
    "行程卡": "3:4",
    "清单卡": "4:5",
    "预算卡": "4:5",
    "日程卡": "3:4",
    "机票": "3:1",
    "收据": "1:2",
    "火车票": "2:1",
}

DEFAULT_RATIO = "4:5"

# ─── Usage → density class ───
USAGE_DENSITY_CLASS: dict[str, str] = {
    "X 封面": "cover",
    "海报": "cover",
    "公众号封面": "cover",
    "公众号次条封面": "cover",
    "公众号朋友圈封面": "cover",
    "公众号贴图": "cover",
    "作品集封面": "cover",
    "PPT 封面": "cover",
    "商业封面": "cover",
    "商业报告封面": "cover",
    "小红书封面": "cover",
    "小红书方形封面": "cover",
    "小红书横版封面": "cover",
    "小红书视频封面": "cover",
    "小红书正文配图": "cover",
    "小红书主页背景": "cover",
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
    """Normalize user-provided usage string to canonical form."""
    raw_lower = raw_input.strip().lower()
    for canonical, aliases in USAGE_ALIASES.items():
        for alias in aliases:
            if alias.lower() == raw_lower:
                return canonical
    return ""


def resolve_ratio(content_type: str | None, usage: str) -> str:
    """Resolve aspect ratio with priority: content_type > usage > default.

    Args:
        content_type: Real-world artifact type (e.g., "boarding-pass", "receipt")
        usage: Canonical usage name (e.g., "机票", "行程卡")

    Returns:
        Aspect ratio string (e.g., "3:1", "4:5")
    """
    # Priority 1: content_type → natural ratio
    if content_type and content_type in CONTENT_NATURAL_RATIOS:
        return CONTENT_NATURAL_RATIOS[content_type]

    # Priority 2: usage → ratio
    if usage in USAGE_RATIO_MAP:
        return USAGE_RATIO_MAP[usage]

    # Priority 3: default
    return DEFAULT_RATIO


def get_ratio(usage: str) -> str:
    """Get the optimal aspect ratio for a given usage (convenience wrapper)."""
    return resolve_ratio(None, usage)


def get_density_class(usage: str) -> str:
    """Get the density class (cover/infographic) for a given usage."""
    return USAGE_DENSITY_CLASS.get(usage, "cover")


def detect_language(text: str) -> str:
    """Detect language from text characters."""
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


# ─── Platform specs: machine-readable reference ───
# 用户指令优先级最高，平台默认次之，系统默认最低。
PLATFORM_SPECS: dict[str, dict] = {
    "小红书": {
        "笔记封面图(首选)": {"ratio": "3:4", "width": 1080, "height": 1440, "note": "信息流最大可视区域"},
        "笔记封面图(方形)": {"ratio": "1:1", "width": 1080, "height": 1080, "note": "产品展示、摄影"},
        "笔记封面图(横版)": {"ratio": "4:3", "width": 1440, "height": 1080, "note": "旅游风光、多产品并列"},
        "视频笔记封面": {"ratio": "9:16", "width": 1080, "height": 1920, "note": "竖版视频标准尺寸"},
        "正文配图": {"ratio": "3:4", "width": 1080, "height": 1440, "note": "与封面保持一致"},
        "个人主页背景图": {"ratio": "4:3", "width": 1000, "height": 800, "note": "为头像和简介预留空间"},
    },
    "微信公众号": {
        "首条图文封面": {"ratio": "2.35:1", "width": 1920, "height": 817, "note": "官方推荐适配尺寸，高清输出"},
        "次条/多图文封面": {"ratio": "1:1", "width": 500, "height": 500, "note": "非头条文章专用方图"},
        "朋友圈/聊天分享封面": {"ratio": "1:1", "width": 383, "height": 383, "note": "从首条正中间截取"},
        "公众号贴图(小绿书)": {"ratio": "3:4", "width": 1080, "height": 1440, "note": "沉浸式浏览体验最佳"},
    },
    "X": {
        "文章封面": {"ratio": "5:2", "width": 1500, "height": 600, "note": "最佳比例"},
    },
}

# ─── Output format ───
OUTPUT_FORMAT = "PNG-32"  # 32位无损，24位RGB + 8位alpha
OUTPUT_FORMAT_WEBP = "WebP"  # 可选，用户系统支持时使用
