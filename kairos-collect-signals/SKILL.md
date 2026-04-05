---
name: kairos-collect-signals
description: |
  选题信号采集与角度生成 Skill。当需要确定文章方向、寻找写作灵感时使用。

  触发场景：
  - "帮我看看最近有什么值得写的"
  - "我想找找某个方向的独特角度"
  - "最近有什么热门话题值得关注"
  - "帮我确定一个写作方向"
  - "有什么信号值得关注"

  注意：
  - 关键词可配置（references/keywords.json），适用于任意领域
  - 数据源可插拔（references/sources.json）
  - Agent 使用自己的 LLM 能力生成角度
---

# kairos-collect-signals

## 目的

采集选题信号，为微信公众号生成候选主题和独特角度。关键词和数据源均可配置，适用于任何领域（AI、产品、运营，投资等）。

## 何时使用

- 用户要求寻找写作灵感或方向
- 用户要求分析当前有哪些值得写的信号
- 用户要求确定文章选题角度
- 用户提供了初步方向，需要深入信号分析

## 核心流程

### Step 1: 采集信号

使用 `python3 scripts/collect.py` 采集信号：

```bash
# 用户提供了关键词
python3 scripts/collect.py --tier 1 --limit 100 --keywords "LangChain RAG"

# 用户未提供关键词，使用默认关键词
python3 scripts/collect.py --tier 1 --limit 100
```

- 采集结果保存至 `./.kairos-temp/signals.json`
- 时效性过滤：只采集 3 天内的内容
- 单个源失败不影响整体（try/except）

### Step 2: 读取信号

读取 `./.kairos-temp/signals.json`，理解每个信号的内容和来源。

### Step 3: 去重

```bash
python3 scripts/dedup.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/signals-deduped.json
```

### Step 4: 过滤信号

应用以下规则，按顺序执行：

**规则 1 - Banned Patterns（直接拒绝）**

使用正则匹配，匹配则直接拒绝：

| 模式 | 类型 | 正则 |
|------|------|------|
| 热点炒作 | hot_news | `^.*(刚刚\|重磅\|突发\|震惊\|炸裂).*(发布\|上线\|推出\|宣布).*$` |
| 预测类标题 | predictions | `^.*(十大\|预测\|展望\|趋势).*\d{4}年\|来年.*趋势\|必火.*$` |
| 二道贩子概述 | generic_overview | `^.*(一文读懂\|全面解读\|快速入门\|分钟学会\|一张图读懂).*$` |
| 焦虑营销 | anxiety_marketing | `^.*(AI取代.*职业\|将被淘汰\|即将消失\|逆天\|颠覆认知\|太卷了).*$` |
| 机器翻译泛滥 | translation_fluff | `^.*(让我们深入\|值得注意的是\|本文将探讨\|翻译自).*$` |
| 工具推荐堆砌 | tool_list | `^.*(工具推荐\|必备神器\|10款.*工具\|超级好用.*工具).*$` |
| 入门教程泛滥 | tutorial_fluff | `^.*(从零开始\|新手必看\|入门教程\|上手指南\|小白.*必学).*$` |
| AI生成特征 | ai_generated | `^.*(首先\|其次\|最后\|总之).{0,15}(我们可以看到\|研究表明).*$` |
| 标题党特征 | clickbait | `^.*(竟然\|居然\|万万没想到\|99%的人都不知道\|绝了).*$` |

**规则 2 - Source Whitelist（来源白名单）**

仅以下来源可进入候选列表：

| 来源类型 | 示例 | 状态 |
|----------|------|------|
| 官方技术博客 | OpenAI Blog, Anthropic Blog, Google DeepMind, Stripe Blog | ✅ 白名单 |
| 顶级开发者博客 | Andrej Karpathy, Tomasz Tunguz, Simon Willison | ✅ 白名单 |
| 学术论文 | ArXiv (cs.AI/CL/LG), ACL, NeurIPS | ✅ 白名单 |
| 知名技术媒体 | The Verge Tech, Ars Technica, Wired | ✅ 白名单 |
| 高质量社交作者 | 见 `references/high_quality_authors.json` | ✅ 白名单 |
| 聚合类内容 | 程序员日报, 开发者头条, 知乎日报 | ❌ 禁止 |
| 资讯类翻译 | 机器翻译的海外资讯 | ❌ 禁止 |

**规则 3 - Quality Gates（质量门控）**

每项 >= 0.5 分且总分 >= 3 才通过：

| 门控 | 标准 |
|------|------|
| 一手经验 | 是否有作者亲身测试、实验、数据或案例 |
| 独特观点 | 是否有差异化视角 |
| 深度分析 | 是否有技术深度 |
| 实战价值 | 是否可落地 |

**实验性 - 跨信号合成（Signal Synthesis）**：

在 Step 5 生成角度之前，先将过滤后的信号按主题/技术栈分组。每组选取 2-3 个互补信号，优先组合：
- 不同来源（博客 + 论文）
- 不同角度（问题 + 解决方案）
- 不同深度（现象 + 根因）

这样可以从信号组合中生成比单一信号更丰富的角度。

### Step 5: 生成角度

1. 读取 `references/angle_prompt.md`
2. 将过滤后的 signals 按格式填入 `{SIGNALS}

## Few-Shot 示例

### ✅ 好角度示例

```json
{
  "topic": "RAG 延迟 3 秒：一次生产环境 P99 优化的完整复盘",
  "angle_hint": "从具体延迟数字切入，有完整排查过程",
  "type": "case_study",
  "differentiation": "基于真实生产问题，有具体数据和解决过程",
  "chase_trend": false,
  "quality_score": 0.85,
  "gate_scores": {
    "firsthand_experience": 0.9,
    "unique_perspective": 0.8,
    "depth_analysis": 0.85,
    "practical_value": 0.9
  },
  "angle": "从 3 秒延迟的具体 case 切入，展示完整的问题定位 → 方案选型 → 效果验证过程"
}
```

### ❌ 坏角度示例

```json
{
  "topic": "2026 年 AI 十大趋势预测",
  "angle_hint": "从行业趋势切入",
  "type": "trend_analysis",
  "differentiation": "综合多方观点",
  "chase_trend": true,
  "quality_score": 0.3,
  "gate_scores": {
    "firsthand_experience": 0.1,
    "unique_perspective": 0.2,
    "depth_analysis": 0.3,
    "practical_value": 0.2
  },
  "angle": "预测未来发展方向",
  "reject_reason": "预测类标题，缺少数理依据"
}
```

### ✅ 合格角度示例

```json
{
  "topic": "HuggingFace Transformers 4.40 的 attention 优化分析",
  "angle_hint": "从代码层面切入，有实测数据支撑",
  "type": "technical_explainer",
  "differentiation": "基于官方 release notes 和实测对比",
  "chase_trend": false,
  "quality_score": 0.75,
  "gate_scores": {
    "firsthand_experience": 0.6,
    "unique_perspective": 0.7,
    "depth_analysis": 0.85,
    "practical_value": 0.8
  },
  "angle": "深入分析 SDPA 和 Flash Attention 2 的实现差异，以及在不同硬件上的实测性能对比"
}
```` 占位符（见 angle_prompt.md 中的信号格式化说明）
3. 使用自己的 LLM 能力生成角度
4. 解析 JSON 输出

### Step 6: 输出结果

输出 JSON 格式，字段见下方输出 schema。

### Step 7: 清理临时文件（最后执行）

```bash
python3 scripts/cleanup.py
```

删除 `./.kairos-temp/` 目录。

---

## 输入

```json
{
  "keywords": "LLM RAG",    // 可选：用户提供的关键词
  "tier": 1,                // 可选：采集 tier（默认 1）
  "limit": 100              // 可选：信号数量限制（默认 100）
}
```

## 输出

```json
{
  "signals": [
    {
      "id": "sig-20260403-xxxx",
      "type": "trend",
      "content": "信号描述",
      "source": {
        "platform": "OpenAI Blog",
        "url": "https://...",
        "author": ""
      },
      "relevance_score": 0.85,
      "priority": "P0",
      "published_at": "2026-04-03T10:00:00+08:00"
    }
  ],
  "candidate_topics": [
    {
      "topic": "CoT 不是银弹：三个致命盲区",
      "angle_hint": "从'实际失效场景'切入",
      "source_signals": ["sig-20260403-xxxx"],
      "signals_count": 1,
      "synthesized_group": false,
      "type": "technical_explainer",
      "quality_score": 0.85,
      "gate_scores": {
        "firsthand_experience": 0.9,
        "unique_perspective": 0.8,
        "depth_analysis": 0.85,
        "practical_value": 0.8
      },
      "differentiation": "基于实测，有独特一手经验",
      "chase_trend": false,
      "worth_writing": true,
      "reject_reason": null,
      "angle": "从实测失效场景切入"
    }
  ],
  "meta": {
    "total_signals": 150,
    "signals_filtered": 130,
    "rejected_reasons": {
      "banned_pattern": 45,
      "quality_gate_failed": 60,
      "source_not_whitelisted": 25
    },
    "synthesis_stats": {
      "total_groups": 0,
      "synthesized_angles": 0,
      "avg_signals_per_synthesized_angle": 0
    },
    "candidate_topics_count": 5,
    "collection_time": "2026-04-03T10:00:00+08:00"
  }
}
```

---

## 关键文件

| 文件 | 说明 |
|------|------|
| `scripts/collect.py` | 信号采集脚本 |
| `scripts/dedup.py` | 去重脚本 |
| `scripts/cleanup.py` | 临时文件清理脚本 |
| `references/sources.json` | 数据源配置 |
| `references/keywords.json` | 关键词配置 |
| `references/high_quality_authors.json` | 高质量社交作者白名单 |
| `references/angle_prompt.md` | 角度生成 Prompt 模板 |

---

## 注意事项

1. **先清理再输出**：Step 7 清理临时文件是最后一步，在输出结果之后执行
2. **正则使用 `^` 和 `$`**：确保匹配整行，避免部分匹配导致误判
3. **时区处理**：published_at 使用 ISO 8601 格式，带时区（+08:00）
4. **去重依据**：基于内容哈希去重，保留最新发布的信号
5. **Quality Gates 由 Agent 判断**：使用 LLM 能力评估每项门控

---

## 示例

**输入**：用户说 "我想找找最近有什么值得写的 AI 信号"

**输出**：
```json
{
  "signals": [...],
  "candidate_topics": [
    {
      "topic": "LangChain 内存泄漏的根因分析",
      "angle_hint": "从生产环境踩坑切入，有一手数据",
      "quality_score": 0.88,
      "worth_writing": true
    }
  ],
  "meta": {...}
}
```

## 角度要求

每个角度必须满足以下**必要条件**：

1. **具体数字或场景**：标题/切入角度必须包含具体数据（延迟 ms、% 提升、token 数等）或具体场景（生产问题、实测过程）
   - ❌ "RAG 优化策略" → ✅ "RAG 延迟从 2s 降至 300ms 的优化路径"
   - ❌ "AI Agent 发展趋势" → ✅ "我们在 5 个生产环境部署 Agent 后的教训总结"

2. **一手信息源**：信号来源必须是作者亲身经历，不能是编译/翻译/综述
   - ❌ "据报道..." "有人认为..." "综合多方观点..."
   - ✅ "我们测试了..." "踩坑记录：..."

3. **拒绝泛泛而谈**：不能是"XX 是什么/为什么重要"类型的主题
   - ❌ "一文读懂 LLM"
   - ❌ "AI Agent 入门指南"
   - ✅ 必须有具体切入角度和差异点

"angle": "具体切入角度"
}

## 额外质量检查

生成每个候选角度前，自问：
1. **这个角度普通人能写吗？** 如果能，拒绝（因为没有差异化）
2. **有具体数据或案例支撑吗？** 如果没有，拒绝
3. **这个角度 3 年后还有价值吗？** 如果只是追当下热点，拒绝
4. **信号内容支持这个角度吗？** 如果角度从信号内容中推导不出，拒绝

"default_keywords": [
    "LLM", "RAG", "LangChain", "AI Agent", "Agentic AI",
    "machine learning", "neural network", "embedding",
    "Claude", "GPT-4", "GPT-4o", "Gemini", "Llama", "transformer",
    "prompt engineering", "fine-tuning", "RLHF",
    "vector database", "embedding", "pinecone", "weaviate",
    "AI coding", "cursor", "copilot", "aider",
    "vibe coding", "MCP", "model context protocol",
    "LangGraph", "LlamaIndex", "dspy"
  ]

### Step 5: 生成角度

1. 读取 `references/angle_prompt.md`
2. **实验性 - 合成信号组**：如果过滤后的 signals >= 5 个，先按主题/技术栈分组，选取互补的 2-3 个信号为一组。每组生成 1-2 个角度
3. 将过滤后的 signals（及其分组信息）按格式填入 `{SIGNALS}` 占位符（见 angle_prompt.md 中的信号格式化说明）
4. 使用自己的 LLM 能力生成角度
5. 解析 JSON 输出
