# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.0.0] - 2026-06-13

Initial release of Kairos Skills — Agent Harness Engineering for content production.

### kairos-wechat-typeset

- Deterministic Markdown-to-WeChat HTML renderer
- 4 built-in themes: song (宋式美学), wending (稳境白纸), tech (科技), wisme (WISME 规范)
- Semantic component system: lead, insight, pullquote, figure, soft-list, closing-note
- Theme JSON contract: all visual tokens locked in JSON, renderer reads deterministically
- Typography hierarchy: H1 30px → H2 22px → Body 16px, standardized line-heights (1.0/1.2/1.5/1.7)
- Color system: 4 functional colors per theme (ink, muted, surface, accent)
- Web font support: optional Noto Serif SC / Noto Sans SC via jsDelivr CDN
- Quality gates: html_verify, editorial_verify, audit_visual
- 25 anti-patterns with Bad/Fix examples
- Category routing: 10 article types → recommended theme/component/density
- Layout recipes: 6 numbered composition patterns (W01-W06)
- No text backgrounds on any element (transparent only)
- Feedback protocol for converting vague feedback to precise parameters

### kairos-visual-generator

- Deterministic consulting-style visual card generator
- 2 visual systems: Editorial Magazine, Swiss Consulting
- 12 theme presets: 9 Editorial + 4 Swiss (including Kami Paper)
- 11 layout skeletons: E01-E03 + S01-S08
- 5 aspect ratios: 4:5, 3:4, 1:1, 5:2, 16:9
- Intake Gate: structured requirement validation before generation
- Metaphor selection system with 15 business metaphors
- Title reconstruction rules (3-layer system)
- Design system verification script
- Font loading guidance for browser-rendered cards
- Noto Sans/Serif SC as primary CJK fonts

### Project Infrastructure

- 3-tier documentation: CHEATSHEET.md (quick ref) → SKILL.md (full workflow) → references/ (deep specs)
- PRODUCT.md for both skills: design decisions, style lock, texture rules
- Root README: 30-second quick start, architecture diagram, design principles
- CONTRIBUTING.md: skill directory contract, commit style, validation checklist
- skills.json: machine-readable inventory with validation commands
- Routing-trigger descriptions for agent discovery
