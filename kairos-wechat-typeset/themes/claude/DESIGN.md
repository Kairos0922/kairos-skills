# Claude DESIGN.md

## Theme Position

Claude 主题用于教程、解释型文章、文档、方法论和技术观点。它借鉴 Claude Docs 的温和、清晰、纸感和层级秩序，目标是在微信移动端形成“可持续阅读的说明文档”。

## Visual Language

- 关键词：暖文档、柔和边界、清晰层级、耐读、可信、温和。
- 适合：教程、指南、产品说明、技术观点、方法论文章。
- 禁止：强烈装饰、深色大面积背景、花哨卡片、过度艺术化断行。

## Tokens

- Paper: warm off-white.
- Ink: brown-black.
- Accent: muted rust, used for links, highlights, tip borders.
- Font: clean sans for doc clarity; mono for code.

## Components

- H1: calm documentation title, slightly editorial.
- H2 numeric: visible but not theatrical.
- Paragraph: clean sans body, generous line-height.
- Callout: warm paper block with soft edge and clear semantic border.
- Code/table: documentation-style surfaces with readable contrast.

## Mobile Rules

- Body must feel like a doc you can read for 10 minutes.
- Avoid tiny labels except table/code metadata.
- Keep all component widths within mobile viewport.
- Images and captions remain quiet and factual.

## Quality Gates

- All styles inline.
- No raw HTML passthrough from Markdown.
- New changes must keep rendered outputs visually distinct from Song and MiMo.
