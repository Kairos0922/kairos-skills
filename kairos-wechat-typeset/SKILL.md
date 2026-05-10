---
name: kairos-wechat-typeset
description: |
  把标准 Markdown 文章转换成适合微信公众号编辑器粘贴的多主题内联 HTML。该 Skill 是确定性的 WeChat Editorial Design System：用人工定义的视觉母版、主题哲学、节奏引擎和校验规则，稳定复现高级、精致、有品牌感的公众号排版。

  触发场景：
  - “把这篇 md 排成公众号样式”
  - “把 Markdown 转成可直接贴进微信编辑器的 HTML”
  - “给公众号文章做兼容微信编辑器的排版”
  - “把 .md 文件输出成排版好的 html 文件”
  - “用宋式美学 / MiMo / Claude 风格排版公众号文章”
metadata:
  version: "2.0"
---

# kairos-wechat-typeset

## Purpose / 目的

将标准 Markdown `.md` 文件转换为微信公众号编辑器友好的 HTML。目标不是 Markdown Renderer，也不是临场 HTML Generator，而是 WeChat Editorial Design Skill：先人工定义高级感，再让系统稳定复现。

- 人工精修的视觉母版
- 主题级视觉哲学，而不是颜色包
- 确定性的节奏、层级、间距和组件约束
- 所有样式内联，尽量避免被微信编辑器打散

## Core Principle / 核心原则

高级感来自人工定义的视觉系统，不来自 AI 即兴发挥。

- LLM：只做编辑判断，包括结构、标题层级、重点句、引用、列表、分隔节奏。
- Semantic System：输出 importance、intent、density、should_split 等语义信号。
- Art Direction Layer：根据主题哲学和文章类型解析 spacing_scale、emphasis_mode、visual_density、section_rhythm。
- Rhythm Engine：控制阅读节奏、breathing space、visual momentum。
- Layout Resolver / Renderer：把 layout decision 编译成微信兼容 inline HTML。
- Verify：同时检查 HTML 兼容性和 editorial quality。

LLM 不得直接生成 HTML、CSS、`style`、`class`、自定义标签或用户自定义主题。

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
4. 如果用户选择“是”，先生成规范化布局 Markdown：
   - LLM 只输出标准 Markdown。
   - 可使用 `## 01 标题`、`==重点==`、`> [!NOTE]`、分割线、图片、列表、表格。
   - 不新增事实，不改写用户核心观点，不生成 HTML。
   - 输出 `layout.md`，并通过 Markdown 合约验证。
5. 如果用户选择“否”，不生成 `layout.md`，直接使用当前 Markdown 进入渲染。
6. 询问用户选择哪个内置主题。主题只能来自 `themes/registry.json`，不得让用户提供 CSS、颜色、模板或主题文件。
7. 执行 semantic analysis、art direction、rhythm strategy 和 layout resolver。
8. 用脚本渲染 HTML，并运行 Markdown / HTML / editorial verify。
9. 输出版本化产物到 `~/.wechat-typeset/<article-slug>/vNNN/`。
10. 如验证或移动端预览有问题，调整 Markdown 布局、主题 token、节奏规则或渲染器，不让 LLM 临场写样式。

## Output / 输出资产

最多两个用户资产：

- 可选：`layout.md`，仅在用户选择优化布局时输出。
- 必选：`output.html`，主题化排版后的 HTML 文件。

每次运行还会输出 `meta.json`，用于记录版本、主题、输入来源、是否优化布局和产物路径。用户产物必须写入跨平台用户目录：

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

- `song`：宋式美学。适合人文评论、生活方式、长文随笔、书评。
- `mimo`：Xiaomi MiMo。适合 AI、产品发布、技术报告、研究解读、数据型文章。
- `claude`：Claude。适合教程、说明文档、方法论、技术观点、深度解释。

主题不是颜色包，而是完整视觉哲学。用户不能传自定义主题、颜色、CSS 或外部模板。开发者扩展主题时，必须新增或更新 `themes/<theme-id>.json`、`themes/<theme-id>/DESIGN.md`，并登记到 `themes/registry.json`。

## Theme Philosophy / 主题哲学

`song`：

```json
{"mood":"literary","density":"airy","rhythm":"slow","hierarchy":"soft"}
```

`mimo`：

```json
{"mood":"analytical-tech","density":"compact","rhythm":"precise","hierarchy":"strong"}
```

`claude`：

```json
{"mood":"minimal-professional","density":"balanced","rhythm":"neutral","hierarchy":"clean"}
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
- 简单表格，渲染时会降级为微信移动端更稳定的堆叠信息卡
- 围栏代码块

额外约定：

- `## 01 标题`、`## 1. 标题`、`## 02｜标题` 会渲染成主题化章节数字 + 章节标题。
- `==需要强调的句子==` 会渲染成主题强调样式。
- `> [!NOTE]`、`> [!WARNING]`、`> [!TIP]` 会渲染成语义提示块。

## Commands / 命令

推荐完整工作流：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --theme song \
  --optimize-layout yes
```

非交互式完整工作流：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --theme claude \
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
  --theme claude \
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
- 布局 Markdown 禁止 raw HTML、`style=`、`class=`、`<script>`
- 移动端 390px / 430px 无横向滚动风险
- 连续长 paragraph <= 3
- 连续 emphasis <= 2
- 高 density section 必须有 divider、quote 或 list 作为 breathing
- heading hierarchy 禁止跳级

## Golden System / 视觉母版

`goldens/` 下保存人工精修的最高视觉标准：

- `goldens/song-style.html`
- `goldens/mimo-style.html`
- `goldens/claude-style.html`

这些文件是主题气质的参照，不是运行时模板。渲染器只能执行 layout decision，不得自由设计或动态创造样式。

## Developer Theme Extension / 开发者扩展

主题扩展使用 `DESIGN.md` 思路：

- `themes/<theme-id>/DESIGN.md`：给开发者看的设计规范。
- `themes/<theme-id>.json`：给脚本读取的确定性 visual philosophy、token、rhythm、constraints。
- `themes/registry.json`：唯一对用户暴露的主题索引。

新增主题必须先使用开发者自备 Markdown 样例渲染、验证、对照 `goldens/` 的视觉标准并完成移动端预览，再加入 registry。用户运行时不能新增主题。
