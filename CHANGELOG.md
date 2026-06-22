# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/).

## [1.1.0] - 2026-06-23

### kairos-wechat-typeset

- 新增第 5 套主题 `pi`（Pi 开发者主题）：衬线暖纸 + 潮汐蓝 + monospace 标签，适用于开发者文档、技术教程、API 参考
- 新增 `pi` 主题配套资产：golden (`goldens/pi-style.html`)、fixture (`fixtures/pi-style-system.md`)、主题 tokens (`themes/pi.json`)、设计规范 (`themes/pi/DESIGN.md`)
- 新增语义分析引擎 `semantic/analyze.py`：为每个块计算 importance / intent / density / emphasis_count / should_split / position 信号，作为美术指导与节奏决策的确定性输入
- 新增 renderer 契约层 `renderer/{blocks,compiler,variants}.py`：定义 16 种语义块与 6 种 Kairos 容器组件，强制"每组件 ≤3 变体"约束
- 新增视觉漂移审计脚本 `scripts/audit_visual.py`：字号、间距、边框密度、背景色审计
- 主题数量 4 → 5，版本 1.0.0 → 1.1.0

### kairos-visual-generator

- 新增第 3 套视觉系统 Mondrian / De Stijl（蒙德里安风格）：适用于设计、艺术、建筑、品牌
- 新增第 4 套视觉系统 Ticket / Receipt（票据风格）：适用于行程、日程、清单、预算、时间轴
- 新增对应 golden 与 composition 配置（mondrian-art、ticket-boarding-pass）
- 视觉系统数量 2 → 4，版本 2.0.0 → 2.1.0

### Project Infrastructure

- 在根 `skills.json` 正式注册 `kairos-wechat-typeset` 技能（含 entrypoints 与 validation 命令）
- 修正 `skills.json` 中 `kairos-visual-generator` 的版本号与 summary，补齐 entrypoints（references/design_system.md、scripts/select_metaphor.py）
- `Makefile` 的 `showcase` 目标覆盖全部 5 个主题（补 pi 主题渲染命令）

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
