# Claude DESIGN.md

## Theme Position

Claude 主题用于教程、解释型文章、文档、方法论、产品说明和技术观点。它借鉴 Claude 产品和文档的温和、清晰、低干扰、移动适配和层级秩序，目标是在微信公众号正文中形成“可持续阅读的解释型文档”。

Claude 主题不是官网复刻、聊天界面截图或品牌页。它只转译正文可控范围内的设计原则：暖中性纸面、少量层级、低噪声组件、清晰的步骤、代码和提示块。

## Visual Language

- 关键词：暖文档、低噪声、清晰层级、耐读、可信、温和、解释秩序。
- 适合：教程、指南、产品说明、技术观点、方法论文章、长解释文章。
- 技术表达重心：步骤、提示块、代码块、表格、任务清单和中英混排稳定性。
- 禁止：强烈装饰、深色大面积背景、花哨卡片、营销式 hero、过度艺术化断行、大号装饰编号、频繁横线。

## Tokens

- Paper: warm off-white, quiet and not pure white.
- Ink: near black for headings, softened dark gray for body text.
- Muted: neutral warm gray for metadata, captions, labels, and list markers.
- Accent: muted rust, used only for links, highlights, tip borders, and rare semantic emphasis.
- Font: clean sans for doc clarity; mono for code.
- Type scale: H1 is 28px, H2 is 20px, H3/body text is 16px, labels/code/captions/lists are 14px, tiny divider marks are 12px.
- Weight scale: prefer 400 and 600. Use 700 only when inherited component compatibility requires it.

## Components

- H1: 28px calm documentation title, left aligned, not a hero.
- H2 numeric: 20px compact section label plus title. Avoid theatrical 32px numbers.
- H3-H6: 16px/600 subsection headings without repeated underline noise.
- Paragraph: clean sans body, comfortable line-height, compact enough for mobile.
- Lead: opening paragraph that states the article promise without becoming a card.
- Insight: short left-rule emphasis for the key explanatory sentence.
- Quote: warm paper block with soft edge and a clear but quiet semantic border.
- Callout: same quote system with subtle NOTE/TIP/WARNING left-line differences.
- Pullquote: quiet excerpt, not a decorative poster.
- Code: 14px documentation-style block, readable contrast, soft background, thin border.
- Inline code: 14px or inherited small code token that does not disturb line height.
- Table: mobile-safe ledger cards with clear label/value relationship and low border noise.
- Lists: simple markers, vertically aligned with text. Task lists render explicit checkbox states instead of raw `[x]` text.
- Divider: very light section pause. Use sparingly.

## Mobile Rules

- Body must feel like a doc you can read for 10 minutes.
- Avoid tiny labels except divider marks.
- Keep all component widths within mobile viewport.
- Images and captions remain quiet and factual.
- List markers, task checkboxes, and table labels must align visually with their text.
- No horizontal scroll at 390px or 430px.

## Quality Gates

- All styles inline.
- No raw HTML passthrough from Markdown.
- New changes must keep rendered outputs visually distinct from Song and MiMo.
- Render `fixtures/claude-style-system.md` before accepting component changes.
- Audit should keep the primary type scale bounded to 12px, 14px, 16px, 20px, and 28px.
