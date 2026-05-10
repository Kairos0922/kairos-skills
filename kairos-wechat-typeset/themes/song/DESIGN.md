# 宋式美学 DESIGN.md

## Theme Position

宋式美学用于人文评论、生活方式、书评、随笔和慢阅读长文。它的目标是“纸、墨、留白、呼吸”，让微信公众号移动端读起来像一页现代中文杂志，也像一张安静的电子墨水屏。

本主题的方向是宋刊式 Mobile Editorial：现代、克制、大气，不做古风装饰，也不把组件堆成卡片。它首先服务微信公众号移动端连续阅读，而不是桌面展示页。

## Visual Language

- 关键词：思源宋体、暖白纸、低饱和、松弛、细线、克制强调。
- 适合：观点长文、文化观察、生活方式、个人叙事。
- 禁止：高饱和彩色渐变、强阴影、厚边框、卡片堆叠、emoji 图标、大面积色块。

## Tokens

- Paper: warm off-white, close to paper but lighter than beige.
- Ink: warm black/brown, not hard black.
- Accent: one muted cinnabar/brown-red, only for rare emphasis, links, and semantic callouts.
- Serif-first: CJK uses Source Han Serif first; Latin and numbers use classic serif.
- Type scale: headings are 18px; all non-heading text is 16px.

## Components

- H1: magazine opening title, left aligned, separated by whitespace rather than a rule.
- H2 numeric: Chinese section label in the form `一、标题`; hierarchy comes from weight and rhythm, not underlines.
- H3-H6: degrade to restrained subsection headings without left rules or repeated H2 blocks.
- Paragraph: comfortable line-height, low contrast text, mobile-first rhythm.
- Lead: opening body paragraph for the editable article body; it creates magazine tone without relying on the WeChat article title area.
- Quote: light paper surface plus restrained cinnabar left rule, matching the reference pullquote language.
- Callout: same quote system with a tiny Chinese label such as 注、笺、警.
- Pullquote: editorial excerpt with one light paper surface and a restrained cinnabar left rule.
- Figure: single-column image plus centered caption; image mood comes from the source asset, not decorative CSS.
- Lists: normal unordered, ordered, task-list fallback, and soft-list blocks share the cinnabar hollow-circle marker in `song` to keep the reference rhythm unified.
- Code: proof-sheet block with fine top/bottom rules and a small label.
- Table: stacked ledger entries with soft left alignment, not rounded cards or repeated field separators.
- Divider: short left/right hairlines with one soft central mark; use sparingly so the article does not become line-heavy.
- Closing note: quiet centered ending paragraph for article-body closure.

## Editable Body Boundary

WeChat only lets this skill control the article body. Do not treat platform title, cover image, account header, menus, or external page chrome as theme surface. If a reference image shows a magazine opening, translate only the body-safe parts into components: lead paragraph, figure, pullquote, soft list, divider, and closing note. Do not add seals or free-positioned decorations.

## Mobile Rules

- Content width max 640px, body padding 16px on mobile.
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
- Render `fixtures/visual-matrix.md` before accepting component changes.
