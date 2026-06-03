# kairos-wechat-typeset

`kairos-wechat-typeset` 把标准 Markdown 文章转换成微信公众号编辑器友好的多主题 HTML。它不是普通 Markdown Renderer，而是确定性的 WeChat Editorial Design Skill：先用人工视觉母版定义高级感，再用主题哲学、节奏引擎和校验规则稳定复现。

## 适用场景

用它处理已经写好或接近写好的公众号长文，尤其是需要稳定品牌感、移动端阅读节奏和可重复主题效果的文章。

| 输入 | 输出 | 适合用户 |
| --- | --- | --- |
| Markdown 文件、Markdown 文本或普通文本 | 可粘贴到微信公众号编辑器的内联 HTML | 写作者、产品经理、技术作者、内容运营、AI agent |
| agent 优化后的 `layout.md` | 版本化 `output.html`、`meta.json` 和可选配图计划 | 需要一套可复用内容生产流程的人 |

它不替代微信公众号平台标题、封面图、账号信息或发布流程，也不允许用户传自定义 CSS。产品重点是正文排版质量、主题一致性和 agent 可维护性。

## 60 秒上手

查看内置主题：

```bash
python3 scripts/render.py --list-themes
```

快速健康检查：

```bash
python3 scripts/check_all.py --smoke
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

完成后打开终端输出里的 `output.html` 路径。发布到微信公众号时，优先使用 `--fragment-only` 生成正文片段；如果需要离线预览，再使用完整 HTML。

### 端到端例子

输入 `article.md`：

```markdown
# AI 产品发布复盘

过去一年，AI 产品的竞争从模型能力转向可被普通用户感知的体验。

==真正影响留存的，往往不是一次惊艳演示，而是用户第二天还愿不愿意打开。==

## 01 入口：让复杂能力变得可接近

> [!NOTE] 入口设计要服务于心智建模
> 用户第一次使用时，最需要的是一个能立刻成功的动作。
```

运行：

```bash
python3 scripts/typeset.py \
  --input article.md \
  --theme tech \
  --optimize-layout no \
  --fragment-only \
  --non-interactive
```

结果会写入：

```text
~/.wechat-typeset/<article-slug>/vNNN/
  output.html
  meta.json
```

把 `output.html` 里的正文片段复制到微信公众号编辑器正文区域，再用微信编辑器自己的预览确认最终平台表现。

## 内置主题

- `song`：宋式美学主题。适用文章类型：技术长文、方法论、人文评论、生活方式、书评。
- `wending`：稳境白纸主题。适用文章类型：个人成长、心理秩序、生活方式、轻方法论、慢阅读文章。
- `tech`：科技主题。适用文章类型：AI 技术文章、工程实践、产品方案、研发实践、工具教程。
- `wisme`：WISME 规范主题。适用文章类型：知识科普、研究报告、组件规范、方法论、专业说明。

主题只能从 registry 中选择。用户不能传自定义 CSS、颜色、HTML 模板或运行时主题文件。

完整工作流会让用户选择内置主题，非交互模式必须显式传入 `--theme`。

### 主题选择指南

| 文章类型 | 推荐主题 | 原因 |
| --- | --- | --- |
| 技术教程、AI 工程实践、工具教程 | `tech` | 强化结构、代码、步骤和技术信息块 |
| 方法论长文、人文评论、书评 | `song` | 保留长文气息，用宋体秩序和留白承载观点 |
| 个人成长、心理秩序、慢阅读 | `wending` | 白纸感更安静，适合轻方法论和内省内容 |
| 知识科普、研究报告、组件规范 | `wisme` | 黑白灰红的规范感更适合说明、表格和专业材料 |

### 主题矩阵

| Theme | 视觉方向 | 核心抓手 | 避免的问题 |
|-------|----------|----------|------------|
| `song` | 文学纸面、墨色、宋体秩序 | 暖纸、宋体层级、克制细线 | 变成古风装饰或山水海报 |
| `wending` | 安静白纸、灰度规格 | 重宋标题、暖白底、浅灰引用面 | 变成普通卡片式成长文 |
| `tech` | 蓝色科技移动文章 | 蓝色编号、暗色代码、浅蓝信息块 | 变成 SaaS 落地页配色 |
| `wisme` | 黑白灰红组件规范 | 黑字标题、红色短线、灰色表格 | 变成静态设计稿而不是正文主题 |

四套主题共享同一套 Markdown 与 Kairos 语义组件矩阵。主题差异来自确定性 token、组件规则和少量 renderer 分支，而不是为单篇文章临场写样式。

## 输出目录与版本

用户产物不写入 skill 目录。默认输出到跨平台用户目录：

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

- `layout.md`：可选，仅在用户选择优化布局时生成。
- `output.html`：必选，排版后的 HTML。
- `meta.json`：必选，记录版本、主题、输入来源、是否优化布局、layout mode、内容 hash 和产物路径。
- `image-plan.json`：可选，仅在用户要求配图时由宿主 agent 生成并校验。
- `image-prompts.md`：可选，宿主 agent 没有生图能力时输出。
- `images/`：可选，宿主 agent 生成或用户提供的正文配图资产。

## 架构

```text
kairos-wechat-typeset/
├── DESIGN.md
├── SKILL.md
├── goldens/
│   ├── song-style.html
│   ├── wending-style.html
│   ├── tech-style.html
│   └── wisme-style.html
├── themes/
│   ├── registry.json
│   ├── song.json
│   ├── song/DESIGN.md
│   ├── wending.json
│   ├── wending/DESIGN.md
│   ├── tech.json
│   ├── tech/DESIGN.md
│   ├── wisme.json
│   └── wisme/DESIGN.md
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
- 配图由宿主 agent 介入：agent 根据文章和主题生成 `image-plan.json`，有生图能力时调用宿主工具生成图片，没有生图能力时输出 prompts。skill 不配置模型、不保存 API key、不绑定 provider。
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

## 文章配图

配图不是 renderer 的自由设计，也不是脚本内置生图模型。它是 agent-mediated workflow：skill 定义规则，agent 做编辑判断和生成动作，脚本负责验证，renderer 只渲染已有的 `:::figure`。

配图原则：

- 图片必须降低理解成本、提供证据、解释结构或建立必要的开场气质。
- 默认允许 `0` 张图；没有必要配图时，应在 `image-plan.json` 里说明原因。
- 默认比例为 `16:9`。
- 每张图必须包含 `purpose`、`why_needed`、`theme_fit`、`alt`、`caption`、`prompt` 和 `avoid`。
- 低必要性图片不进入计划；`necessity` 只能是 `high` 或 `medium`。
- `evidence_figure` 必须有 `source_note`。
- 生成图不得伪造截图、数据、图表、品牌、引用或事实证据。

允许的图像角色：

| Visual Type | 用途 |
| --- | --- |
| `concept_diagram` | 概念、框架、心智模型和抽象关系 |
| `process_diagram` | 流程、链路、管线和实现步骤 |
| `comparison_diagram` | 取舍、前后对比、能力矩阵和差异说明 |
| `evidence_figure` | 有来源的截图、研究图、产品状态或数据视觉 |
| `atmosphere_still` | 极少量开场定调图，主要适合文学、生活方式和慢阅读文章 |

微信公众号正文不能控制平台标题、封面图、账号信息、菜单和外部页面背景。`song` 的正文组件只追求单列阅读里的宋式杂志气质，不做印章、自由定位或封面式大标题。

## 质量目标

- 稳定输出：白名单语义组件、全内联样式、无任意 HTML/CSS。
- 快速扩主题：每个主题实现同一套组件矩阵，而不是为每篇文章临场补样式。
- 高级感：靠语义选择、留白、阅读节奏、克制强调和图文关系建立，不靠堆装饰。
- 移动端适配：表格使用微信移动端安全的 faux layout，代码块不依赖横向滚动，图片始终移动端安全。

## 验证

产品级健康检查：

```bash
python3 scripts/check_all.py --smoke
```

完整回归检查：

```bash
python3 scripts/check_all.py
```

渲染单篇文章时加 `--verify`，或单独运行：

```bash
python3 scripts/verify.py \
  --input article.html
```

### 常见限制

- 不生成或配置图片模型；配图由宿主 agent 负责，skill 只验证 `image-plan.json`。
- 不接受任意 HTML、CSS、`style`、`class` 或运行时主题文件。
- 不控制微信公众号封面、平台标题、账号信息和发布后台。
- 宽表格会被转成移动端安全结构，不追求桌面表格原貌。
- 微信编辑器可能在粘贴后调整部分细节，发布前仍需要平台预览确认。

验证项包括：无 `<style>`、无 `class=`、无外部 CSS、无脚本、无原生宽表格、图片移动端安全，以及 heading 不跳级、连续长段不超过 3、连续强强调不超过 2、高密度区块必须有 breathing。

完整工作流 `scripts/typeset.py` 会在渲染后自动执行 HTML 和 editorial verify。

验证布局 Markdown：

```bash
python3 scripts/verify_markdown.py \
  --input layout.md
```

验证配图计划：

```bash
python3 scripts/verify_image_plan.py \
  --input image-plan.json \
  --theme tech
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

见 [`themes/METHODOLOGY.md`](themes/METHODOLOGY.md) 与 [`themes/README.md`](themes/README.md)。当前四套主题沉淀出的快速方法是：先把参考图转成正文边界内的组件规则，再落 token、fixture、renderer 和 golden。

新增主题需要：

1. 先写主题 thesis、适用文章类型、禁用视觉手法和组件规则。
2. 新建 `themes/<theme-id>/DESIGN.md`。
3. 新建 `themes/<theme-id>.json`。
4. 注册到 `themes/registry.json`。
5. 使用对应的真实文章 fixture 渲染 `goldens/<theme-id>-style.html`，例如 `song` 使用 `fixtures/song-style-system.md`。
6. 更新 `README.md`、`SKILL.md`、`themes/README.md` 和仓库根目录 `skills.json`。
7. 通过 `--verify`、`scripts/audit_visual.py`、检查 `goldens/` 对齐度，并进行 390px / 430px 移动端预览。

快速新增高质量主题时，优先选择最接近的原型：

- `paper-literary`：从 `song` 开始，适合纸面、宋体、文学气质。
- `quiet-spec`：从 `wending` 开始，适合白纸、心理秩序、灰度规范。
- `technical-explicit`：从 `tech` 开始，适合代码、工程、蓝色技术层级。
- `component-spec`：从 `wisme` 开始，适合黑白灰、红色强调、组件规范类文章。

新增主题的正常变更清单：

```text
themes/<theme-id>.json
themes/<theme-id>/DESIGN.md
fixtures/<theme-id>-style-system.md
goldens/<theme-id>-style.html
themes/registry.json
scripts/render.py
README.md
SKILL.md
themes/README.md
../skills.json
```

质量门槛：

- Identity：看 H1、H2、引用、代码、表格、重点句就能识别主题。
- Matrix：所有共享 Markdown / Kairos 组件都有明确处理。
- Restraint：只有一个强调色，背景、边框和图标不抢内容。
- Reproducibility：fixture、golden、文档、registry、验证命令和 renderer 行为一致。

`wending` 使用 `fixtures/wending-style-system.md` 生成 `goldens/wending-style.html`，验收重点是 28px H1、22px H2、18px H3、16px 正文、14px 辅助/代码文字、暗色代码块、细线表格、8px 图片圆角和浅灰引用面。

`tech` 使用 `fixtures/tech-style-system.md` 生成 `goldens/tech-style.html`，验收重点是 28px H1、32px 蓝色章节编号、22px H2、18px H3、16px 正文、14px 辅助/代码文字、暗色代码块、浅蓝信息块、细线表格和 8px 图片圆角。

`wisme` 使用 `fixtures/wisme-style-system.md` 生成 `goldens/wisme-style.html`，验收重点是 32px H1、18px 章节标题、16px/13px 规格层级、15px 正文、红色单强调、暗色代码块、浅灰表格、浅红重点句面板和 4px 图片圆角。
