"""
Intake Engine: natural language parsing + auto-inference + clarification.

Quality-first principle: must ask when uncertain, never guess when quality risk is high.
"""

import re
from dataclasses import dataclass, field
from pathlib import Path

from shared.platform import normalize_usage, get_ratio, get_density_class, detect_language
from shared.router import resolve_style, load_registry


@dataclass
class IntakeResult:
    """Result of intake processing."""
    topic: str = ""
    usage: str = ""
    ratio: str = "4:5"
    language: str = "chinese"
    style_id: str | None = None
    style_confidence: int = 0
    subtitle: str = ""
    context: str = ""
    banned_elements: list[str] = field(default_factory=list)
    needs_clarification: bool = False
    clarification_question: str = ""


def parse_input(user_input: str) -> tuple[str, str]:
    """Parse natural language input to extract topic and usage signal.

    Returns (topic, raw_usage).
    """
    text = user_input.strip()

    # Common patterns to extract usage (order matters: longer matches first)
    usage_patterns = [
        r"小红书视频封面",
        r"小红书方形封面",
        r"小红书横版封面",
        r"小红书正文配图",
        r"小红书主页背景",
        r"小红书封面",
        r"小红书",
        r"小绿书",
        r"公众号贴图",
        r"公众号次条",
        r"公众号朋友圈",
        r"公众号封面",
        r"公众号",
        r"PPT封面",
        r"PPT",
        r"X封面",
        r"Twitter封面",
        r"商业报告封面",
        r"商业封面",
        r"作品集封面",
        r"咨询分析页",
        r"信息图",
        r"方法论图",
        r"流程图",
        r"矩阵图",
        r"海报",
        r"封面",
    ]

    raw_usage = ""
    for pattern in usage_patterns:
        match = re.search(pattern, text)
        if match:
            raw_usage = match.group(0)
            break

    # Remove usage signal from text to get topic
    topic = text
    if raw_usage:
        topic = text.replace(raw_usage, "").strip()

    # Clean up common prefixes/suffixes and connecting words
    topic = re.sub(r"^(帮我|给我|请|做一张|生成|制作|来一张|的|一张)\s*", "", topic)
    topic = re.sub(r"^(帮我|给我|请|做一张|生成|制作|来一张|的|一张)\s*", "", topic)
    topic = re.sub(r"(蒙德里安|杂志|Bauhaus|bauhaus)\s*风格\s*的?\s*[，,]?\s*", "", topic)
    topic = re.sub(r"^[\s，,]*(主题是|主题|关于)\s*", "", topic)
    topic = re.sub(r"(风格的|风格|的)\s*$", "", topic)
    topic = re.sub(r"(的|吧|呢|呀|啊)\s*$", "", topic)
    topic = topic.strip("，。,. ：: ")

    return topic, raw_usage


def run_intake(user_input: str, skill_dir: Path) -> IntakeResult:
    """Run the full intake pipeline.

    Quality-first: asks clarification when quality risk is high.
    """
    result = IntakeResult()

    # 1. Parse natural language
    topic, raw_usage = parse_input(user_input)
    result.topic = topic

    # 2. Normalize usage
    if raw_usage:
        normalized = normalize_usage(raw_usage)
        if normalized:
            result.usage = normalized
            result.ratio = get_ratio(normalized)

    # 3. Detect language from topic
    result.language = detect_language(topic)

    # 4. Style routing
    registry = load_registry(skill_dir.parent / "styles")
    style_id, confidence = resolve_style(user_input, registry)

    result.style_id = style_id
    result.style_confidence = confidence

    # 5. Determine if clarification is needed (quality-first)
    if not result.usage:
        result.needs_clarification = True
        result.clarification_question = "你想做什么？封面 / 信息图 / 海报？"
        return result

    if result.style_id is None or confidence < 50:
        result.needs_clarification = True
        result.clarification_question = "你想要什么风格？商业分析风 / 杂志编辑风 / 现代艺术风？"
        return result

    # All clear — no clarification needed
    return result
