# kairos-wechat-typeset

`kairos-wechat-typeset` 把标准 Markdown 文章转换成微信公众号编辑器友好的多主题 HTML。它不是普通 Markdown Renderer，而是确定性的 WeChat Editorial Design Skill：先用人工视觉母版定义高级感，再用主题哲学、节奏引擎和校验规则稳定复现。

## 60 秒上手

查看内置主题：

```bash
python3 scripts/render.py --list-themes
```

推荐完整工作流。系统会创建版本化输出目录，并根据参数决定是否输出 `layout.md`：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --theme song \
  --optimize-layout yes
```

如果 agent 已经生成优化后的布局 Markdown：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --layout-input layout.md \
  --theme song \
  --optimize-layout yes
```

不优化布局，直接使用当前 Markdown 渲染：

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

只生成微信公众号 HTML 模式可粘贴片段：

```bash
python3 scripts/render.py \
  --theme song \
  --input article.md \
  --output article.fragment.html \
  --fragment-only \
  --verify
```

## 内置主题

- `song`：宋式美学。技术长文、方法论、人文评论、生活方式、书评。

主题只能从 registry 中选择。用户不能传自定义 CSS、颜色、HTML 模板或运行时主题文件。

完整工作流会让用户选择内置主题，非交互模式必须显式传入 `--theme`。

## 输出目录与版本

用户产物不写入 skill 目录。默认输出到跨平台用户目录：

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

- `layout.md`：可选，仅在用户选择优化布局时生成。
- `output.html`：必选，排版后的 HTML。
- `meta.json`：必选，记录版本、主题、输入来源、是否优化布局、layout mode、内容 hash 和产物路径。

## 架构

```text
kairos-wechat-typeset/
├── DESIGN.md
├── SKILL.md
├── goldens/
│   └── song-style.html
├── themes/
│   ├── registry.json
│   ├── song.json
│   └── song/DESIGN.md
├── semantic/
│   └── analyze.py
├── art_direction/
│   ├── mood.py
│   ├── rhythm.py
│   ├── hierarchy.py
│   └── spacing.py
├── renderer/
│   ├── blocks.py
│   ├── variants.py
│   └── compiler.py
├── verify/
│   ├── html_verify.py
│   ├── markdown_verify.py
│   └── editorial_verify.py
└── scripts/
    ├── typeset.py
    ├── render.py
    ├── verify_markdown.py
    └── verify.py
```

`COMPONENTS.md` 是语义组件契约，`themes/<theme-id>.json` 是确定性视觉契约，`themes/<theme-id>/DESIGN.md` 是人工设计说明，`goldens/` 是最高视觉参照。

## Fixtures

`fixtures/` 中的文章既是可读样文，也是组件覆盖样例。维护 fixture 时应覆盖微信公众号文章里的中高频正文元素：

- 文章标题、作者/来源/日期信息、导语和正文段落。
- H1、数字 H2、H3、普通引用、`NOTE` / `TIP` / `WARNING` 提示块。
- 加粗、斜体、删除线、`==重点==`、行内代码、链接和拉丁文本。
- 普通图片、`:::figure` 图文组件、图注、分隔线和结尾收束。
- 有序列表、无序列表、任务清单、`:::soft-list`、表格、代码块、FAQ 和延伸阅读。

新增或大改 fixture 后，至少运行对应 Markdown 合约验证和主题渲染验证。

## V3 Pipeline

```text
Markdown path / Markdown text / non-Markdown text
  -> Input normalization
  -> Ask whether to optimize layout
  -> Optional layout Markdown
  -> Ask user to choose a built-in theme
  -> Semantic Analysis
  -> Semantic Component Contract
  -> Art Direction
  -> Rhythm Engine
  -> Theme Component Renderer
  -> WeChat Verify + Editorial Verify
  -> Versioned output under ~/.wechat-typeset
```

## LLM 与脚本分工

- LLM 只优化 Markdown 与白名单 Kairos 组件语法：标题层级、段落节奏、重点句、引用、列表、步骤、分隔线、导语、洞察、摘引、图文、收束。
- LLM 不生成 HTML、不写 CSS、不新增任意自定义标签，不决定 typography、spacing、layout。
- 脚本负责确定性执行：输入归一化、保存/验证 `layout.md`、解析 Markdown、加载主题、分析语义、解析节奏、输出全内联 HTML、执行验证。
- 语义组件不是装饰模块，而是内容在微信公众号正文中的最佳表达方式。

如果用户不选择优化布局，脚本不输出 `layout.md`，直接使用当前 Markdown 渲染，并只做 safety verify。如果输入不是 Markdown，脚本会先做最小 Markdown 标准化。

## 支持的 Markdown

- 标题、段落、列表、引用、分割线
- 粗体、斜体、删除线、行内代码、链接、图片
- 围栏代码块
- 简单表格，渲染为微信移动端安全的 faux table 或主题化信息卡
- `==重点句==`
- `> [!NOTE]` / `> [!TIP]` / `> [!WARNING]`
- `## 01 标题` 数字章节标题

## 语义组件

普通 Markdown 承载技术文章的基础元素：标题、正文、表格、代码块、行内代码、加粗、斜体、删除线、划线、列表、步骤、Quote、Insight、Divider 和图片。Kairos 语义组件承载 Markdown 难以稳定表达的公众号正文杂志感。组件仍然是 Markdown 输入，不允许写 HTML、CSS、`style` 或 `class`。

语义组件用于回答“这段内容最适合如何被读者接收”，而不是“这里要加什么装饰”。完整契约见 [`COMPONENTS.md`](COMPONENTS.md)。

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

微信公众号正文不能控制平台标题、封面图、账号信息、菜单和外部页面背景。`song` 的正文组件只追求单列阅读里的宋式杂志气质，不做印章、自由定位或封面式大标题。

## 质量目标

- 稳定输出：白名单语义组件、全内联样式、无任意 HTML/CSS。
- 快速扩主题：每个主题实现同一套组件矩阵，而不是为每篇文章临场补样式。
- 高级感：靠语义选择、留白、阅读节奏、克制强调和图文关系建立，不靠堆装饰。
- 移动端适配：表格使用微信移动端安全的 faux layout，代码块不依赖横向滚动，图片始终移动端安全。

## 验证

渲染时加 `--verify`，或单独运行：

```bash
python3 scripts/verify.py \
  --input article.html
```

验证项包括：无 `<style>`、无 `class=`、无外部 CSS、无脚本、无原生宽表格、图片移动端安全，以及 heading 不跳级、连续长段不超过 3、连续强强调不超过 2、高密度区块必须有 breathing。

完整工作流 `scripts/typeset.py` 会在渲染后自动执行 HTML 和 editorial verify。

验证布局 Markdown：

```bash
python3 scripts/verify_markdown.py \
  --input layout.md
```

审计渲染后的视觉库存：

```bash
python3 scripts/audit_visual.py \
  --input goldens/song-style.html \
  --allowed-font-size 12px \
  --allowed-font-size 14px \
  --allowed-font-size 16px \
  --allowed-font-size 25px \
  --allowed-font-size 28px \
  --max-margin-px 48
```

## 开发者新增主题

见 [`themes/METHODOLOGY.md`](themes/METHODOLOGY.md) 与 [`themes/README.md`](themes/README.md)。新增主题需要：

1. 先写主题 thesis、适用文章类型、禁用视觉手法和组件规则。
2. 新建 `themes/<theme-id>/DESIGN.md`。
3. 新建 `themes/<theme-id>.json`。
4. 注册到 `themes/registry.json`。
5. 使用对应的真实文章 fixture 渲染 `goldens/<theme-id>-style.html`，例如 `song` 使用 `fixtures/song-style-system.md`。
6. 通过真实文章样例检查标题、段落、引用、代码、表格、分割符、图片、链接和安全转义。
7. 通过 `--verify`、`scripts/audit_visual.py`、检查 `goldens/` 对齐度，并进行 390px / 430px 移动端预览。
