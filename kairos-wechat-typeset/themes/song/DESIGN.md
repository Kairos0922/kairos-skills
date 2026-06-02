# 宋式美学 DESIGN.md

## Theme Position

宋式美学是一个宋式中文正文系统，而不是古风装饰主题或一次性 CSS 皮肤。它的目标是把“纸、墨、秩序、克制、呼吸”翻译成微信公众号正文里稳定可复用的排版语言。

本主题优先保障技术文章的结构清晰、代码可读、表格稳定和提示块可扫描；同时保留人文随笔、生活方式、书评和慢阅读长文需要的导语、图文、摘引、柔性列表和收束能力。它首先服务微信公众号移动端连续阅读，而不是桌面展示页。

参考母版中的山水、生活器物和大幅留白只作为方法论来源：暖纸、墨色层级、细线秩序、适度空白、低饱和强调。不得照搬山水图、生活图标、自由定位或展览式留白作为默认技术文章外观。

## Visual Language

- 关键词：思源宋体、暖白纸、墨黑、低饱和金棕、细线、技术秩序、克制强调。
- 适合：技术长文、方法论、产品解释、观点长文、文化观察、生活方式、书评、个人叙事。
- 技术文章表达重心：标题层级、段落节奏、代码块、表格、NOTE/TIP/WARNING、步骤和清单。
- 人文与生活方式表达重心：lead、figure、pullquote、soft-list、closing-note 和更舒展的段落呼吸。
- 禁止：高饱和彩色渐变、强阴影、厚边框、卡片堆叠、emoji 图标、大面积色块、古风印章、山水背景、装饰性图标列表。

## Tokens

- Paper: warm off-white, close to paper but lighter than beige.
- Ink: near black, softened for long Chinese reading.
- Muted: neutral gray-brown for captions, labels, and secondary metadata.
- Accent: one muted gold-brown, only for rare emphasis, links, semantic callouts, list markers, and fine rules.
- Serif-first: CJK uses Source Han Serif first; Latin and numbers use classic serif.
- Type scale: H1 is 28px, H2 main titles are 25px with 12px section metadata, H3/body text is 16px, annotations/quotes/code/tables are 14px.

## Components

- H1: 28px calm opening title, left aligned, heavier than body but not poster-sized; separated by whitespace rather than a rule.
- H2 numeric: magazine-style section heading with a 12px serif metadata line such as `SECTION 02`, a 25px Chinese main title in the form `二、标题`, and one thin bottom rule. Hierarchy comes from controlled metadata, type contrast, and rhythm rather than decoration.
- H2 non-numeric: the same 25px main-title treatment and bottom rule without fabricated section metadata.
- H3-H6: 16px restrained subsection headings; they support scanability in technical articles without becoming repeated H2 blocks.
- Paragraph: comfortable line-height, low contrast text, mobile-first rhythm. Technical paragraphs stay compact; literary paragraphs may breathe through semantic layout.
- Lead: opening body paragraph for the editable article body; it creates tone without relying on the WeChat article title area.
- Quote: 14px quiet paper surface with a thin full border for citation-style quoted text. Avoid extra top/bottom rules.
- Callout: same quote system with a tiny Chinese label such as 注、笺、警, optimized for technical reminders and warnings.
- Pullquote: 14px editorial excerpt with one light paper surface and a restrained left rule. Use sparingly and avoid extra horizontal rules.
- Figure: single-column image plus centered caption; image mood comes from the source asset, not decorative CSS.
- Lists: unordered and soft-list blocks use a gold-brown hollow marker; ordered lists keep explicit numbers; task lists render as square checked/unchecked states.
- Code: 14px proof-sheet block with line numbers, warm paper fill, a small language label, and a thin border.
- Table: 14px mobile-safe faux grid that borrows the reference table's fine-line order without becoming a native wide table.
- Divider: short left/right hairlines with one soft central mark; use sparingly so the article does not become line-heavy.
- Closing note: quiet centered ending paragraph for article-body closure.

## Article Type Strategy

- Technical: favor compact rhythm, clear headings, code labels, ledger-like tables, and callout labels. Do not introduce scenic whitespace or decorative figures unless the source content contains them.
- Humanities: allow more lead, pullquote, divider, and closing-note usage. Keep the same token system so the article still belongs to Song.
- Lifestyle: allow stronger figure and soft-list rhythm, but use source images and semantic components rather than built-in decorative icons.

## Image Direction

Song image planning should be sparse and editorial. Prefer 16:9 images that explain a concept, reveal a method structure, establish a quiet opening atmosphere, or support a real comparison. The visual language is warm off-white paper, restrained ink, low saturation, fine line order, and quiet stillness.

Do not use images as section decoration. Avoid ancient seals, landscape posters, decorative icon lists, strong shadows, gradients, busy collages, and high-contrast color surfaces. Technical articles should usually prefer concept diagrams over scenic or lifestyle imagery.

## Editable Body Boundary

WeChat only lets this skill control the article body. Do not treat platform title, cover image, account header, menus, or external page chrome as theme surface. If a reference image shows a magazine opening, translate only the body-safe parts into components: lead paragraph, figure, pullquote, soft list, divider, and closing note. Do not add seals or free-positioned decorations.

## Mobile Rules

- Content width max 720px, body padding 24px on desktop and mobile-safe padding on narrow screens.
- Chapter gaps must stay readable but compact; avoid exhibition-style blank space.
- Quote and callout blocks should sit inside the reading flow, not behave like standalone posters.
- Divider-to-heading rhythm should feel like one pause, not two stacked pauses.
- Quote top/bottom margins should stay close to paragraph rhythm.
- No horizontal scroll.
- Images must be block-level, max-width 100%, subtle radius.
- Tables never render as native wide tables.

## Quality Gates

- All styles inline.
- No `<style>`, no CSS classes, no user theme overrides.
- Theme changes must update both this file and `themes/song.json`.
- Render `fixtures/song-style-system.md` before accepting component changes.
- For Song, the technical golden is the primary acceptance fixture. Humanistic and lifestyle capability should be covered through semantic components without replacing the technical acceptance path.
