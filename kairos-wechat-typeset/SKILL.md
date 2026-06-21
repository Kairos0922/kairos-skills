---
name: kairos-wechat-typeset
description: |
  当用户需要把 Markdown 文章排版成微信公众号可粘贴的 HTML 时加载。触发词包括："排版公众号"、"Markdown 转公众号"、"微信排版"、"公众号样式"、"排版这篇文章"、"转成微信 HTML"。不适用于 PPT、PDF、封面图或动态页面。
metadata:
  version: "1.0.0"
---

# kairos-wechat-typeset

## Purpose / 目的

将标准 Markdown `.md` 文件转换为微信公众号编辑器友好的 HTML。目标不是 Markdown Renderer，也不是临场 HTML Generator，而是 WeChat Semantic Editorial Design Skill：先定义内容的最佳语义表达，再由主题组件稳定复现高级感。

- 人工精修的视觉母版
- 主题级视觉哲学，而不是颜色包
- 确定性的语义组件、节奏、层级、间距和主题约束
- 所有样式内联，尽量避免被微信编辑器打散

## Core Principle / 核心原则

高级感来自人工定义的语义组件和视觉系统，不来自 AI 即兴发挥。语义组件不是装饰模块，而是内容在微信公众号正文中的最佳表达方式。

- LLM：只做编辑判断，包括结构、标题层级、重点句、引用、列表、步骤、分隔节奏，以及少量受控 Kairos 组件语法。
- Semantic System：输出 importance、intent、density、should_split 等语义信号。
- Semantic Component Contract：把 Markdown 和 Kairos 组件语法映射为稳定组件矩阵。
- Art Direction Layer：根据主题哲学和文章类型解析 spacing_scale、emphasis_mode、visual_density、section_rhythm。
- Rhythm Engine：控制阅读节奏、breathing space、visual momentum。
- Theme Component Renderer：把语义组件和 layout decision 编译成微信兼容 inline HTML。
- Verify：同时检查 HTML 兼容性和 editorial quality。

LLM 不得直接生成 HTML、CSS、`style`、`class`、任意自定义标签或用户自定义主题。Markdown 无法稳定表达的正文杂志组件，必须使用白名单 Kairos 组件语法，由 renderer 编译成主题组件。

## Tiered Spec Loading / 分层规范加载

按任务复杂度加载不同深度的规范，不需要每次都读完整 SKILL.md。

| Tier | 场景 | 读取 |
|------|------|------|
| **Content-only** | 只改文字，不动排版 | `CHEATSHEET.md` |
| **Layout tweak** | 调整间距/字号，在规范内 | `CHEATSHEET.md` + 主题 JSON |
| **New article** | 从零排版一篇文章 | `CHEATSHEET.md` + `references/category-routing.md` + `references/layout-recipes.md` |
| **Theme work** | 新增/修改主题 | `themes/METHODOLOGY.md` + `themes/<theme-id>/DESIGN.md` |
| **Anti-patterns review** | 审查输出质量 | `references/anti-patterns.md` |

## Reference Files / 参考文件

| 文件 | 用途 | 何时读 |
|------|------|--------|
| `CHEATSHEET.md` | 一页速查 | 每次操作 |
| `COMPONENTS.md` | 语义组件契约 | 使用 Kairos 组件时 |
| `PRODUCT.md` | 设计决策和产品边界 | 理解"为什么"时 |
| `references/anti-patterns.md` | 反模式 + Bad/Fix 对照 | 审查输出时 |
| `references/category-routing.md` | 文章类型 → 推荐策略 | 选主题和组件时 |
| `references/layout-recipes.md` | 编号版式骨架 | 规划文章结构时 |
| `themes/METHODOLOGY.md` | 主题扩展方法论 | 新增主题时 |
| `themes/registry.json` | 主题索引 | 选主题时 |

## System Architecture / 系统架构

```text
Markdown path / Markdown text / non-Markdown text
        ↓
Input normalization
        ↓
Ask: optimize layout?
        ↓ yes                           ↓ no
Layout Markdown contract          Current Markdown
        ↓                              ↓
Optional layout.md                    ↓
        ↓                              ↓
Ask: choose built-in theme from registry
        ↓
Semantic Analysis
        ↓
Semantic Component Contract
        ↓
Art Direction
        ↓
Rhythm Engine
        ↓
Layout Resolver
        ↓
Deterministic Renderer
        ↓
WeChat Verify + Editorial Verify
        ↓
Versioned output under ~/.wechat-typeset
```

## User Workflow / 用户流程

1. 用户提供 Markdown 文件路径、Markdown 内容，或非 Markdown 内容。
2. 系统将输入归一化为 Markdown。非 Markdown 内容只做最小 Markdown 标准化，不新增事实。
3. 询问用户是否需要优化布局。
4. 如果用户选择“是”，由 agent/LLM 先生成规范化布局 Markdown：
   - LLM 只输出 Markdown 与白名单 Kairos 组件语法。
   - 可使用 `## 01 标题`、`==重点==`、`> [!NOTE]`、分割线、图片、列表、步骤、表格，以及 `:::lead`、`:::insight`、`:::pullquote`、`:::figure`、`:::soft-list`、`:::closing-note`。
   - 不新增事实，不改写用户核心观点，不生成 HTML。
   - 输出 `layout.md`，并通过 Markdown 合约验证。
   - 脚本的 `--optimize-layout yes` 只负责保存和验证 `layout.md`；没有外部布局稿时只做 deterministic normalization fallback，不能替代人工/LLM 编辑判断。
5. 如果用户选择“否”，不生成 `layout.md`，直接使用当前 Markdown 进入渲染，只执行安全验证。
6. 询问用户选择哪个内置主题。主题只能来自 `themes/registry.json`，不得让用户提供 CSS、颜色、模板或主题文件。
7. 执行 semantic analysis、art direction、rhythm strategy 和 layout resolver。
8. 如用户要求配图，由 host agent 根据文章、主题和 `image_direction` 规则生成 `image-plan.json`：
   - `kairos-wechat-typeset` 不配置生图模型、不保存 API key、不绑定 provider。
   - 如果宿主 agent 有生图能力，agent 调用自己的生图工具并把图片写入输出目录。
   - 如果宿主 agent 没有生图能力，agent 输出 `image-prompts.md`。
   - 图片计划必须通过 `scripts/verify_image_plan.py`，再转换为 `:::figure`。
9. 用脚本渲染 HTML，并运行 Markdown / HTML / editorial verify。
10. 输出版本化产物到 `~/.wechat-typeset/<article-slug>/vNNN/`。
11. 如验证或移动端预览有问题，调整 Markdown 布局、主题 token、节奏规则或渲染器，不让 LLM 临场写样式。

## Output / 输出资产

最多两个用户资产：

- 可选：`layout.md`，仅在用户选择优化布局时输出。
- 必选：`output.html`，主题化排版后的 HTML 文件。
- 可选：`image-plan.json`，仅在用户要求配图时输出，由 agent 编写并由脚本验证。
- 可选：`image-prompts.md`，宿主 agent 无生图能力时输出。
- 可选：`images/`，宿主 agent 生成或用户提供的正文配图资产。

每次运行还会输出 `meta.json`，用于记录版本、主题、输入来源、是否优化布局、layout mode、内容 hash 和产物路径。用户产物必须写入跨平台用户目录：

```text
~/.wechat-typeset/
  article-slug/
    v001/
      layout.md
      image-plan.json
      image-prompts.md
      images/
      output.html
      meta.json
    v002/
      output.html
      meta.json
```

实现时使用 `Path.home() / ".wechat-typeset"`，不得把用户输出写入 skill 目录。

## Built-in Themes / 内置主题

运行以下命令查看主题：

```bash
python3 scripts/render.py --list-themes
```

v2 内置：

- `song`：宋式美学主题。适用文章类型：技术长文、方法论、人文评论、生活方式、书评。
- `wending`：稳境白纸主题。适用文章类型：个人成长、心理秩序、生活方式、轻方法论、慢阅读文章。
- `tech`：科技主题。适用文章类型：AI 技术文章、工程实践、产品方案、研发实践、工具教程。
- `wisme`：WISME 规范主题。适用文章类型：知识科普、研究报告、组件规范、方法论、专业说明。
- `pi`：Pi 开发者主题。适用文章类型：开发者文档、技术教程、API 参考、工具指南、编程实战、开源项目介绍。

主题不是颜色包，而是完整视觉哲学。用户不能传自定义主题、颜色、CSS 或外部模板。开发者扩展主题时，必须先遵守 `themes/METHODOLOGY.md`，再新增或更新 `themes/<theme-id>.json`、`themes/<theme-id>/DESIGN.md`，并登记到 `themes/registry.json`。

## Theme Philosophy / 主题哲学

`song`：

```json
{"mood":"literary","density":"balanced","rhythm":"mobile","hierarchy":"soft"}
```

`pi`：

```json
{"mood":"technical","density":"airy","rhythm":"mobile","hierarchy":"explicit"}
```

所有主题必须遵守：

- Accent Color = 1
- Highlight Frequency <= 8%
- Component Variants <= 3
- Heading Styles 固定
- Divider Styles 固定

## Input / 输入

标准 Markdown 文件路径，例如：

```text
article.md
```

支持：

- `# / ## / ###` 标题
- 普通段落
- 无序列表 / 有序列表
- 引用块 `>`
- 分割线 `---` / `***` / `<!--段落分割线-->`
- 粗体、斜体、删除线、行内代码、链接、图片
- 简单表格，渲染为微信移动端安全的 faux table 或主题化信息卡
- 围栏代码块

额外约定：

- `## 01 标题`、`## 1. 标题`、`## 02｜标题` 会渲染成主题化章节数字 + 章节标题。
- `==需要强调的句子==` 会渲染成主题强调样式。
- `> [!NOTE]`、`> [!WARNING]`、`> [!TIP]` 会渲染成语义提示块。

## Kairos Components / 受控正文组件

普通 Markdown 负责技术文章基础元素：标题、正文、表格、代码块、行内代码、加粗、斜体、删除线、划线、列表、步骤、Quote、Insight、Divider 和图片。Kairos 组件负责 Markdown 难以稳定表达的公众号正文杂志感。组件只表达语义，不允许 HTML、CSS、`style`、`class` 或任意自定义标签。完整契约见 `COMPONENTS.md`。

```markdown
:::lead
导语段，用于正文开头建立文章气息。
:::

:::insight
真正稳定的不是样式，而是样式背后的语义契约。
:::

:::pullquote
计白当黑，数虚当实。
:::

:::figure
![图片替代文字](https://example.com/image.png)
图注文字。
:::

:::soft-list
- 第一条
- 第二条
:::

:::closing-note
安静的结尾收束语。
:::
```

## Image Direction / 文章配图

配图是 agent-mediated workflow，不是 renderer 的自由设计，也不是脚本内置模型调用。Skill 只定义配图标准、主题方向、`image-plan.json` 契约和验证门槛；宿主 agent 负责判断是否生成图片、调用自己的生图能力，或在没有生图能力时输出 prompt。

配图必须符合以下原则：

- 图片必须降低理解成本、提供证据、解释结构或建立必要的开场气质。
- 默认允许 `0` 张图；不需要图片的文章应说明原因，而不是硬插图。
- 默认比例为 `16:9`。
- 每张图必须有 `purpose`、`why_needed`、`theme_fit`、`alt`、`caption`、`prompt` 和 `avoid`。
- 低必要性图片不进入计划；`necessity` 只能是 `high` 或 `medium`。
- `evidence_figure` 必须有 `source_note`，生成图片不得伪造截图、数据、图表、品牌、引用或事实证据。
- prompt 必须禁止图片内生成可读文字，除非用户提供的证据图片本身包含文字。

允许的图像角色：

- `concept_diagram`：概念、框架、心智模型和抽象关系。
- `process_diagram`：流程、链路、管线和实现步骤。
- `comparison_diagram`：取舍、前后对比、能力矩阵和差异说明。
- `evidence_figure`：有来源的截图、研究图、产品状态或数据视觉。
- `atmosphere_still`：极少量开场定调图，主要适合文学、生活方式和慢阅读文章。

平台边界：微信公众号只能控制正文，不能把文章标题、封面图、账号信息、菜单、外部页面背景当作主题表面。`song` 不使用印章、自由定位或封面式大标题组件。

## Commands / 命令

推荐完整工作流：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --theme song \
  --optimize-layout yes
```

如果 agent 已经生成优化后的 Markdown，可显式传入：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --layout-input layout.md \
  --theme song \
  --optimize-layout yes
```

非交互式完整工作流：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --theme song \
  --optimize-layout no \
  --non-interactive
```

底层渲染器：

```bash
python3 scripts/render.py \
  --theme song \
  --input article.md \
  --output article.html \
  --verify
```

仅输出可粘贴正文片段：

```bash
python3 scripts/render.py \
  --theme song \
  --input article.md \
  --output article.fragment.html \
  --fragment-only \
  --verify
```

加载 Web 字体（本地预览用）：

```bash
python3 scripts/render.py \
  --theme song \
  --input article.md \
  --output article.html \
  --web-fonts \
  --verify
```

`--web-fonts` 会在 `<head>` 中注入 `@font-face` 声明，加载思源宋体（衬线主题）或霞鹜新晰黑（无衬线主题）等免费商用字体。**此功能仅用于本地浏览器预览和 PDF 导出；粘贴到微信公众号编辑器时 `<style>` 会被剥离，Web 字体不会加载。**

单独验证已有 HTML：

```bash
python3 scripts/verify.py \
  --input article.html
```

单独验证布局 Markdown：

```bash
python3 scripts/verify_markdown.py \
  --input layout.md
```

单独验证配图计划：

```bash
python3 scripts/verify_image_plan.py \
  --input image-plan.json \
  --theme tech
```

## Feedback Protocol / 反馈处理

当用户给出模糊反馈时，先报告当前值，再提供具体选项。不要猜测用户想要什么，把模糊反馈转化为精确对话。

| 用户说 | 先报告 | 选项 |
|--------|--------|------|
| "太挤了" | 当前 spacing_scale | (a) compressed (b) balanced (c) relaxed |
| "不够高级" | 当前 emphasis_mode | (a) minimal (b) moderate (c) editorial |
| "颜色不对" | 当前主题 ID | (a) song (b) wending (c) tech (d) wisme |
| "标题太大了" | 当前 H1 字号 | 降低到下一级 |
| "段落太长" | 当前段落长度 | 拆分为多段 |
| "代码块不好看" | 当前主题的代码块样式 | 检查主题 JSON 中的 code_token |

模板回复："当前值是 X。你想改成 (a) 还是 (b)？"。不要说"我调一下间距"而不说明具体改了什么。

## Quality Gates / 验收规则

生成后必须检查：

- 无 `<style>`
- 无 `class=`
- 无外部 CSS
- 无 `<script>`
- 无原生 `<table>`、`<ul>`、`<ol>`
- 图片必须 `max-width: 100%`
- 配图计划必须通过 `scripts/verify_image_plan.py`
- 配图默认 16:9，低必要性图片不得进入计划
- 生成图不得伪造截图、数据、图表、品牌、引用或事实证据
- 原始 HTML 必须被转义，不能透传
- 所有输入都必须通过 Markdown safety verify：禁止 raw HTML、`style=`、`class=`、`<script>`
- `layout.md` 还必须通过 layout contract verify：heading 不跳级、重点不过量、段落不过长
- 移动端 390px / 430px 无横向滚动风险
- 连续长 paragraph <= 3
- 连续 emphasis <= 2
- 高 density section 必须有 divider、quote 或 list 作为 breathing
- heading hierarchy 禁止跳级

## Local Assets / 本地资产

所有字体已本地化到 `assets/fonts/` 目录，渲染管线无需外部网络连接。

| 字体 | 用途 | 位置 |
|------|------|------|
| Noto Sans SC | 中文显示/正文（tech/wisme 主题） | `assets/fonts/sans-serif/noto-sans-sc/` |
| Noto Serif SC | 中文衬线（song/wending 主题） | `assets/fonts/serif/noto-serif-sc/` |
| Inter | 拉丁文显示/正文 | `assets/fonts/sans-serif/inter/` |
| Playfair Display | 衬线拉丁（song/wending 主题） | `assets/fonts/serif/playfair-display/` |

字体注册表：`assets/fonts/fonts.json`
字体 CSS 生成：`scripts/build_font_css.py`

渲染管线优先使用本地字体（`assets/fonts/fonts.css`），无需 `--web-fonts` 标志即可获得一致的字体渲染。

验证资产完整性：
```bash
python3 scripts/verify_fonts.py      # 验证字体文件存在
python3 scripts/verify_assets.py     # 验证无外部 CDN 依赖
```

## Golden System / 视觉母版

`goldens/` 下保存人工精修的最高视觉标准：

- `goldens/song-style.html`
- `goldens/wending-style.html`
- `goldens/tech-style.html`
- `goldens/wisme-style.html`

这些文件是主题气质的参照，不是运行时模板。渲染器只能执行 layout decision，不得自由设计或动态创造样式。

`fixtures/song-style-system.md` 是 `song` 的设计规范与文章样例来源。`fixtures/wending-style-system.md` 是 `wending` 的移动端白纸主题组件体系与文章样例来源。`fixtures/tech-style-system.md` 是 `tech` 的科技主题组件体系来源。`fixtures/wisme-style-system.md` 是 `wisme` 的黑白灰规范组件体系来源。`fixtures/universal-showcase.md` 是全部 4 个主题共享的通用展示文章，覆盖标题、正文、加粗、斜体、删除线、高亮、链接、内联代码、有序/无序/任务列表、代码块、表格、引用、提示块（NOTE/TIP/WARNING）、图片、分隔线、引言（pullquote）、洞察（insight）、软列表（soft-list）、结尾注（closing-note）等全部组件，用于生成对比效果图。新增或重打磨主题时，使用对应真实文章 fixture 覆盖标题、段落、引用、代码、表格、分割符、图片、链接和安全转义，再把通过人工审核的结果提升为 golden。

## Developer Theme Extension / 开发者扩展

主题扩展必须先读 `themes/METHODOLOGY.md`。扩展主题不是写 CSS，而是把视觉母版转译为确定性的语义组件、设计 token、renderer 规则、fixture、golden 和验证门槛。

主题扩展使用以下资产：

- `themes/METHODOLOGY.md`：从 Song 定稿沉淀出的主题扩展方法论。
- `themes/<theme-id>/DESIGN.md`：给开发者看的设计规范。
- `themes/<theme-id>.json`：给脚本读取的确定性 visual philosophy、token、rhythm、constraints。
- `themes/registry.json`：唯一对用户暴露的主题索引。
- `fixtures/song-style-system.md`：`song` 设计规范与文章样例 golden 来源。
- `fixtures/wending-style-system.md`：`wending` 白纸主题组件体系与文章样例 golden 来源。
- `fixtures/tech-style-system.md`：`tech` 科技主题组件体系与文章样例 golden 来源。
- `fixtures/wisme-style-system.md`：`wisme` 规范主题组件体系与文章样例 golden 来源。
- `fixtures/universal-showcase.md`：全部 4 个主题共享的通用展示文章，覆盖全部组件类型，用于生成对比效果图。
- `scripts/audit_visual.py`：渲染后视觉库存审计，用于发现字号漂移、间距过大、边框过密和背景色过多。

新增主题必须先完成设计确认，再使用对应真实文章 fixture 渲染、验证、对照 `goldens/` 的视觉标准并完成 390px / 430px 移动端预览。对齐敏感组件必须量测表格、列表 marker 和任务清单 checkbox 的视觉中心。用户运行时不能新增主题。
