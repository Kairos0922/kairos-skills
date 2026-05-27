---
name: kairos-wechat-typeset
description: |
  把标准 Markdown 文章转换成适合微信公众号编辑器粘贴的多主题内联 HTML。该 Skill 是确定性的 WeChat Semantic Editorial Design System：用语义组件、人工定义的视觉母版、主题哲学、节奏引擎和校验规则，稳定复现高级、精致、有品牌感的公众号排版。

  触发场景：
  - “把这篇 md 排成公众号样式”
  - “把 Markdown 转成可直接贴进微信编辑器的 HTML”
  - “给公众号文章做兼容微信编辑器的排版”
  - “把 .md 文件输出成排版好的 html 文件”
  - “用宋式美学排版公众号文章”
metadata:
  version: "2.0"
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
8. 用脚本渲染 HTML，并运行 Markdown / HTML / editorial verify。
9. 输出版本化产物到 `~/.wechat-typeset/<article-slug>/vNNN/`。
10. 如验证或移动端预览有问题，调整 Markdown 布局、主题 token、节奏规则或渲染器，不让 LLM 临场写样式。

## Output / 输出资产

最多两个用户资产：

- 可选：`layout.md`，仅在用户选择优化布局时输出。
- 必选：`output.html`，主题化排版后的 HTML 文件。

每次运行还会输出 `meta.json`，用于记录版本、主题、输入来源、是否优化布局、layout mode、内容 hash 和产物路径。用户产物必须写入跨平台用户目录：

```text
~/.wechat-typeset/
  article-slug/
    v001/
      layout.md
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

- `song`：宋式美学。适合技术长文、方法论、人文评论、生活方式、书评。
- `wending`：稳境白纸。适合个人成长、心理秩序、生活方式、轻方法论、公众号规范。
- `techspec`：蓝图科技规范。适合 AI 技术文章、工程实践、产品方案、研发规范、工具教程。

主题不是颜色包，而是完整视觉哲学。用户不能传自定义主题、颜色、CSS 或外部模板。开发者扩展主题时，必须先遵守 `themes/METHODOLOGY.md`，再新增或更新 `themes/<theme-id>.json`、`themes/<theme-id>/DESIGN.md`，并登记到 `themes/registry.json`。

## Theme Philosophy / 主题哲学

`song`：

```json
{"mood":"literary","density":"balanced","rhythm":"mobile","hierarchy":"soft"}
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

## Quality Gates / 验收规则

生成后必须检查：

- 无 `<style>`
- 无 `class=`
- 无外部 CSS
- 无 `<script>`
- 无原生 `<table>`、`<ul>`、`<ol>`
- 图片必须 `max-width: 100%`
- 原始 HTML 必须被转义，不能透传
- 所有输入都必须通过 Markdown safety verify：禁止 raw HTML、`style=`、`class=`、`<script>`
- `layout.md` 还必须通过 layout contract verify：heading 不跳级、重点不过量、段落不过长
- 移动端 390px / 430px 无横向滚动风险
- 连续长 paragraph <= 3
- 连续 emphasis <= 2
- 高 density section 必须有 divider、quote 或 list 作为 breathing
- heading hierarchy 禁止跳级

## Golden System / 视觉母版

`goldens/` 下保存人工精修的最高视觉标准：

- `goldens/song-style.html`
- `goldens/wending-style.html`

这些文件是主题气质的参照，不是运行时模板。渲染器只能执行 layout decision，不得自由设计或动态创造样式。

`fixtures/song-style-system.md` 是 `song` 的设计规范与文章样例来源。`fixtures/wending-style-system.md` 是 `wending` 的附件移动端组件规范与文章样例来源。新增或重打磨主题时，使用对应真实文章 fixture 覆盖标题、段落、引用、代码、表格、分割符、图片、链接和安全转义，再把通过人工审核的结果提升为 golden。

## Developer Theme Extension / 开发者扩展

主题扩展必须先读 `themes/METHODOLOGY.md`。扩展主题不是写 CSS，而是把视觉母版转译为确定性的语义组件、设计 token、renderer 规则、fixture、golden 和验证门槛。

主题扩展使用以下资产：

- `themes/METHODOLOGY.md`：从 Song 定稿沉淀出的主题扩展方法论。
- `themes/<theme-id>/DESIGN.md`：给开发者看的设计规范。
- `themes/<theme-id>.json`：给脚本读取的确定性 visual philosophy、token、rhythm、constraints。
- `themes/registry.json`：唯一对用户暴露的主题索引。
- `fixtures/song-style-system.md`：`song` 设计规范与文章样例 golden 来源。
- `fixtures/wending-style-system.md`：`wending` 附件移动端组件规范与文章样例 golden 来源。
- `scripts/audit_visual.py`：渲染后视觉库存审计，用于发现字号漂移、间距过大、边框过密和背景色过多。

新增主题必须先完成设计确认，再使用对应真实文章 fixture 渲染、验证、对照 `goldens/` 的视觉标准并完成 390px / 430px 移动端预览。对齐敏感组件必须量测表格、列表 marker 和任务清单 checkbox 的视觉中心。用户运行时不能新增主题。
