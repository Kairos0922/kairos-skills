# kairos-collect-signals 重构设计文档

**日期**: 2026-04-03
**版本**: v3.0
**状态**: 设计中

---

## 变更日志

| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1.0 | 2026-04-03 | 初始设计 |
| v2.0 | 2026-04-03 | 根据 CTO/PM/工程师审阅意见更新 |
| v3.0 | 2026-04-03 | 修正 Skill 设计原则：Skill 是指令集，Agent 执行，不包含 LLM API 调用 |

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
│   └── dedup.py                 # 去重脚本（可选）
├── references/
│   ├── sources.json             # 数据源配置（72个源）
│   ├── keywords.json            # 关键词配置
│   ├── banned_patterns.json     # 禁止选题模式
│   └── angle_prompt.md          # 角度生成 Prompt 模板
└── evals/
    └── evals.json               # 测试用例
```

---

## 4. 工作流程

```
用户请求 → Agent 激活 Skill → Agent 执行：

Step 1: 采集信号
   └─ Bash: python3 scripts/collect.py --tier 1 --limit 100
   └─ 输出: /tmp/kairos-signals.json

Step 2: 读取信号
   └─ Agent: 读取 JSON 文件

Step 3: 过滤信号
   └─ Agent: 应用 Banned Patterns 和 Whitelist 规则

Step 4: 生成角度
   └─ Agent: 使用 references/angle_prompt.md 的 Prompt
   └─ Agent: 使用自己的 LLM 能力生成角度

Step 5: 输出结果
   └─ Agent: 输出 JSON 格式
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
- 输出到 `/tmp/kairos-signals.json`

**调用方式**:
```bash
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

### Step 2: 过滤信号

**执行者**: Agent（根据规则自己判断）

**规则**: 见第 6 节

**Banned Patterns**: 直接拒绝
**Translation Whitelist**: 豁免或标记

### Step 3: 生成角度

**执行者**: Agent（使用自己的 LLM 能力）

**Prompt**: `references/angle_prompt.md`

**Agent 行为**:
1. 读取 `references/angle_prompt.md`
2. 将过滤后的 signals 填充到 Prompt
3. 使用自己的 LLM 能力生成角度
4. 解析 JSON 输出

### Step 4: 输出结果

**执行者**: Agent

**格式**: 见第 7 节

---

## 6. 过滤规则

### 6.1 Banned Patterns（直接拒绝）

以下模式**直接拒绝**，不进入候选列表：

| 模式 | 类型 | 拒绝理由 |
|------|------|---------|
| "刚刚，OpenAI又发布..." | hot_news | 热点话题，泛滥内容 |
| "2026年AI十大预测！" | predictions | 无长期价值 |
| "一文读懂AI前世今生！" | generic_overview | 二道贩子特征 |
| "AI取代XXX职业！" | anxiety_marketing | 标题党 |

### 6.2 Translation Whitelist（豁免规则）

以下来源**可以豁免**进入候选列表：

| 来源 | 条件 | 状态 |
|------|------|------|
| 官方技术博客 (OpenAI/Claude/DeepMind) | 有深度技术解读 | ✅ 豁免 |
| 大佬博客 (Andrej Karpathy等) | 有独特观点或一手经验 | ✅ 豁免 |
| 资讯类翻译 | 无深度内容 | ❌ 禁止 |

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
      "value_score": 0.85,
      "differentiation": "基于实测，有独特一手经验",
      "chase_trend": false,
      "值得写吗": true,
      "拒绝理由": null,
      "platforms": {
        "wechat": {
          "format": "深度技术文",
          "length": "3000+ 字"
        }
      }
    }
  ],
  "meta": {
    "total_signals": 150,
    "signals_filtered": 130,
    "candidate_topics_count": 5,
    "collection_time": "2026-04-03T10:00:00+08:00"
  }
}
```

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

1. **采集信号**: `python3 scripts/collect.py --tier 1 --limit 100`
2. **读取信号**: 读取 `/tmp/kairos-signals.json`
3. **过滤**: 应用 Banned Patterns 和 Whitelist 规则
4. **生成角度**: 使用 `references/angle_prompt.md` 的 Prompt
5. **输出**: JSON 格式

## 过滤规则

### Banned Patterns（直接拒绝）

- ❌ hot_news: "刚刚，OpenAI又发布..."
- ❌ predictions: "2026年AI十大预测！"
- ❌ generic_overview: "一文读懂AI前世今生！"
- ❌ anxiety_marketing: "AI取代XXX职业！"

### Translation Whitelist（豁免条件）

- ✅ 官方技术博客 (OpenAI/Claude/DeepMind): 必须有深度技术解读
- ✅ 大佬博客 (Andrej Karpathy等): 必须有独特观点

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
    }
  ]
}
```

### 9.2 references/angle_prompt.md

```markdown
# 角度生成 Prompt

你是一个写作角度策划专家。根据以下信号，生成独特的写作角度。

## 信号

{SIGNALS}

## 要求

1. 每个角度必须独特，不是泛泛而谈
2. 说明差异化：为什么我们能写别人写不了的
3. 评估是否在追热点（chase_trend）
4. 只输出高价值角度（value_score > 0.5）
5. 最多生成 10 个角度

## 目标用户

微信公众号 AI 技术深度作者，3000+ 字深度技术文

## 输出格式

JSON 数组，每个元素包含：
{
  "topic": "角度标题",
  "angle_hint": "切入说明",
  "type": "technical_explainer | tool_review | opinion_commentary",
  "differentiation": "差异化说明",
  "chase_trend": true/false,
  "value_score": 0-1
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
        "每个 candidate_topic 包含 value_score, differentiation, chase_trend"
      ]
    }
  ]
}
```

---

## 11. Phase 规划

### Phase 1：MVP

- [ ] SKILL.md（符合规范）
- [ ] scripts/collect.py（采集脚本）
- [ ] references/sources.json（72源配置）
- [ ] references/angle_prompt.md（Prompt 模板）
- [ ] 评估用例

### Phase 2

- [ ] 去重脚本
- [ ] 关键词配置
- [ ] 小红书/抖音输出字段

---

## 12. 与 ai-signal 对比

| 维度 | ai-signal | kairos-collect-signals |
|------|-----------|------------------------|
| Skill 规范 | 非官方 | 遵循 agentskills.io |
| LLM 调用 | skill 内部调用 | Agent 自己执行 |
| 数据源 | 4 个固定源 | 72 个可配置源 |
| 角度生成 | 规则评分 | Agent + Prompt 模板 |
