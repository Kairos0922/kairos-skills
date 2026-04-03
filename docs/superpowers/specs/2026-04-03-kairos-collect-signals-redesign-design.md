# kairos-collect-signals 重构设计文档

**日期**: 2026-04-03
**版本**: v4.1
**状态**: 设计中

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-04-03 | 初始设计 |
| v2.0 | 2026-04-03 | 根据 CTO/PM/工程师审阅意见更新 |
| v3.0 | 2026-04-03 | 修正 Skill 设计原则：Skill 是指令集，Agent 执行，不包含 LLM API 调用 |
| v4.0 | 2026-04-03 | 深度优化：新增 9 项 Banned Patterns、Quality Gates 四项门控、Source Whitelist；针对公众号高质量内容优化 |
| v4.1 | 2026-04-04 | 修复：临时文件改到本地临时目录、高质量社交作者白名单、时效性3天、默认关键词搜索 |

---

## 1. 背景与目标

### 1.1 现状分析

| 项目 | ai-signal (现有) | kairos-collect-signals (新) |
|------|-----------------|------------------------------|
| 数据源 | Tavily + HN + GH + AlphaXiv | 72 个 RSS/API/HTML 源 |
| 关键词配置 | 固定痛点关键词 | JSON 可配置 |
| 搜索源 | 依赖 Tavily API | 可配置搜索源 |
| 角度生成 | 多维评分 | Agent 自己用 LLM 能力生成 |
| Skill 规范 | 非官方格式 | 遵循 agentskills.io |

### 1.2 目标

重构 `kairos-collect-signals`，成为一个**遵循 agentskills.io 规范的选题信号采集 Skill**：

1. **模块化脚本架构** — Agent 调用脚本采集数据
2. **可配置关键词** — JSON 管理
3. **选题过滤** — Banned Patterns + Translation Whitelist
4. **Prompt 模板** — Agent 生成角度用
5. **遵循 Skill 规范** — SKILL.md 是指令集，不是程序

### 1.3 目标用户

**Phase 1 聚焦**：微信公众号 AI 技术深度作者

---

## 2. Skill 设计原则（核心）

### 2.1 什么是 Skill

**Skill = 指令集，不是独立程序。**

```
Agent 激活 Skill → Agent 读取 SKILL.md → Agent 执行指令
                                            ↓
                                    调用 scripts/ 中的脚本
                                    或使用自己的 LLM 能力
```

### 2.2 Skill 能包含什么

| 类型 | 说明 |
|------|------|
| **指令** | SKILL.md 中的步骤说明 |
| **脚本** | Agent 通过 Bash 调用（Python/Shell） |
| **Prompt 模板** | Agent 自己填充并执行 |
| **配置** | JSON/YAML 数据文件 |

### 2.3 Skill 不能包含什么

| 类型 | 说明 |
|------|------|
| ❌ LLM API 调用代码 | Agent 本身就是 LLM，不需要调用外部 API |
| ❌ 独立的 HTTP 服务 | Skill 不是服务 |
| ❌ 单独运行的进程 | Agent 执行，不是后台运行 |

### 2.4 "LLM 角度生成" 在哪

**在 Agent 自己的 LLM 能力里，不在代码里。**

Skill 提供：
- Prompt 模板（在 `references/` 或 SKILL.md 里）
- 输出格式要求

Agent 读取信号后，用自己的 LLM 能力生成角度。

---

## 3. 目录结构

```
kairos-collect-signals/
├── SKILL.md                      # Skill 定义（指令集）
├── README.md                     # 人类可读文档
├── scripts/
│   ├── collect.py               # 信号采集脚本
│   ├── dedup.py                 # 去重脚本
│   └── cleanup.py               # 临时文件清理脚本
├── references/
│   ├── sources.json             # 数据源配置（RSS/API/HTML 源）
│   ├── keywords.json            # 关键词配置（默认搜索关键词）
│   ├── high_quality_authors.json # 高质量作者白名单（Twitter/Reddit）
│   ├── banned_patterns.json     # 禁止选题模式
│   └── angle_prompt.md          # 角度生成 Prompt 模板
└── evals/
    └── evals.json               # 测试用例
```

**临时文件管理**：
- 所有过程文件存放在 `./.kairos-temp/` 目录
- 任务结束后自动清理（Agent 执行 `python3 scripts/cleanup.py`）
- 不使用 `/tmp` 目录

---

## 4. 工作流程

```
用户请求 → Agent 激活 Skill → Agent 执行：

Step 1: 采集信号
   └─ Bash: python3 scripts/collect.py --tier 1 --limit 100 --keywords "{用户关键词}"
   └─ 如果用户未提供关键词：使用 references/keywords.json 中的默认关键词
   └─ 时效性过滤：只采集 3 天内的内容
   └─ 输出: ./.kairos-temp/signals.json

Step 2: 读取信号
   └─ Agent: 读取 JSON 文件

Step 3: 去重
   └─ Bash: python3 scripts/dedup.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/signals-deduped.json

Step 4: 过滤信号
   └─ Agent: 应用 Banned Patterns 和 Whitelist 规则
   └─ 时效性：3 天以内的信号

Step 5: 生成角度
   └─ Agent: 使用 references/angle_prompt.md 的 Prompt
   └─ Agent: 使用自己的 LLM 能力生成角度

Step 6: 输出结果
   └─ Agent: 输出 JSON 格式

Step 7: 清理临时文件
   └─ Bash: python3 scripts/cleanup.py
   └─ 删除 ./.kairos-temp/ 目录
```

---

## 5. 各步骤详细说明

### Step 1: 采集信号

**执行者**: Bash（通过 Agent 调用）

**脚本**: `scripts/collect.py`

**功能**:
- 读取 `references/sources.json` 获取数据源
- 并发采集 RSS/API/HTML 源
- 单个源失败不影响整体（try/except）
- **时效性过滤**：只采集 3 天内的内容
- **关键词逻辑**：
  - 如果用户提供了关键词：使用用户关键词
  - 如果用户未提供：使用 `references/keywords.json` 中的默认关键词
- 输出到 `./.kairos-temp/signals.json`

**调用方式**:
```bash
# 用户提供关键词
python3 scripts/collect.py --tier 1 --limit 100 --keywords "LangChain RAG"

# 用户未提供关键词，使用默认关键词
python3 scripts/collect.py --tier 1 --limit 100
```

**输出格式**:
```json
{
  "signals": [
    {
      "id": "sig-20260403-xxxx",
      "type": "trend",
      "content": "Why Chain-of-Thought Reasoning Fails...",
      "source": {
        "platform": "HuggingFace Blog",
        "url": "https://...",
        "author": ""
      },
      "relevance_score": 0.85,
      "priority": "P0",
      "published_at": "2026-04-03T10:00:00+08:00"
    }
  ],
  "meta": {
    "total_signals": 150,
    "sources_used": ["OpenAI Blog", "HuggingFace"],
    "sources_failed": [],
    "collection_time": "2026-04-03T10:00:00+08:00"
  }
}
```

### Step 2: 读取信号

**执行者**: Agent（读取 JSON 文件）

**文件**: `./.kairos-temp/signals.json`

### Step 3: 去重

**执行者**: Bash（通过 Agent 调用）

**脚本**: `scripts/dedup.py`

**功能**:
- 基于信号内容哈希去重
- 保留发布时间更新的信号
- 输出到 `./.kairos-temp/signals-deduped.json`

**调用方式**:
```bash
python3 scripts/dedup.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/signals-deduped.json
```

### Step 7: 清理临时文件

**执行者**: Bash（任务结束时执行）

**脚本**: `scripts/cleanup.py`

**功能**:
- 删除 `./.kairos-temp/` 目录及其所有内容
- 确保不残留临时文件

**调用方式**:
```bash
python3 scripts/cleanup.py
```

### Step 4: 过滤信号

**执行者**: Agent（根据规则自己判断）

**规则**: 见第 6 节

**Banned Patterns**: 直接拒绝
**Translation Whitelist**: 豁免或标记

### Step 5: 生成角度

**执行者**: Agent（使用自己的 LLM 能力）

**Prompt**: `references/angle_prompt.md`

**Agent 行为**:
1. 读取 `references/angle_prompt.md`
2. 将过滤后的 signals 填充到 Prompt
3. 使用自己的 LLM 能力生成角度
4. 解析 JSON 输出

### Step 6: 输出结果

**执行者**: Agent

**格式**: 见第 7 节

---

## 6. 过滤规则

### 6.1 Banned Patterns（直接拒绝）

以下模式**直接拒绝**，不进入候选列表：

| 模式 | 类型 | 拒绝理由 | 正则示例 |
|------|------|---------|---------|
| 热点炒作 | hot_news | 热点话题，泛滥内容 | `/(刚刚\|重磅\|突发\|震惊\|炸裂).*(发布\|上线\|推出\|宣布)/` |
| 预测类标题 | predictions | 无长期价值 | `/(十大\|预测\|展望\|趋势).*\d{4}年\|来年.*趋势\|必火/` |
| 二道贩子概述 | generic_overview | 二手信息重组，无一手经验 | `/一文读懂\|全面解读\|快速入门\|分钟学会\|一张图读懂\|深入浅出.*介绍/` |
| 焦虑营销 | anxiety_marketing | 标题党，情绪操控 | `/AI取代.*职业\|将被淘汰\|即将消失\|逆天\|颠覆认知\|太卷了/` |
| 机器翻译泛滥 | translation_fluff | 无深度内容，翻译腔 | `/(让我们深入\|值得注意的是\|本文将探讨\|翻译自)/` |
| 工具推荐堆砌 | tool_list | 无深度体验，流水账式 | `/工具推荐\|必备神器\|10款.*工具\|超级好用.*工具/` |
| 入门教程泛滥 | tutorial_fluff | 基础内容，无独特价值 | `/从零开始\|新手必看\|入门教程\|上手指南\|小白.*必学/` |
| AI生成特征 | ai_generated | AI批量生产特征 | `/(首先\|其次\|最后\|总之).{0,15}(我们可以看到\|研究表明\|显而易见)/` |
| 标题党特征 | clickbait | 夸张标题 | `/竟然\|居然\|万万没想到\|99%的人都不知道\|绝了/` |

### 6.2 Quality Gates（质量门控）

**每个信号必须通过以下所有门控**，使用 Agent + LLM 判断：

| 门控 | 标准 | 检验方式 |
|------|------|---------|
| **一手经验** | 包含作者亲身测试、实验、数据、案例 | 关键词：实测、自己、我的实验、我们发现、我们测试、代码实现 |
| **独特观点** | 不是泛泛而谈，有差异化视角 | 非综述类，非对比类，有独特结论 |
| **深度分析** | 不是浅层介绍，有技术深度 | 包含代码/数据/架构/原理/分析 |
| **实战价值** | 可落地，不是纯理论 | 包含案例/实操/经验/踩坑/总结 |

**Agent 质量评估 Prompt**：
```
你是内容质量评审员。评估以下信号是否通过质量门控。

信号内容：{content}
信号来源：{source}

评估标准（每项 0-1 分）：
1. 一手经验：是否有作者亲身测试、实验、数据或案例？
2. 独特观点：是否有差异化视角？不是泛泛而谈？
3. 深度分析：是否有技术深度？不是浅层介绍？
4. 实战价值：是否可落地？不是纯理论？

通过条件：总分 >= 3 且每项 >= 0.5

输出 JSON：
{
  "quality_score": 总分,
  "pass": true/false,
  "reasons": ["优势...", "劣势..."],
  "gate_scores": {
    "firsthand_experience": 分数,
    "unique_perspective": 分数,
    "depth_analysis": 分数,
    "practical_value": 分数
  }
}
```

### 6.3 Source Whitelist（来源白名单）

**仅以下来源可进入候选列表**，其余直接拒绝：

| 来源类型 | 示例 | 状态 |
|----------|------|------|
| 官方技术博客 | OpenAI Blog, Anthropic Blog, Google DeepMind, Stripe Blog | ✅ 白名单 |
| 顶级开发者博客 | Andrej Karpathy, Tomasz Tunguz, Simon Willison | ✅ 白名单 |
| 学术论文 | ArXiv (cs.AI/CL/LG), ACL, NeurIPS | ✅ 白名单 |
| 知名技术媒体 | The Verge Tech, Ars Technica, Wired | ✅ 白名单 |
| **高质量社交作者** | 见 `references/high_quality_authors.json` | ✅ 白名单 |
| 聚合类内容 | 程序员日报, 开发者头条, 知乎日报 | ❌ 禁止 |
| 资讯类翻译 | 机器翻译的海外资讯 | ❌ 禁止 |
| 普通社交内容 | Twitter/X, Reddit 非白名单内容 | ❌ 禁止 |

### 6.4 内容类型过滤

| 类型 | 处理方式 |
|------|---------|
| 新闻报道 | ❌ 禁止（太时效性，无长期价值） |
| 产品介绍 | ⚠️ 仅当有深度评测/对比时保留 |
| 教程/入门 | ❌ 禁止（泛滥，无独特价值） |
| 观点评论 | ✅ 保留，需有独特视角 |
| 技术深度文 | ✅ 保留，核心目标 |
| 实战案例 | ✅ 保留，最高价值 |
| 工具评测 | ✅ 保留，需有真实体验 |

---

## 7. 输出格式

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
      "angle_hint": "从'实际失效场景'切入，不是泛泛谈 CoT",
      "source_signals": ["sig-20260403-xxxx"],
      "signals_count": 1,
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
      "platforms": {
        "wechat": {
          "format": "深度技术文",
          "length": "3000+ 字",
          "angle": "从实测失效场景切入"
        }
      }
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
    "candidate_topics_count": 5,
    "collection_time": "2026-04-03T10:00:00+08:00"
  }
}
```

**字段说明**：

| 字段 | 类型 | 说明 |
|------|------|------|
| `quality_score` | float | 质量总分（0-1），由 gate_scores 平均 |
| `gate_scores` | object | 四项质量门控得分 |
| `worth_writing` | bool | 是否值得写（替代"值得写吗"） |
| `reject_reason` | string/null | 拒绝理由（如果 worth_writing=false） |
| `rejected_reasons` | object | 过滤统计（meta 中） |
| `chase_trend` | bool | 是否追热点（应尽量避免） |
| `angle` | string | 公众号专属角度提示 |

---

## 8. SKILL.md 设计

### 8.1 Frontmatter

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

  注意：此 Skill 提供指令，Agent 使用自己的 LLM 能力生成角度。
---

# kairos-collect-signals

## 流程

1. **采集信号**: `python3 scripts/collect.py --tier 1 --limit 100 --keywords "{用户关键词}"`（用户未提供关键词时使用默认关键词）
2. **读取信号**: 读取 `./.kairos-temp/signals.json`
3. **去重**: `python3 scripts/dedup.py --input ./.kairos-temp/signals.json --output ./.kairos-temp/signals-deduped.json`
4. **过滤**: 应用 Banned Patterns 和 Whitelist 规则
5. **生成角度**: 使用 `references/angle_prompt.md` 的 Prompt
6. **输出**: JSON 格式
7. **清理**: `python3 scripts/cleanup.py`（删除 `./.kairos-temp/`）

## 过滤规则

### Step 1: Banned Patterns（直接拒绝）

使用正则匹配以下模式，匹配则直接拒绝：

- ❌ hot_news: `/(刚刚|重磅|突发|震惊|炸裂).*(发布|上线|推出|宣布)/`
- ❌ predictions: `/(十大|预测|展望|趋势).*\d{4}年|来年.*趋势|必火/`
- ❌ generic_overview: `/一文读懂|全面解读|快速入门|分钟学会|一张图读懂/`
- ❌ anxiety_marketing: `/AI取代.*职业|将被淘汰|即将消失|逆天|颠覆认知|太卷了/`
- ❌ translation_fluff: `/(让我们深入|值得注意的是|本文将探讨|翻译自)/`
- ❌ tool_list: `/工具推荐|必备神器|10款.*工具|超级好用.*工具/`
- ❌ tutorial_fluff: `/从零开始|新手必看|入门教程|上手指南|小白.*必学/`
- ❌ ai_generated: `/(首先|其次|最后|总之).{0,15}(我们可以看到|研究表明)/`
- ❌ clickbait: `/竟然|居然|万万没想到|99%的人都不知道|绝了/`

### Step 2: Source Whitelist（来源白名单）

**来源类型**：

| 来源类型 | 示例 | 状态 |
|----------|------|------|
| 官方技术博客 | OpenAI Blog, Anthropic Blog, Google DeepMind, Stripe Blog | ✅ 白名单 |
| 顶级开发者博客 | Andrej Karpathy, Tomasz Tunguz, Simon Willison | ✅ 白名单 |
| 学术论文 | ArXiv (cs.AI/CL/LG), ACL, NeurIPS | ✅ 白名单 |
| 知名技术媒体 | The Verge Tech, Ars Technica, Wired | ✅ 白名单 |
| **高质量社交作者** | 见 `references/high_quality_authors.json` | ✅ 白名单 |
| 聚合类内容 | 程序员日报, 开发者头条, 知乎日报 | ❌ 禁止 |
| 资讯类翻译 | 机器翻译的海外资讯 | ❌ 禁止 |
| 普通社交内容 | Twitter/Reddit 泛泛热帖 | ❌ 禁止 |

**高质量社交作者白名单**（`references/high_quality_authors.json`）：
- Twitter/X 上有独特观点的 AI 开发者、研究者
- Reddit (r/MachineLearning, r/LocalLLaMA) 上有深度的讨论
- 配置字段：`username`, `platform`, `bio`, `followers_threshold`

**社交媒体采集逻辑**：
1. 仅采集白名单作者的推文/帖子
2. 非白名单作者的社交内容直接拒绝
3. 白名单作者的内容仍需通过 Banned Patterns 和 Quality Gates

### Step 3: Quality Gates（质量门控）

使用 Agent + LLM 评估，每项 >= 0.5 分且总分 >= 3：

1. **一手经验**：是否有作者亲身测试/实验/数据？
2. **独特观点**：是否有差异化视角？
3. **深度分析**：是否有技术深度？
4. **实战价值**：是否可落地？

## 角度生成

Agent 使用 `references/angle_prompt.md` 中的 Prompt 模板，
结合自己的 LLM 能力生成独特角度。

## 输出格式

```json
{
  "signals": [...],
  "candidate_topics": [...],
  "meta": {...}
}
```

详细字段说明见 `references/output_schema.json`。

## 关键文件

| 文件 | 说明 |
|------|------|
| `scripts/collect.py` | 信号采集脚本 |
| `scripts/dedup.py` | 去重脚本 |
| `references/sources.json` | 72 个数据源配置 |
| `references/keywords.json` | 关键词配置 |
| `references/banned_patterns.json` | 禁止选题模式 |
| `references/angle_prompt.md` | 角度生成 Prompt 模板 |
```

---

## 9. 参考文件

### 9.1 references/sources.json

```json
{
  "sources": [
    {
      "name": "OpenAI Blog",
      "url": "https://openai.com/blog/rss.xml",
      "type": "rss",
      "tier": 1,
      "category": "official",
      "enabled": true
    },
    {
      "name": "HuggingFace Blog",
      "url": "https://huggingface.co/blog/feed.xml",
      "type": "rss",
      "tier": 1,
      "category": "official",
      "enabled": true
    },
    {
      "name": "Twitter - Anthropic",
      "url": "https://twitter.com/AnthropicAI",
      "type": "twitter",
      "tier": 1,
      "category": "twitter",
      "enabled": true
    }
  ]
}
```

### 9.2 references/keywords.json

```json
{
  "default_keywords": [
    "LLM", "RAG", "LangChain", "AI Agent",
    "machine learning", "neural network",
    "Claude", "GPT-4", "transformer"
  ],
  "recency_days": 3
}
```

### 9.3 references/high_quality_authors.json

```json
{
  "twitter": [
    {
      "username": "anthropic",
      "display_name": "Anthropic",
      "bio": "AI safety and research",
      "description": "官方账号，发布 Claude 相关技术解读"
    },
    {
      "username": "kaborl",
      "display_name": "OpenClover 作者",
      "bio": "Building open source AI tools",
      "description": "OpenClover 作者，AI 工具深度实践"
    },
    {
      "username": "amasad",
      "display_name": "Riley Goodside",
      "bio": "LLM prompting techniques",
      "description": "LLM prompting 专家，独特视角"
    }
  ],
  "reddit": [
    {
      "subreddit": "MachineLearning",
      "description": "高质量 ML 讨论"
    },
    {
      "subreddit": "LocalLLaMA",
      "description": "本地 LLM 部署实践"
    }
  ]
}
```

### 9.4 references/angle_prompt.md

```markdown
# 角度生成 Prompt

你是一个写作角度策划专家，为微信公众号 AI 技术深度文生成独特角度。

## 信号

{SIGNALS}

## 角度生成要求

1. **禁止二道贩子**：必须是原创视角，不能是综述/对比/入门介绍
2. **一手经验**：角度必须有实测/案例/踩坑，不能是纯理论
3. **独特差异化**：说明为什么我们能写别人写不了的
4. **追热点警告**：如果是热点（chase_trend=true），必须有独特深度视角
5. **质量门槛**：value_score > 0.6 才能输出

## 公众号专属角度要求

每个角度必须包含：
- **切入角度**：不是泛泛而谈，从具体场景切入
- **独特视角**：有差异化，不是翻译/编译/综述
- **可写性**：3000+ 字有东西可写，不是凑字数

## 输出格式

JSON 数组，每个元素包含：
{
  "topic": "角度标题（具体，不是泛泛）",
  "angle_hint": "从XX切入，有XX独特优势",
  "type": "technical_explainer | case_study | opinion_critique",
  "differentiation": "为什么我们能写别人写不了",
  "chase_trend": true/false,
  "quality_score": 0-1,
  "gate_scores": {
    "firsthand_experience": 0-1,
    "unique_perspective": 0-1,
    "depth_analysis": 0-1,
    "practical_value": 0-1
  },
  "platforms": {
    "wechat": {
      "format": "深度技术文",
      "length": "3000+ 字",
      "angle": "具体切入角度"
    }
  }
}
```

---

## 10. 评估体系

### 10.1 测试用例

```json
{
  "skill_name": "kairos-collect-signals",
  "evals": [
    {
      "id": 1,
      "prompt": "帮我看看最近有什么值得写的AI信号",
      "expected_output": "输出 signals 和 candidate_topics",
      "assertions": [
        "signals 是非空数组",
        "candidate_topics 是非空数组",
        "每个 candidate_topic 包含 value_score, differentiation, chase_trend",
        "每个 candidate_topic 的 value_score 在 0-1 之间"
      ]
    },
    {
      "id": 2,
      "name": "Banned Patterns 过滤 - hot_news",
      "signals": [
        {
          "id": "sig-001",
          "content": "刚刚，OpenAI又发布重磅更新！",
          "type": "hot_news"
        }
      ],
      "expected_output": "该信号不应出现在 candidate_topics 中",
      "assertions": [
        "candidate_topics 长度为 0 或不包含 sig-001"
      ]
    },
    {
      "id": 3,
      "name": "Banned Patterns 过滤 - predictions",
      "signals": [
        {
          "id": "sig-002",
          "content": "2026年AI十大预测！",
          "type": "predictions"
        }
      ],
      "expected_output": "该信号不应出现在 candidate_topics 中",
      "assertions": [
        "candidate_topics 长度为 0 或不包含 sig-002"
      ]
    },
    {
      "id": 4,
      "name": "Banned Patterns 过滤 - generic_overview",
      "signals": [
        {
          "id": "sig-003",
          "content": "一文读懂AI前世今生",
          "type": "generic_overview"
        }
      ],
      "expected_output": "该信号不应出现在 candidate_topics 中",
      "assertions": [
        "candidate_topics 长度为 0 或不包含 sig-003"
      ]
    },
    {
      "id": 5,
      "name": "value_score 范围验证",
      "signals": [
        {
          "id": "sig-004",
          "content": "Valid technical content",
          "type": "technical"
        }
      ],
      "expected_output": "candidate_topics 中 value_score 应在 0-1 之间",
      "assertions": [
        "每个 candidate_topic 的 value_score >= 0",
        "每个 candidate_topic 的 value_score <= 1"
      ]
    },
    {
      "id": 6,
      "name": "空信号场景",
      "signals": [],
      "expected_output": "应返回空数组或合理的空状态响应",
      "assertions": [
        "signals 是空数组 或",
        "candidate_topics 是空数组"
      ]
    },
    {
      "id": 7,
      "name": "Source Whitelist - 聚合类内容应被拒绝",
      "signals": [
        {
          "id": "sig-007",
          "content": "程序员日报：本周 AI 十大新闻",
          "source": {"platform": "程序员日报", "url": "..."}
        }
      ],
      "expected_output": "该信号不应出现在 candidate_topics 中",
      "assertions": [
        "candidate_topics 长度为 0 或不包含 sig-007"
      ]
    },
    {
      "id": 8,
      "name": "Quality Gate - 一手经验验证",
      "signals": [
        {
          "id": "sig-008",
          "content": "我测试了 5 种 RAG 策略，发现只有 XX 有效...",
          "source": {"platform": "Personal Blog", "url": "..."}
        }
      ],
      "expected_output": "应通过质量门控，gate_scores.firsthand_experience >= 0.5",
      "assertions": [
        "candidate_topics 包含 sig-008",
        "candidate_topics[0].gate_scores.firsthand_experience >= 0.5"
      ]
    },
    {
      "id": 9,
      "name": "Quality Gate - 缺乏深度应被拒绝",
      "signals": [
        {
          "id": "sig-009",
          "content": "AI 是什么？有哪些应用？本文给你答案...",
          "source": {"platform": "技术博客", "url": "..."}
        }
      ],
      "expected_output": "该信号应被质量门控拒绝",
      "assertions": [
        "candidate_topics 长度为 0 或不包含 sig-009"
      ]
    },
    {
      "id": 10,
      "name": "高质量内容 - 实战案例应通过",
      "signals": [
        {
          "id": "sig-010",
          "content": "我们在生产环境踩坑 LangChain 的教训：内存泄漏、token 爆表、响应延迟的排查过程...",
          "source": {"platform": "Stripe Blog", "url": "..."}
        }
      ],
      "expected_output": "应通过所有质量门控",
      "assertions": [
        "candidate_topics 包含 sig-010",
        "candidate_topics[0].quality_score >= 0.6",
        "candidate_topics[0].gate_scores.firsthand_experience >= 0.7"
      ]
    }
  ]
}
```

---

## 11. Phase 规划

### Phase 1：MVP

- [ ] SKILL.md（符合规范）
- [ ] scripts/collect.py（采集脚本，支持关键词参数）
- [ ] scripts/dedup.py（去重脚本）
- [ ] scripts/cleanup.py（临时文件清理脚本）
- [ ] references/sources.json（RSS/API/HTML 源配置）
- [ ] references/keywords.json（默认关键词配置）
- [ ] references/high_quality_authors.json（高质量社交作者白名单）
- [ ] references/angle_prompt.md（Prompt 模板）
- [ ] references/banned_patterns.json（Banned Patterns 配置）
- [ ] 评估用例

### Phase 2

- [ ] 关键词配置（增强版）
- [ ] 小红书/抖音输出字段

---

## 12. 与 ai-signal 对比

| 维度 | ai-signal | kairos-collect-signals |
|------|-----------|------------------------|
| Skill 规范 | 非官方 | 遵循 agentskills.io |
| LLM 调用 | skill 内部调用 | Agent 自己执行 |
| 数据源 | 4 个固定源 | 72 个可配置源 |
| 角度生成 | 规则评分 | Agent + Prompt 模板 |
