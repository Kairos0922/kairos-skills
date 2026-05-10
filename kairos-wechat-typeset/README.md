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

不优化布局，直接使用当前 Markdown 渲染：

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

只生成微信公众号 HTML 模式可粘贴片段：

```bash
python3 scripts/render.py \
  --theme claude \
  --input article.md \
  --output article.fragment.html \
  --fragment-only \
  --verify
```

## 内置主题

- `song`：宋式美学。人文、评论、书评、生活方式。
- `mimo`：Xiaomi MiMo。AI、产品发布、技术报告、研究解读。
- `claude`：Claude。教程、文档、方法论、技术观点。

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
- `meta.json`：必选，记录版本、主题、输入来源、是否优化布局和产物路径。

## 架构

```text
kairos-wechat-typeset/
├── DESIGN.md
├── SKILL.md
├── goldens/
│   ├── song-style.html
│   ├── mimo-style.html
│   └── claude-style.html
├── themes/
│   ├── registry.json
│   ├── song.json
│   ├── song/DESIGN.md
│   ├── mimo.json
│   ├── mimo/DESIGN.md
│   ├── claude.json
│   └── claude/DESIGN.md
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
│   └── editorial_verify.py
└── scripts/
    ├── render.py
    └── verify.py
```

`themes/<theme-id>.json` 是确定性视觉契约，`themes/<theme-id>/DESIGN.md` 是人工设计说明，`goldens/` 是最高视觉参照。

## V2 Pipeline

```text
Markdown path / Markdown text / non-Markdown text
  -> Input normalization
  -> Ask whether to optimize layout
  -> Optional layout Markdown
  -> Ask user to choose a built-in theme
  -> Semantic Analysis
  -> Art Direction
  -> Rhythm Engine
  -> Layout Resolver
  -> Deterministic Renderer
  -> WeChat Verify + Editorial Verify
  -> Versioned output under ~/.wechat-typeset
```

## LLM 与脚本分工

- LLM 只优化 Markdown：标题层级、段落节奏、重点句、引用、列表、分隔线。
- LLM 不生成 HTML、不写 CSS、不新增自定义标签，不决定 typography、spacing、layout。
- 脚本负责确定性渲染：解析 Markdown、加载主题、分析语义、解析节奏、输出全内联 HTML、执行验证。

如果用户不选择优化布局，脚本不输出 `layout.md`，直接使用当前 Markdown 渲染。如果输入不是 Markdown，脚本会先做最小 Markdown 标准化。

## 支持的 Markdown

- 标题、段落、列表、引用、分割线
- 粗体、斜体、删除线、行内代码、链接、图片
- 围栏代码块
- 简单表格，自动降级为移动端堆叠信息卡
- `==重点句==`
- `> [!NOTE]` / `> [!TIP]` / `> [!WARNING]`
- `## 01 标题` 数字章节标题

## 验证

渲染时加 `--verify`，或单独运行：

```bash
python3 scripts/verify.py \
  --input article.html
```

验证项包括：无 `<style>`、无 `class=`、无外部 CSS、无脚本、无原生宽表格、图片移动端安全，以及 heading 不跳级、连续长段不超过 3、连续强强调不超过 2、高密度区块必须有 breathing。

验证布局 Markdown：

```bash
python3 scripts/verify_markdown.py \
  --input layout.md
```

## 开发者新增主题

见 [`themes/README.md`](themes/README.md)。新增主题需要：

1. 新建 `themes/<theme-id>/DESIGN.md`
2. 新建 `themes/<theme-id>.json`
3. 注册到 `themes/registry.json`
4. 使用开发者自备 Markdown 样例渲染完整 HTML
5. 通过 `--verify`、检查 `goldens/` 对齐度，并进行移动端预览
