# Pi 开发者主题 DESIGN.md

## Theme Position

Pi 主题受 pi.dev 的极简开发者美学启发，面向开发者文档、技术教程、API 参考和工具指南。核心特征：干净的无衬线排版、青色（teal）强调层级、终端风格代码块、充足的留白、扫描优先的布局。

本主题不复刻 pi.dev 的终端 UI。它把 Pi 的视觉语言翻译为微信公众号正文可控表面：青色编号、细线秩序、暗色代码块、浅青色信息提示和宽松的手机阅读节奏。

## Visual Language

- 关键词：青色 teal、纯白纸面、强标题、细线、6px 圆角、暗色代码、浅青提示。
- 适用文章类型：开发者文档、技术教程、API 参考、工具指南、编程实战、开源项目介绍。
- 禁止：渐变背景、强投影、多色强调、厚重卡片、营销按钮、深色整页、装饰性图标。
- 页面气质：像一套已经排进公众号手机正文里的开发者组件体系，干净、克制、高效。

## Tokens

- H1: 30px / 1.3，深色，粗体，左对齐。
- H2: 22px 深色标题，左侧青色竖线标记，底部细线分隔。
- H3: 17px / 1.6，深色，粗体。
- 正文: 16px / 1.8，`#1e293b`，行距比 tech 主题更宽松。
- 辅助信息、列表、图注、代码标签: 14px，灰色。
- Code: 14px 等宽字体，暗色面板 `#1e293b`，6px 圆角。

主色只有 `#0d9488`。浅青只作为同一主色的低浓度信息底，不引入第二强调色。

## Components

- H1: 30px 深色标题，紧凑但不压迫。
- Lead: 作为元信息/导语的正文内表达，灰字、小节奏。
- H2: 左侧 3px 青色竖线 + 22px 深色标题，底部浅灰细线。
- H3-H6: 17px 深色小标题。
- Paragraph: 16px / 1.8，段距 20px。
- Highlight: 浅青底、青色字，用于重点句，不能高频使用。
- Quote / Pullquote: 左侧青色线，正文灰黑，克制的技术引用感。
- Insight / Closing note: 浅青信息块，6px 圆角。
- Figure: 图片 100% 宽，6px 圆角，图注 14px 灰色左对齐。
- Lists: 青色圆点或数字，任务清单使用 12px 方框，完成态青底白勾。
- Code: 暗色代码块，14px 等宽字体，语言标签在块上方，圆角 6px。
- Table: faux table，14px 字号，细线网格，表头浅青底。
- Divider: 细线为主，青色短线用于章节强调。

## Mobile Rules

- 内容最大宽度 640px，默认左右内边距 24px。
- 主要验收宽度为 390px 和 430px。
- 所有样式内联，无 `style` 标签、无 `class`、无外部 CSS。
- 表格使用 faux table，不输出原生 table。
- 代码块使用 `pre-wrap`，不得依赖横向滚动。
- 图片必须 `max-width: 100%`、`height: auto`、圆角 6px。

## Quality Gates

- `themes/pi.json` 与本文档同步维护。
- `fixtures/pi-style-system.md` 是唯一验收 fixture。
- `goldens/pi-style.html` 必须由该 fixture 渲染得到。
- 修改主题后运行 JSON 校验、HTML verify、visual audit，并在 390px 与 430px 宽度下检查无横向溢出。