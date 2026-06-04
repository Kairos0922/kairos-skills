#!/usr/bin/env python3
"""Assist consulting visual generation with intake checks and metaphor suggestions."""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from typing import Iterable


COVER_USAGES = {
    "x封面",
    "ppt封面",
    "商业报告封面",
    "作品集封面",
    "公众号封面",
    "微信公众号文章封面",
    "小红书",
    "小绿书",
    "海报封面",
}

INFOGRAPHIC_USAGES = {
    "信息图",
    "咨询分析页",
    "方法论图",
    "流程图",
    "矩阵图",
}


@dataclass(frozen=True)
class Metaphor:
    name: str
    reason: str
    keywords: tuple[str, ...]
    cover_hint: str
    infographic_hint: str


METAPHORS: tuple[Metaphor, ...] = (
    Metaphor(
        "漏斗",
        "适合表达筛选、转化、收敛、用户路径、销售流程、机会识别。",
        ("筛选", "转化", "收敛", "用户路径", "销售", "线索", "机会识别", "获客", "留资", "转化率", "漏斗"),
        "用巨型核心词形成收敛负空间，少量节点从入口走向底部结论。",
        "用一个主漏斗承载输入、筛选、转化和输出，左右只保留关键变量。",
    ),
    Metaphor(
        "路径",
        "适合表达战略推进、方法论、增长路线、行动计划、转型进程。",
        ("战略推进", "方法论", "路线", "路径", "行动计划", "转型", "进程", "路线图", "roadmap", "迁移"),
        "让路径线穿过重构文字，形成起点、转折和终点。",
        "用一条主路径组织阶段、动作和里程碑，从现状走向目标。",
    ),
    Metaphor(
        "阶梯",
        "适合表达升级、价值提升、能力进阶、商业成熟度、定价层级。",
        ("升级", "提升", "进阶", "成熟度", "定价", "层级", "增长阶梯", "能力", "价值提升", "level"),
        "把主视觉文字做成上升台阶，底部留出短结论。",
        "用阶梯呈现层级、门槛和价值递进，每一级只保留短标签。",
    ),
    Metaphor(
        "矩阵",
        "适合表达定位、比较、选择、竞争格局、优先级判断。",
        ("定位", "比较", "选择", "竞争", "格局", "优先级", "矩阵", "象限", "评估", "对比"),
        "把标题嵌入极简网格或象限骨架，突出一个决策位置。",
        "用矩阵承载维度、选项和判断，标出机会区或推荐象限。",
    ),
    Metaphor(
        "坐标",
        "适合表达市场地图、战略定位、机会区间、风险收益关系。",
        ("市场地图", "战略定位", "机会区间", "风险收益", "坐标", "地图", "区间", "象限图", "收益"),
        "用坐标轴切入主视觉文字，少量标注显示方向和机会。",
        "用双轴坐标组织市场、风险、收益和位置判断。",
    ),
    Metaphor(
        "飞轮",
        "适合表达增长循环、复利机制、网络效应、持续运转系统。",
        ("增长循环", "复利", "网络效应", "循环", "持续", "飞轮", "闭环", "自增长", "增长引擎"),
        "让圆形动势围绕核心词旋转，但只保留一层循环。",
        "用一个飞轮解释输入、驱动、反馈和复利结果。",
    ),
    Metaphor(
        "节点网络",
        "适合表达系统协同、组织连接、技术架构、资源关系。",
        ("协同", "连接", "架构", "资源关系", "节点", "网络", "生态", "组织", "系统", "关系"),
        "用细节点连接标题笔画，形成克制的系统关系图。",
        "用节点网络展示角色、资源、链路和关键连接。",
    ),
    Metaphor(
        "数据流",
        "适合表达信息流动、自动化、效率提升、输入输出关系。",
        ("信息流", "数据流", "自动化", "效率", "输入", "输出", "流动", "pipeline", "工作流", "ai agent"),
        "让数据线穿过核心词，从输入侧流向输出侧。",
        "用单向数据流组织输入、处理、自动化节点和输出结果。",
    ),
    Metaphor(
        "门槛",
        "适合表达准入、筛选、风险控制、阶段关口、决策标准。",
        ("准入", "门槛", "筛选", "风险控制", "关口", "决策标准", "审核", "准入标准", "gate"),
        "把标题置于一道极简阈值线两侧，形成通过与未通过。",
        "用阶段关口展示标准、判断、通过条件和下一阶段。",
    ),
    Metaphor(
        "窗口",
        "适合表达市场机会、时间窗口、突破口、趋势入口。",
        ("市场机会", "时间窗口", "窗口", "突破口", "趋势", "入口", "风口", "机会", "时机"),
        "在核心词中打开一个窗口负空间，露出机会方向。",
        "用窗口结构呈现趋势、进入条件、机会边界和行动建议。",
    ),
    Metaphor(
        "防线",
        "适合表达风险管理、治理机制、合规控制、安全边界。",
        ("风险治理", "治理体系", "风险管理", "治理", "合规", "安全", "边界", "防线", "控制", "风控", "审计", "监管", "风险"),
        "用细线防线切分标题，突出边界、约束和保护。",
        "用多道防线展示风险来源、控制机制和治理结果。",
    ),
    Metaphor(
        "断层",
        "适合表达结构变化、代际变化、产业转折、认知差距。",
        ("结构变化", "代际", "转折", "认知差距", "断层", "分化", "断裂", "变革", "拐点"),
        "让标题被一道断层切开，形成旧秩序与新秩序对比。",
        "用断层结构呈现变化前后、影响变量和新机会。",
    ),
    Metaphor(
        "容器",
        "适合表达价值承载、商业模式、资源池、收益池。",
        ("承载", "商业模式", "资源池", "收益池", "容器", "资产池", "价值池", "平台", "portfolio"),
        "把主视觉文字做成承载空间，少量价值点沉入容器。",
        "用容器表达资源输入、价值沉淀、收益输出和边界。",
    ),
    Metaphor(
        "罗盘",
        "适合表达方向选择、战略判断、长期定位、路径导航。",
        ("方向", "战略判断", "长期定位", "导航", "罗盘", "选择", "愿景", "north star", "定位"),
        "把核心词与方向刻度融合，突出一个清晰指向。",
        "用罗盘组织方向、判断维度、权衡因素和推荐路径。",
    ),
    Metaphor(
        "建筑结构",
        "适合表达组织架构、能力底座、系统搭建、治理框架。",
        ("组织架构", "底座", "搭建", "治理框架", "建筑", "结构", "体系", "框架", "基座", "能力底座"),
        "把标题建筑化为立面或承重结构，突出底座和框架。",
        "用建筑剖面展示底座、支柱、治理层和目标层。",
    ),
)


def normalize(value: str) -> str:
    return value.strip().lower()


def classify_usage(usage: str) -> str:
    normalized = normalize(usage)
    if any(item in normalized for item in COVER_USAGES):
        return "cover"
    if any(item in normalized for item in INFOGRAPHIC_USAGES):
        return "infographic"
    return "cover"


def common_ratio_for_usage(usage: str) -> str | None:
    normalized = normalize(usage)
    if "x封面" in normalized:
        return "5:2"
    if "ppt封面" in normalized or "商业报告封面" in normalized or "咨询分析页" in normalized:
        return "16:9"
    if "小红书" in normalized or "小绿书" in normalized or "海报封面" in normalized:
        return "4:5"
    return None


def intake_questions(title: str, usage: str, ratio: str, context: str) -> list[str]:
    questions: list[str] = []

    if not title.strip():
        questions.append("请提供主题词或主标题。")
    if not usage.strip():
        questions.append("这张图的用途是什么：封面、信息图、咨询分析页、流程图还是矩阵图？")
    if usage.strip() and not ratio.strip() and common_ratio_for_usage(usage) is None:
        questions.append("画幅比例是什么：5:2、16:9、4:5、3:4 还是 1:1？")

    generic_terms = ("增长", "战略", "转型", "机会", "风险", "方法论", "趋势", "商业化")
    title_is_generic = title.strip() in generic_terms or len(title.strip()) <= 4
    if title.strip() and title_is_generic and not context.strip():
        questions.append("请补充行业背景、目标受众或使用场景，避免隐喻和结构选偏。")

    return questions[:3]


def score_metaphor(metaphor: Metaphor, text: str) -> tuple[int, list[str]]:
    matches = [keyword for keyword in metaphor.keywords if keyword.lower() in text]
    return sum(max(1, len(keyword)) for keyword in matches), matches


def select_metaphor(title: str, usage: str, context: str) -> dict[str, object]:
    text = normalize(" ".join(part for part in (title, usage, context) if part))
    mode = classify_usage(usage)
    ranked: list[tuple[int, int, Metaphor, list[str]]] = []

    for index, metaphor in enumerate(METAPHORS):
        score, matches = score_metaphor(metaphor, text)
        ranked.append((score, -index, metaphor, matches))

    ranked.sort(reverse=True, key=lambda item: (item[0], item[1]))
    score, _, metaphor, matches = ranked[0]

    if score == 0:
        metaphor = next(item for item in METAPHORS if item.name == "路径")
        matches = []

    hint = metaphor.cover_hint if mode == "cover" else metaphor.infographic_hint
    return {
        "metaphor": metaphor.name,
        "reason": metaphor.reason,
        "matched_keywords": matches,
        "mode": mode,
        "composition_hint": hint,
        "rule": "Use exactly one main metaphor. Do not stack multiple metaphors.",
    }


def build_intake_result(title: str, usage: str, ratio: str, context: str) -> dict[str, object]:
    questions = intake_questions(title, usage, ratio, context)
    inferred_ratio = ratio.strip() or common_ratio_for_usage(usage)
    return {
        "ready": not questions,
        "questions": questions,
        "inferred_ratio": inferred_ratio,
        "rule": "If ready is false, ask these questions before generating the final visual.",
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--title", required=True, help="User title or topic.")
    parser.add_argument("--usage", default="", help="Output usage, such as X封面 or 信息图.")
    parser.add_argument("--ratio", default="", help="Canvas ratio, such as 5:2, 16:9, 4:5, 3:4, or 1:1.")
    parser.add_argument("--context", default="", help="Optional industry or audience context.")
    parser.add_argument("--check-intake", action="store_true", help="Check whether user input is sufficient before generation.")
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.check_intake:
        result = build_intake_result(args.title, args.usage, args.ratio, args.context)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0

    result = select_metaphor(args.title, args.usage, args.context)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
