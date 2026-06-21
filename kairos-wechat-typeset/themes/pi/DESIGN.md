# Pi 开发者主题 DESIGN.md

## Theme Position

Pi 主题从 pi.dev 的实际 CSS 源码中提取设计语言：Plantin MT Pro 衬线正文、Commit Mono / Departure Mono 等宽标签、暖调羊皮纸色系（`#ebe7e4`）、柔和潮汐蓝强调（`#4b607c`）、零圆角锐利边框、低对比度暖灰线条。

本主题不复刻 pi.dev 的深色终端 UI。它把 Pi 的视觉基因翻译为微信公众号正文可控表面：衬线正文、monospace 标签、暖纸面、柔和蓝强调、锐利边框、克制的技术引用感。

## Visual Language

- 关键词：衬线正文、暖羊皮纸、monospace 标签、潮汐蓝、锐利边角、低对比度线条。
- 适用文章类型：开发者文档、技术教程、API 参考、工具指南、编程实战、开源项目介绍。
- 禁止：渐变背景、强投影、多色强调、厚重卡片、营销按钮、圆角装饰、深色整页。
- 页面气质：像一本精致的技术杂志内页，温暖、克制、有阅读感。

## Tokens（从 pi.dev CSS 源码提取）

Pi.dev 的 CSS 变量：

| Pi.dev 变量 | 值 | 主题映射 |
|-------------|-----|---------|
| `--bg-canvas` (light) | `#ebe7e4` | `body.background` |
| `--panel` (light) | `#f4f2f0` | `colors.surface` |
| `--text` (light) | `#252f3df5` | `colors.ink` |
| `--muted` (light) | `#5c5752c4` | `colors.muted` |
| `--line` (light) | `#8b847d59` | `colors.line` |
| `--accent` (light) | `#4b607c` | `colors.accent` |
| `--accent-rust` (light) | `#b86b52` | `colors.warning` |
| `--serif` | Plantin MT Pro | `fonts.cjk` / `fonts.latin` |
| `--mono` | Commit Mono | `fonts.mono` |
| `--accent-mono` | Departure Mono | `fonts.label` |
| `--body-copy-line-height` | `1.55` | `typography.body_line` |

字号与层级：

- H1: 30px / 1.35，深蓝灰色，衬线体，粗体。
- H2: 22px 深色标题，左侧潮汐蓝 3px 竖线，底部暖灰细线。
- H3: 17px / 1.6，深色，粗体。
- 正文: 16px / 1.65，`#384251`，衬线体。
- 标签: 14px monospace，大写，0.13em 字距，灰色。
- Code: 14px 等宽字体，暗色面板 `#212730`，零圆角。

主色只有 `#4b607c`（潮汐蓝）。赤陶色 `#b86b52` 仅用于警告。

## Components

- H1: 30px 深色衬线标题。
- Lead: 作为元信息/导语，灰字、monospace 标签感。
- H2: 左侧 3px 潮汐蓝竖线 + 22px 深色标题，底部暖灰细线。
- H3-H6: 17px 深色小标题。
- Paragraph: 16px / 1.65，段距 18px，衬线体。
- Highlight: 潮汐蓝浅底、蓝字，用于重点句。
- Quote / Pullquote: 左侧潮汐蓝线，正文灰黑。
- Insight / Closing note: 浅蓝信息块，零圆角。
- Figure: 图片 100% 宽，4px 微圆角，图注 14px 灰色。
- Lists: 潮汐蓝圆点或数字，任务清单使用 12px 方框。
- Code: 暗色代码块，14px 等宽字体，零圆角。
- Table: faux table，14px 字号，暖灰细线网格，表头浅蓝底。
- Divider: 暖灰细线。

## Mobile Rules

- 内容最大宽度 640px，默认左右内边距 24px。
- 主要验收宽度为 390px 和 430px。
- 所有样式内联，无 `style` 标签、无 `class`、无外部 CSS。
- 表格使用 faux table，不输出原生 table。
- 代码块使用 `pre-wrap`，不得依赖横向滚动。
- 图片必须 `max-width: 100%`、`height: auto`。

## Quality Gates

- `themes/pi.json` 与本文档同步维护。
- `fixtures/pi-style-system.md` 是唯一验收 fixture。
- `goldens/pi-style.html` 必须由该 fixture 渲染得到。
- 修改主题后运行 JSON 校验、HTML verify、visual audit，并在 390px 与 430px 宽度下检查无横向溢出。
