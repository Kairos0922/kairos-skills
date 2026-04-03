# kairos-collect-signals 重构设计文档

**日期**: 2026-04-03
**版本**: v2.0
**状态**: 设计中（已根据审阅意见更新）

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-04-03 | 初始设计 |
| v2.0 | 2026-04-03 | 根据 CTO/PM/工程师审阅意见更新 |

---

## 1. 背景与目标

### 1.1 现状分析

| 项目 | ai-signal (现有) | kairos-collect-signals (当前) |
|------|-----------------|------------------------------|
| 数据源 | Tavily + HN + GH + AlphaXiv | 72 个 RSS/API/HTML 源 |
| 关键词配置 | 固定痛点关键词 | JSON 可配置 |
| 搜索源 | 依赖 Tavily API | 固定 |
| 平台支持 | 通用 | 通用 |
| 角度生成 | 多维评分 | 规则 + 评分 |
| Skill 规范 | 非官方格式 | 遵循 agentskills.io |

### 1.2 目标

重构 `kairos-collect-signals`，成为一个**遵循 agentskills.io 规范的通用写作选题切口生成器**：

1. **模块化 Source Adapter 架构** — 数据源可配置、可扩展
2. **可配置关键词** — 通过 JSON 管理搜索关键词
3. **可配置搜索源** — Tavily/SerpAPI/自定义 API
4. **LLM 角度生成** — 为每个信号生成独特写作切口
5. **多平台输出** — 微信公众号为主，小红书/抖音独立字段
6. **遵循 Skill 规范** — SKILL.md frontmatter + progressive disclosure

### 1.3 目标用户（已明确）

**Phase 1 聚焦**：微信公众号 AI 技术深度作者

| 用户特征 | 需求 |
|---------|------|
| 技术背景 | 有 AI/ML 技术背景，追求深度解读 |
| 写作风格 | 3000+ 字深度技术文，有独特视角 |
| 内容价值 | 长期价值，非热点追风 |

> 小红书、抖音支持作为 Phase 2/3 扩展，不在 Phase 1 范围内。

---

## 2. 设计原则

### 2.1 agentskills.io 规范遵循

| 规范要求 | 实现方式 |
|---------|---------|
| `name` 字段 | `kairos-collect-signals`（小写+连字符） |
| `description` 字段 | 1024字符内，描述"做什么"+"何时用" |
| 渐进式披露 | name/description 启动时加载；SKILL.md body 激活时加载 |
| 目录结构 | SKILL.md + README.md + scripts/ + references/ + evals/ |
| SKILL.md 限制 | < 500 行，< 5000 tokens |

### 2.2 Skill Description 触发设计

```yaml
description: |
  选题信号采集与角度生成。当需要确定文章方向、寻找写作灵感时使用。

  触发场景：
  - "帮我看看最近有什么值得写的"
  - "我想找找 AI 编程的独特角度"
  - "最近有哪些高质量的 LLM 信号"
  - "帮我确定一个写作方向"
  - "有什么值得写的选题吗"

  目标用户：微信公众号 AI 技术深度作者
```

---

## 3. 架构设计

### 3.1 目录结构

```
kairos-collect-signals/
├── SKILL.md                      # Skill 定义（纯指令，无硬编码路径）
├── README.md                     # 人类可读文档
├── src/
│   ├── __init__.py
│   ├── skill.py                 # Skill 主逻辑（入口）
│   ├── adapters/
│   │   ├── __init__.py
│   │   ├── base.py              # BaseAdapter 抽象类
│   │   ├── rss_adapter.py       # RSS/Atom 适配器
│   │   ├── api_adapter.py       # REST API 适配器
│   │   ├── search_adapter.py    # 搜索 API 适配器（Tavily）
│   │   └── html_adapter.py      # HTML 解析适配器
│   ├── config/
│   │   ├── __init__.py
│   │   ├── sources.json         # 数据源配置（从现有 72 源迁移）
│   │   └── keywords.json        # 关键词配置（从现有迁移）
│   ├── aggregators/
│   │   ├── __init__.py
│   │   ├── signal_aggregator.py # 信号聚合 + 去重 + 归一化评分
│   │   └── normalizer.py        # relevance_score 归一化
│   ├── generators/
│   │   ├── __init__.py
│   │   └── angle_generator.py   # LLM 角度生成器
│   ├── filters/
│   │   ├── __init__.py
│   │   └── topic_filter.py      # 选题过滤规则
│   └── models.py                # 数据模型（Signal, CandidateTopic）
├── scripts/
│   └── run.py                   # CLI 入口
└── evals/
    └── evals.json                # 测试用例（5个现有用例 + 扩展）
```

### 3.2 数据流（含错误处理）

```
用户输入（话题/关键词）
    ↓
① Source Adapter 并发采集（错误隔离）
   ├── RSS Adapter（72 源配置）
   ├── Search Adapter（Tavily）
   └── API Adapter（HN API）
         ↓
② 信号聚合 + 去重（三层去重）
         ↓
③ relevance_score 归一化
         ↓
④ Top N 信号筛选（LLM 调用限流，最多 20 个）
         ↓
⑤ LLM 角度生成
         ↓
⑥ 选题过滤
   ├── Banned Patterns（禁止选题）
   └── Translation Whitelist（豁免规则）
         ↓
⑦ 评分排序 + 输出
```

### 3.3 去重策略（三层）

| 层级 | 策略 | 说明 |
|------|------|------|
| L1 | URL 完全相同 | 直接去重 |
| L2 | 内容 simhash 相似度 > 0.9 | 内容重复检测 |
| L3 | 来源 + 时间窗口 | 同源同话题 24h 内只保留最新 |

### 3.4 错误隔离机制

```python
# 每个 Adapter 调用独立 try/except
async def collect_all(self, adapters: List[BaseAdapter]) -> List[Signal]:
    all_signals = []
    errors = []

    tasks = []
    for adapter in adapters:
        task = self._safe_fetch(adapter)
        tasks.append(task)

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for adapter, result in zip(adapters, results):
        if isinstance(result, Exception):
            errors.append({"adapter": adapter.name, "error": str(result)})
            continue  # 单个失败不影响整体
        all_signals.extend(result)

    return all_signals, errors
```

### 3.5 relevance_score 归一化

各 Adapter 返回原始信号后，由 `SignalAggregator` 统一计算归一化分数：

```python
def normalize_score(self, signal: Signal, sources_config: dict) -> float:
    """
    归一化评分公式：
    score = base_score * source_weight * time_decay * keyword_match
    """
    source_weight = sources_config.get(signal.source['platform'], {}).get('weight', 1.0)
    time_decay = self._calculate_time_decay(signal.published_at)
    keyword_match = self._calculate_keyword_match(signal.content, self.keywords)

    return min(1.0, signal.base_score * source_weight * time_decay * keyword_match)
```

### 3.6 LLM 调用限流

| 参数 | 值 | 说明 |
|------|-----|------|
| `MAX_LLM_SIGNALS` | 20 | 最多 20 个信号触发 LLM |
| `LLM_MODEL` | `claude-sonnet-4-20250514` | 默认模型（成本平衡） |
| `LLM_MAX_TOKENS` | 2000 | 单次调用最大 Token |

> LLM 调用前按 `relevance_score` 排序，只处理 Top 20 信号。

---

## 4. Source Adapter 接口（已修正）

### 4.1 BaseAdapter 抽象类

```python
# src/adapters/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ValidationResult:
    """验证结果，区分不同错误状态"""
    available: bool
    latency_ms: Optional[float] = None
    error_type: Optional[str] = None  # network_timeout | http_error | parse_error
    error_message: Optional[str] = None

@dataclass
class RawSignal:
    """Adapter 返回的原始信号（未归一化评分）"""
    title: str
    url: str
    platform: str
    author: str
    published_at: datetime
    snippet: str
    raw_score: float = 0.5  # Adapter 原始分数，不同学Adapter标准不同

class BaseAdapter(ABC):
    name: str
    source_type: str  # rss | api | search | html

    @abstractmethod
    async def fetch(self, limit: int) -> List[RawSignal]:
        """
        获取信号。

        Adapter 只负责"采集"，过滤逻辑统一由 Filter 层处理。
        关键词过滤不在此层进行，由 SignalAggregator 统一处理。
        """
        pass

    async def validate(self) -> ValidationResult:
        """验证数据源是否可用，返回详细信息"""
        pass
```

### 4.2 各 Adapter 实现差异

| Adapter | fetch() 参数 | 特殊处理 |
|---------|-------------|---------|
| RSSAdapter | `limit` | 解析 RSS/Atom |
| APIAdapter | `limit` | HN API 调用 |
| SearchAdapter | `limit, query` | Tavily/SerpAPI |
| HTMLAdapter | `limit` | BeautifulSoup 解析 |

```python
# SearchAdapter 需要 query 参数，与其他 Adapter 不同
class SearchAdapter(BaseAdapter):
    def __init__(self, query: str):
        self.query = query
        super().__init__()

    async def fetch(self, limit: int) -> List[RawSignal]:
        # 使用 self.query 搜索
        pass
```

---

## 5. 数据模型（已补全）

### 5.1 Signal 模型

```python
@dataclass
class Signal:
    id: str
    type: str  # trend | event | question | debate
    content: str
    source: dict  # platform, url, author
    relevance_score: float  # 归一化后的分数（0-1）
    priority: str  # P0 | P1 | P2
    published_at: str
    expires_at: str
```

### 5.2 CandidateTopic 模型（完整字段）

```python
@dataclass
class CandidateTopic:
    topic: str                    # 角度标题
    angle_hint: str               # 切入说明
    source_signals: List[str]     # 相关信号 IDs
    signals_count: int            # 相关信号数量
    top_signal: dict              # 最相关的信号
    type: str                     # technical_explainer | tool_review | opinion_commentary | ...
    value_score: float            # 0-1，长期价值评分
    differentiation: str          # 差异化说明
    chase_trend: bool             # 是否在追热点
    值得写吗: bool                 # 综合判断
    拒绝理由: Optional[str]       # 如果不值得写，说明原因
    platforms: dict = None        # 多平台输出建议
```

### 5.3 完整输出格式

```json
{
  "signals": [
    {
      "id": "sig-20260403-xxxx",
      "type": "trend",
      "content": "Why Chain-of-Thought Reasoning Fails in Practice",
      "source": {
        "platform": "HuggingFace Blog",
        "url": "https://huggingface.co/blog/...",
        "author": ""
      },
      "relevance_score": 0.85,
      "priority": "P0",
      "published_at": "2026-04-03T10:00:00+08:00",
      "expires_at": "2026-04-05T10:00:00+08:00"
    }
  ],
  "candidate_topics": [
    {
      "topic": "CoT 不是银弹：三个致命盲区",
      "angle_hint": "从'实际失效场景'切入，不是泛泛谈 CoT",
      "source_signals": ["sig-20260403-xxxx", "sig-20260403-yyyy"],
      "signals_count": 2,
      "top_signal": {信号对象},
      "type": "technical_explainer",
      "value_score": 0.85,
      "differentiation": "基于实测，有独特一手经验",
      "chase_trend": false,
      "值得写吗": true,
      "拒绝理由": null,
      "platforms": {
        "wechat": {
          "format": "深度技术文",
          "length": "3000+ 字",
          "angle": "适合技术深度解析"
        }
      }
    }
  ],
  "meta": {
    "total_signals": 150,
    "signals_after_dedup": 89,
    "signals_for_llm": 20,
    "sources_used": ["OpenAI Blog", "HuggingFace"],
    "sources_failed": ["Anthropic News"],
    "collection_time": "2026-04-03T10:00:00+08:00"
  }
}
```

---

## 6. 数据源配置（sources.json）

### 6.1 配置格式

```json
{
  "sources": [
    {
      "name": "OpenAI Blog",
      "adapter": "rss",
      "url": "https://openai.com/blog/rss.xml",
      "tier": 1,
      "category": "official",
      "weight": 1.0,
      "enabled": true
    },
    {
      "name": "HuggingFace Blog",
      "adapter": "rss",
      "url": "https://huggingface.co/blog/feed.xml",
      "tier": 1,
      "category": "tool",
      "weight": 0.9,
      "enabled": true
    },
    {
      "name": "Tavily Search",
      "adapter": "search",
      "api_type": "tavily",
      "api_key_env": "TAVILY_API_KEY",
      "tier": 1,
      "category": "search",
      "weight": 1.2,
      "enabled": true,
      "notes": "搜索源，支持关键词配置"
    }
  ],
  "categories": {
    "official": { "weight": 1.0, "description": "官方技术博客" },
    "research": { "weight": 0.9, "description": "学术研究" },
    "thought_leader": { "weight": 0.85, "description": "思想领袖" },
    "tool": { "weight": 0.8, "description": "工具/框架博客" },
    "community": { "weight": 0.7, "description": "社区讨论" },
    "media": { "weight": 0.6, "description": "媒体报道" },
    "search": { "weight": 1.2, "description": "搜索结果" }
  }
}
```

### 6.2 数据源分类（已添加 category）

| category | weight | 说明 |
|----------|--------|------|
| official | 1.0 | 官方技术博客 |
| research | 0.9 | 学术研究 |
| thought_leader | 0.85 | 思想领袖 |
| tool | 0.8 | 工具/框架博客 |
| community | 0.7 | 社区讨论 |
| media | 0.6 | 媒体报道 |
| search | 1.2 | 搜索结果（高权重） |

---

## 7. 关键词配置（keywords.json）

### 7.1 配置格式

```json
{
  "keywords": [
    "agent",
    "agent memory",
    "agent evaluation",
    "LLM",
    "large language model",
    "GPT",
    "Claude",
    "Gemini",
    "multimodal",
    "reasoning",
    "chain-of-thought",
    "RAG",
    "fine-tuning",
    "inference",
    "benchmark",
    "evaluation",
    "context window",
    "memory",
    "attention"
  ],
  "topic_keywords": {
    "LLM": ["large language model", "GPT", "Claude", "Gemini", "multimodal"],
    "Agent": ["agent", "agent memory", "agent evaluation", "agent orchestration"],
    "推理": ["reasoning", "chain-of-thought", "CoT"]
  }
}
```

### 7.2 关键词更新策略

| 机制 | 说明 |
|------|------|
| 手动更新 | 用户可编辑 `keywords.json` |
| 自动建议 | LLM 定期分析新出现的关键词，建议添加到配置 |
| 频率 | 建议每月审视一次关键词列表 |

---

## 8. 选题过滤规则

### 8.1 Banned Patterns（禁止选题）

| 模式 | 类型 | 拒绝理由 |
|------|------|---------|
| "刚刚，OpenAI又发布..." | hot_news | 热点话题，泛滥内容 |
| "2026年AI十大预测！" | predictions | 无长期价值 |
| "一文读懂AI前世今生！" | generic_overview | 二道贩子特征 |
| "AI取代XXX职业！" | anxiety_marketing | 标题党 |

### 8.2 Translation Whitelist（豁免规则）

| 来源 | 条件 | 状态 |
|------|------|------|
| 官方技术博客 (OpenAI/Claude/DeepMind) | 有深度技术解读 | ✅ 豁免 |
| 大佬博客 (Andrej Karpathy等) | 有独特观点或一手经验 | ✅ 豁免 |
| 资讯类翻译 | 无深度内容 | ❌ 禁止 |

### 8.3 过滤优先级

```
信号 → Banned Patterns 检测 → 如果命中直接拒绝
      → Translation Whitelist 检测 → 如果未豁免则标记
      → 评分排序 → 输出
```

---

## 9. LLM 角度生成

### 9.1 Prompt 模板

```prompt
你是一个写作角度策划专家。根据以下信号，为每个信号生成一个独特的写作角度。

## 信号
{信号列表（最多20条）}

## 目标用户
微信公众号 AI 技术深度作者，3000+ 字深度技术文

## 要求
1. 每个角度必须独特，不是泛泛而谈
2. 说明差异化：为什么我们能写别人写不了的
3. 评估是否在追热点（chase_trend）
4. 给出 value_score (0-1)
5. 只输出高价值角度（value_score > 0.5）

## 输出格式
JSON 数组，每个元素包含：
{
  "topic": "角度标题",
  "angle_hint": "切入说明",
  "type": "technical_explainer | tool_review | opinion_commentary | ...",
  "differentiation": "差异化说明",
  "chase_trend": true/false,
  "value_score": 0-1
}
```

### 9.2 Prompt 版本管理

```python
# src/generators/prompts/
#   v1_default.txt      # 默认 Prompt
#   v2_longform.txt     # 长文优化
#   v3_xiaohongshu.txt  # 小红书优化（Phase 2）
```

---

## 10. SKILL.md 设计（已修正）

### 10.1 设计原则

1. **纯指令式**：不依赖硬编码路径或外部 Python 解释器
2. **渐进式披露**：核心指令在 SKILL.md，详细参考在 references/
3. **< 500 行**：将详细配置和示例拆分到 references/

### 10.2 Frontmatter

```yaml
---
name: kairos-collect-signals
description: |
  选题信号采集与角度生成。当需要确定文章方向、寻找写作灵感时使用。

  触发场景：
  - "帮我看看最近有什么值得写的"
  - "我想找找 AI 编程的独特角度"
  - "最近有哪些高质量的 LLM 信号"
  - "帮我确定一个写作方向"
  - "有什么值得写的选题吗"

  目标用户：微信公众号 AI 技术深度作者
---

# kairos-collect-signals

## 核心能力

1. **多源并发采集**: RSS/API/搜索 API，支持配置化扩展
2. **三层去重**: URL/内容相似度/时间窗口
3. **统一评分**: 归一化 relevance_score
4. **LLM 角度生成**: Top 20 信号触发 LLM
5. **选题过滤**: Banned Patterns + Translation Whitelist

## 使用方式

当用户需要确定写作方向或寻找选题灵感时，激活此 Skill。

### 处理流程

1. 加载 `references/sources.json` 和 `references/keywords.json`
2. 并发调用 Source Adapters 采集信号（单个 Adapter 失败不影响整体）
3. 三层去重 + relevance_score 归一化
4. Top 20 信号触发 LLM 角度生成
5. 应用选题过滤规则
6. 评分排序，输出结果

### 输出

JSON 结构化输出，包含：
- `signals`: 原始信号列表（带归一化分数）
- `candidate_topics`: 候选角度列表（含多平台建议）
- `meta`: 元信息（采集时间、去重数量、失败源）

### 关键文件

| 文件 | 说明 |
|------|------|
| `src/skill.py` | Skill 主入口 |
| `src/adapters/` | 数据源适配器 |
| `references/sources.json` | 72 个数据源配置 |
| `references/keywords.json` | 关键词配置 |
| `src/aggregators/signal_aggregator.py` | 信号聚合 + 去重 + 归一化 |
| `src/generators/angle_generator.py` | LLM 角度生成 |
| `src/filters/topic_filter.py` | 选题过滤规则 |

### 选题过滤规则

#### Banned Patterns（直接拒绝）

- ❌ hot_news: "刚刚，OpenAI又发布..."
- ❌ predictions: "2026年AI十大预测！"
- ❌ generic_overview: "一文读懂AI前世今生！"
- ❌ anxiety_marketing: "AI取代XXX职业！"

#### Translation Whitelist（豁免条件）

- ✅ 官方技术博客 (OpenAI/Claude/DeepMind): 必须有深度技术解读
- ✅ 大佬博客 (Andrej Karpathy等): 必须有独特观点

### 错误处理

- 单个 Adapter 失败：记录到 `meta.sources_failed`，不影响其他源
- LLM 调用失败：返回已采集信号，标注角度生成失败
- 网络超时：Adapter 独立 try/catch，partial success 策略

### LLM 调用限制

- 最多 20 个信号触发 LLM（按 relevance_score 排序）
- 默认模型：`claude-sonnet-4-20250514`
- 单次最大 Token：2000

---

## 11. Phase 规划（已明确边界）

### Phase 1：MVP（目标：可投入使用）

| 交付物 | 验收标准 |
|-------|---------|
| 模块化 Adapter 架构 | RSS/HTML/API Adapter 可用 |
| 72 源配置迁移 | sources.json 完整迁移 |
| 三层去重 + 归一化 | 去重率 > 30% |
| LLM 角度生成 | Top 20 信号生成角度 |
| 选题过滤 | Banned Patterns + Whitelist |
| SKILL.md | 符合 agentskills.io 规范 |
| 评估体系 | 5 个现有用例 + 2 个新用例 |

**Phase 1 输出**：wechat 平台为主（其他平台字段为空）

### Phase 2：搜索增强

| 交付物 | 说明 |
|-------|------|
| Tavily 搜索适配器 | 关键词搜索 |
| SerpAPI fallback | Google 搜索备选 |
| 关键词动态更新建议 | LLM 分析新关键词 |

### Phase 3：多平台扩展

| 平台 | 字段 |
|------|------|
| wechat | format, length, angle |
| xiaohongshu | format, length, angle |
| douyin | format, duration, angle |

### Phase 4：质量优化

| 交付物 | 说明 |
|-------|------|
| 角度新颖度评分 | 避免重复角度 |
| 人工标注数据集 | evals 扩展 |
| Prompt 版本管理 | prompts/ 目录 |

---

## 12. 评估体系（已细化）

### 12.1 现有 5 个用例迁移

```json
{
  "skill_name": "kairos-collect-signals",
  "evals": [
    {
      "id": 1,
      "prompt": "帮我看看最近有什么值得写的AI信号，我想找一个独特的写作角度",
      "expected_output": "收集AI领域的信号，输出结构化的signals列表和candidate_topics",
      "assertions": [
        "输出是有效的JSON格式",
        "signals 是非空数组",
        "candidate_topics 是非空数组",
        "每个 candidate_topic 包含 value_score, differentiation, chase_trend, 值得写吗"
      ]
    },
    {
      "id": 2,
      "prompt": "我在关注 LLM 领域，有什么高质量的信号可以帮我确定写作方向？",
      "expected_output": "基于LLM关键词过滤的信号收集",
      "assertions": [
        "signals 数组非空",
        "至少 50% 信号与 LLM/AI 相关",
        "candidate_topics 非空"
      ]
    },
    {
      "id": 3,
      "prompt": "最近看到一篇讲GPT-5发布快讯的文章，感觉可以写一下，你觉得呢？",
      "expected_output": "热点类内容应被识别并降低优先级",
      "assertions": [
        "如果包含 GPT-5 发布相关 topic，则 chase_trend 为 true 或 value_score < 0.5"
      ]
    },
    {
      "id": 4,
      "prompt": "OpenAI官方博客最近有一篇关于GPT-5技术原理的深度解析，值得写吗？",
      "expected_output": "官方技术博客应该被豁免进入候选列表",
      "assertions": [
        "candidate_topics 非空",
        "至少一个候选主题 type 为 technical_explainer"
      ]
    },
    {
      "id": 5,
      "prompt": "有什么关于AI编程工具的信号？我想找找有没有独特角度",
      "expected_output": "收集AI编程相关信号，differentiation 字段非空",
      "assertions": [
        "candidate_topics 非空",
        "每个 candidate_topic 包含 differentiation 字段"
      ]
    }
  ]
}
```

### 12.2 新增测试用例（针对新架构）

```json
{
  "new_evals": [
    {
      "id": 6,
      "prompt": "帮我采集信号，忽略任何网络错误",
      "expected_output": "部分 Adapter 失败时仍返回可用信号",
      "assertions": [
        "signals 非空数组",
        "meta.sources_failed 包含失败源列表"
      ]
    },
    {
      "id": 7,
      "prompt": "帮我看看有没有重复的信号",
      "expected_output": "去重后信号数量 < 去重前",
      "assertions": [
        "meta.signals_after_dedup < meta.total_signals"
      ]
    }
  ]
}
```

---

## 13. 风险与应对

| 风险 | 应对策略 |
|------|---------|
| LLM API 调用成本 | Top 20 信号限制，成本可控 |
| Tavily API 不可用 | SerpAPI fallback，Phase 2 实现 |
| 网络不稳定 | Adapter 错误隔离，partial success |
| 角度生成质量 | Prompt 迭代优化，持续评估 |
| 数据源失效 | health_check 验证，长期失败源降级 |
| 关键词过时 | 每月审视更新 keywords.json |

---

## 14. 与 ai-signal 对比

| 维度 | ai-signal | kairos-collect-signals v2 |
|------|-----------|--------------------------|
| 数据源 | 4 个固定源 | 72 个可配置源 |
| 关键词 | 固定 | JSON 可配置 |
| 去重 | 无 | 三层去重 |
| 评分 | 多维评分 | 统一归一化评分 |
| 角度生成 | 多维评分 | LLM 生成独特角度 |
| 错误处理 | 无 | Adapter 隔离 |
| 平台支持 | 通用 | 微信公众号为主 |
| Skill 规范 | 非官方 | 遵循 agentskills.io |
