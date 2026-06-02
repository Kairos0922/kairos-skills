# WISME 规范主题 DESIGN.md

## Theme Position

WISME 规范主题根据附件设计图落地。它面向知识科普、研究报告、组件规范、方法论和专业说明，把参考图中的“微信公众号文章组件规范”翻译为微信公众号正文可控表面：强黑标题、红色单强调、黑白灰秩序、细线分隔、规格化表格、暗色代码块、浅红重点句和干净留白。

本主题不复刻设计稿画布、右上角账号标识、规范卡片、整页双栏排版或封面式说明区。微信公众号正文只能控制正文流，因此 WISME 将参考图的视觉语言转译到标题、导语、章节、正文、引用、列表、代码、表格、图片、重点句和延伸阅读里。

## Visual Language

- 关键词：简洁、清晰、专注、高级、黑白灰、红色短线、规格表、正文组件规范。
- 适用文章类型：知识科普、研究报告、组件规范、方法论、专业说明。
- 禁止：渐变、彩色多强调、装饰插画、强投影、胶囊堆叠、营销按钮、深色整页。
- 页面气质：像一份已经排进公众号正文的组件规范，而不是营销落地页。

## Tokens

参考图里的字号与层级是硬约束：

- H1: 32px / 1.28，黑色，粗体；正文内允许红色强调词。
- H2 numeric: 16px 数字编号 + 18px 黑色章节标题，同一行，右侧细灰线。
- H3: 16px / 1.6，黑色，粗体。
- 正文: 15px / 1.8，`#333333`。
- 辅助信息、列表、图注、代码标签: 13px，灰色。
- 强调: `#e63946`，只能用于重点句、短线、链接和关键标签。
- Code: 13px 等宽字体，暗色面板，4px 圆角，保留行号。

主色只有 `#e63946`。浅红底只作为同一主色的低浓度重点面，不引入第二强调色。

## Components

- H1: 强黑大标题，支持内联 `==规范==` 形成红色关键词。
- Lead: 作为标题下说明文字，15px 灰字，前置红色短线。
- H2 numeric: `01 文本样式` 式编号标题，编号和标题在同一行，右侧细线延伸。
- H2 non-numeric: 同样使用标题 + 右侧细线，不额外装饰。
- H3-H6: 16px 黑色小标题，保持规格表里的紧凑层级。
- Paragraph: 15px / 1.8，段距 16px。
- Highlight: 红字，不铺大面积底色；完整重点句可由 insight 使用浅红面板。
- Quote / Pullquote: 左侧红线，正文灰黑，pullquote 带红色引号符号。
- Insight: 浅红重点句面板，4px 圆角，左侧红色方框符号，承接设计图“重点句子”区域。
- Figure: 图片 100% 宽，4px 圆角，图注 13px 灰色居中。
- Lists: 黑色圆点或数字，任务清单使用 12px 方框，完成态黑底白勾。
- Code: 暗色代码块，13px 等宽字体，行号灰色，语言标签在块上方右侧保留复制感但不输出图标。
- Table: faux table，13px 字号，细线网格，表头浅灰底，移动端不横向溢出。
- Divider: 全宽细线或短红线语义，默认输出浅灰细线。
- Closing note: 灰色居中脚注，用于规范声明或版权提示。

## Image Direction

WISME image planning should behave like a specification artifact. Prefer 16:9 concept diagrams, process diagrams, comparison diagrams, and evidence figures when the article needs component structure, research framing, professional explanation, or source-backed visual evidence.

The visual language is black, white, gray, sparse red accent, strict alignment, thin rules, and report-like clarity. Avoid decorative illustration, unsourced evidence images, gradients, multi-accent palettes, strong shadows, pill-heavy layouts, large hero cards, dark full-page visuals, and busy collages.

## Mobile Rules

- 内容最大宽度 640px，默认左右内边距 20px。
- 主要验收宽度为 390px 和 430px。
- 所有样式内联，无 `style` 标签、无 `class`、无外部 CSS。
- 表格使用 faux table，不输出原生 table。
- 代码块使用 `pre-wrap`，不得依赖横向滚动。
- 图片必须 `max-width: 100%`、`height: auto`、圆角 4px。
- 细线只服务层级，避免把整篇文章压成表单。

## Quality Gates

- `themes/wisme.json` 与本文档同步维护。
- `fixtures/wisme-style-system.md` 是唯一验收 fixture。
- `goldens/wisme-style.html` 必须由该 fixture 渲染得到。
- 修改主题后运行 JSON 校验、Markdown 合约、HTML verify、visual audit、`typeset.py --check`，并在 390px 与 430px 宽度下检查无横向溢出。
