---
name: kairos-visual-generator
description: |
  当用户需要生成视觉卡片、封面、信息图或海报时加载。触发词包括：
  "做一张封面"、"生成信息图"、"视觉卡片"、"海报"、"小红书封面"、
  "PPT 封面"、"蒙德里安"、"咨询风"、"杂志风"。
  不适用于微信正文排版、PPT 演示文稿或纯图片编辑。
metadata:
  version: "2.0.0"
---

# kairos-visual-generator

## Purpose

把用户给出的主题转化为一张高质量视觉卡片或海报。支持三套独立视觉系统（Editorial Magazine / Swiss Consulting / Mondrian），风格即插件，确定性渲染管线。

- 质量第一：质量 > 稳定 > 效率
- 三套视觉系统，每套有独立设计规则
- 确定性渲染：AI 生成 Visual Brief，代码消费 Brief 输出 PNG
- 最小输入：用户只需提供主题和用途，系统自动推断其余字段

## Core Principle

**确定性的 AI 内容生产工作流。AI 只做编辑判断，视觉系统由代码和契约决定。**

质量第一原则：质量 > 稳定 > 效率。当三者冲突时，质量优先。宁可多追问一个问题，也不猜测导致风格错误。

- LLM：只做编辑判断，包括风格选择、主题拆分、隐喻选择、文字重构决策。
- Intake Engine：确定性解析自然语言，自动推断语言、画幅、用途。
- Style Router：两层路由（显式指定 > 语义推断），低置信度时追问。
- Visual Brief：AI 输出的唯一接口，JSON Schema 强制验证。
- Render Pipeline：确定性代码实现，token → CSS 变量映射，HTML/CSS → PNG。
- QA：两层检查（全局 + 风格专项），不通过拒绝输出。

LLM 不得直接生成 HTML、CSS、`style`、`class` 或任意自定义标签。LLM 的输出是 Visual Brief，不是渲染产物。

## Tiered Spec Loading

按任务复杂度加载不同深度的规范：

| Tier | 场景 | 读取 |
|------|------|------|
| **Quick check** | 检查输入是否足够 | `CHEATSHEET.md` + `scripts/select_style.py` |
| **Standard card** | 生成一张封面或轻信息卡 | `CHEATSHEET.md` + 对应风格的 `DESIGN.md` |
| **Full infographic** | 生成深度信息图/矩阵图 | 对应风格的 `DESIGN.md` + `composition.json` |
| **New style** | 新增一套视觉系统 | `styles/METHODOLOGY.md` |

## Reference Files

| 文件 | 用途 | 何时读 |
|------|------|--------|
| `CHEATSHEET.md` | 一页速查 | 每次操作 |
| `PRODUCT.md` | 设计决策和产品边界 | 理解"为什么"时 |
| `styles/registry.json` | 风格注册表 | 选风格时 |
| `styles/METHODOLOGY.md` | 风格扩展方法论 | 新增风格时 |
| `styles/<style-id>/DESIGN.md` | 风格定义 | 生成该风格时 |
| `styles/<style-id>/composition.json` | 构图规则 | 生成该风格时 |
| `references/anti-patterns.md` | 全局反模式 | 审查输出时 |

## System Architecture

```text
用户自然语言输入
        ↓
Intake Engine (shared/intake.py)
  ├─ 解析自然语言 → 主题 + 用途
  ├─ 语言自动检测
  ├─ 用途 → 画幅映射 (shared/platform.py)
  └─ 风格路由 (shared/router.py)
        ↓
    需要追问？
    ├─ 是 → 追问用户（质量优先）
    └─ 否 ↓
        ↓
Visual Brief 生成 (AI)
  ├─ A 层：核心视觉词
  ├─ B 层：完整标题
  ├─ C 层：标签
  ├─ 隐喻选择
  ├─ 版式骨架选择
  └─ 文字重构决策
        ↓
Brief 验证 (shared/brief.py)
  ├─ JSON Schema 检查
  └─ 必填字段验证
        ↓
Render Pipeline (shared/render.py)
  ├─ 加载 composition.json
  ├─ 加载主题 token (css_mapping)
  ├─ 生成 HTML/CSS
  └─ 输出 PNG
        ↓
QA Verification (shared/verify.py)
  ├─ 全局检查
  └─ 风格专项检查
        ↓
版本化输出 ~/.visual-generator/<slug>/vNNN/
```

## User Workflow

1. 用户提供一句话输入（如"帮我做一张小红书封面，主题是用户增长飞轮"）。
2. Intake Engine 解析输入，提取主题和用途信号。
3. 系统自动检测语言、映射画幅比例、路由到最佳风格。
4. 如果风格不确定（置信度 < 50%），追问用户选择风格。
5. 如果用途不明确，追问用户确认。
6. AI 生成 Visual Brief（A/B/C 层文字、隐喻、版式、重构方法）。
7. Brief 通过 JSON Schema 验证。
8. Render Pipeline 消费 Brief，生成 HTML/CSS → PNG。
9. QA 两层检查（全局 + 风格专项）。
10. 输出到版本化目录 `~/.visual-generator/<slug>/vNNN/`。

## Input Contract

用户只需提供：

- `主题`：必需。一句话自然语言输入。
- `用途/平台`：可从输入中推断（如"小红书封面"→ 用途=小红书封面, 画幅=3:4）。

系统自动推断：

| 字段 | 推断逻辑 | 默认值 |
|------|----------|--------|
| 语言 | 字符检测：中文/英文/混排 | 跟随标题 |
| 画幅比例 | 用途 → 画幅映射 | 4:5 |
| 风格 | 内容语义路由 | 系统最佳判断 |

## Intake Gate

**质量不确定时必须追问**，风格错误 = 质量归零。

**必须追问**：
- 用途不明确 → "你想做什么？封面 / 信息图 / 海报？"
- 风格不确定 → "你想要什么风格？商业分析风 / 杂志编辑风 / 现代艺术风？"
- 主题过于模糊 → 追问方向

**绝不追问**：
- 语言自动检测
- 画幅比例平台映射
- 用途别名归一化

## Style Routing

两层路由，优先级从高到低：

**第一层：用户显式指定**

| 用户说 | 路由到 |
|--------|--------|
| "蒙德里安风格"、"De Stijl"、"Bauhaus 风" | `mondrian` |
| "麦肯锡风格"、"咨询风"、"Swiss 风" | `swiss` |
| "杂志风"、"编辑风"、"墨水风" | `editorial` |

**第二层：内容语义推断**

| 内容关键词 | 路由到 |
|------------|--------|
| 增长、转化、漏斗、策略、方法论、框架、指标、运营、商业 | Swiss Consulting |
| 文化、机构、叙事、评论、人文、反思、深度、观点 | Editorial Magazine |
| 设计、艺术、建筑、构成、创意、视觉、品牌、美学 | Mondrian |

## Visual Systems

只在三套视觉系统中选择，不要临场发明风格：

- `Editorial Magazine`：杂志感、叙事、观点、人物/组织/文化主题。
- `Swiss Consulting`：分析、框架、方法论、产品、技术组织主题。
- `Mondrian / De Stijl`：设计、艺术、建筑、构成、创意主题。

每套风格有独立的 DESIGN.md、composition.json 和主题 token。

## Output

输出到版本化目录：

```text
~/.visual-generator/
  <topic-slug>/
    v001/
      output.png           # 最终视觉卡片
      brief.json           # Visual Brief（可追溯）
      meta.json            # 版本元数据
```

## Deterministic Boundary

AI 生成 Visual Brief，代码消费 Brief 输出 PNG。

- Brief 有 JSON Schema 强制验证，不通过拒绝渲染。
- 渲染管线是纯确定性的，AI 不参与。
- QA 两层检查：全局通用 + 风格专项。
