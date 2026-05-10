# 宋式美学 DESIGN.md

## Theme Position

宋式美学用于人文评论、生活方式、书评、随笔和慢阅读长文。它的目标是“纸、墨、留白、呼吸”，让微信公众号移动端读起来像一页温润的电子杂志，也像一张安静的电子墨水屏。

## Visual Language

- 关键词：宋体、暖纸、低饱和、松弛、细线、克制强调。
- 适合：观点长文、文化观察、生活方式、个人叙事。
- 禁止：高饱和彩色渐变、强阴影、厚边框、卡片堆叠、emoji 图标。

## Tokens

- Paper: warm ivory, not pure white.
- Ink: warm black/brown, not hard black.
- Accent: only for rare emphasis and tip callout.
- Serif-first: CJK uses Songti; Latin and numbers use classic serif.

## Components

- H1: compact editorial title, left aligned.
- H2 numeric: large pale number plus ruled section title.
- Paragraph: long line-height, low contrast text, mobile-first rhythm.
- Quote/callout: soft paper surface, thin left border, no heavy container.
- Code/table: paper-like block; table degrades to stacked field cards.

## Mobile Rules

- Content width max 640px, body padding 16px on mobile.
- No horizontal scroll.
- Images must be block-level, max-width 100%, subtle radius.
- Tables never render as native wide tables.

## Quality Gates

- All styles inline.
- No `<style>`, no CSS classes, no user theme overrides.
- Theme changes must update both this file and `themes/song.json`.
