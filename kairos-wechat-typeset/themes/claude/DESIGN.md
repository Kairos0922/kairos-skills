# Claude DESIGN.md

## Theme Position

Claude 主题用于教程、解释型文章、文档、方法论、产品说明和技术观点。它以附件中的 Claude Design Language 母版为方向：Paper 背景、Ink / Stone / Paper 三色系统、系统字体层级、8px spacing system、细线分区和可扫描内容组件。

Claude 主题不是聊天界面截图，也不是通用文档皮肤。它要贴近参考图中可落地到微信公众号正文的部分：微暖纸面、浅 Stone 组件、细线结构、低饱和图片、引用符号、代码块、任务清单、表格和底部提示条。中文示例不直接照搬英文参考图的 52px 大标题，避免中文标题在移动端失衡。

## Visual Language

- 关键词：Paper、Ink、Stone、system font、fine rules、calm intelligent reading、clarity and focus。
- 适合：教程、指南、产品说明、技术观点、方法论文章、长解释文章。
- 技术表达重心：大标题开篇、说明段、insight 细线块、外部 quote、步骤、代码块、表格、任务清单和图片。
- 禁止：强烈装饰、深色大面积背景、花哨卡片、营销式 hero、过度圆角卡片堆叠、亮色强调、厚边框。

## Tokens

- Paper: `#F7F5F2`, page background and primary surface.
- Ink: `#1D1D1B`, headings, quote marks, primary text.
- Stone: `#A8A29B`, neutral swatches, subtle rules, component icons.
- Body text: `#4F4F4A`.
- Line: warm gray hairlines.
- Font: default system sans for Chinese readability; mono for code.
- Type scale for Chinese WeChat body: all headings 18px; everything else 16px.
- Spacing: base unit 8px; common steps 8, 16, 24, 40, 64, 96.

## Components

- H1: 18px system-font editorial title, left aligned, balanced for Chinese mobile reading.
- H2 numeric: quiet 16px `01` label plus 18px section heading; number is metadata, not a competing title.
- H3-H6: 18px system-font subheads.
- Paragraph: system-font body, 16px / 1.75.
- Lead: opening body paragraph with calm explanatory tone.
- Insight / callout: shallow Stone surface with a left hairline, like the reference connector explanation block.
- Quote: large Stone quote mark plus serif text, no heavy card.
- Pullquote: same quote language, for key article excerpts.
- Code: Paper/Stone code panel with 16px mono text, thin border and small language label.
- Inline code: subtle Stone chip at 16px.
- Table: true fine-line grid in inline spans, matching the reference table more closely than stacked cards.
- Lists: small system-font markers, vertically aligned. Task lists render checked/unchecked square boxes.
- Figure: grayscale/stone-toned image area, square corners, quiet caption.
- Divider: one thin hairline, used sparingly.
- Closing note: shallow Stone strip with star mark, matching the reference bottom note.

## Mobile Rules

- Body must feel like a doc you can read for 10 minutes.
- Preserve the reference type contrast without causing mobile overflow.
- Keep all component widths within mobile viewport.
- Images and captions remain quiet and factual.
- List markers, task checkboxes, and table labels must align visually with their text.
- No horizontal scroll at 390px or 430px.

## Quality Gates

- All styles inline.
- No raw HTML passthrough from Markdown.
- New changes must keep rendered outputs visually distinct from Song and MiMo.
- Render `fixtures/claude-style-system.md` before accepting component changes.
- Audit should keep the primary type scale bounded to 16px and 18px.
