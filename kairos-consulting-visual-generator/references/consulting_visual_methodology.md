# Consulting Visual Methodology

This reference turns the skill from a prompt into a repeatable visual direction workflow. Load it when the task is ambiguous, high-stakes, or needs a stable consulting-grade card result.

The methodology is the primary operating system. Scripts may help with intake checks or first-pass metaphor suggestions, but they must not override user intent, context, or visual director judgment.

The target artifact is a refined visual card. It may contain analysis, but it must not look like a dense dashboard, an ordinary PPT slide, or a hand-built SVG chart with ugly typography.

## 1. Demand Clarity Before Output

Do not generate a final image when the request lacks the fields that materially change the result.

Required before generation:

- Main title or topic.
- Usage.
- Ratio, unless the platform implies one clearly and the user accepts agent judgment.

Ask concise questions when missing information affects the result:

- If usage is missing, ask for the target format.
- If ratio is missing, ask for the canvas ratio.
- If the topic is broad, ask for audience or business context.

Do not ask about optional fields if they would not change the design. Subtitle and banned elements can be empty.

## 2. Visual Brief

Before generating, form a visual brief internally:

```json
{
  "title_full": "",
  "subtitle": "",
  "usage": "",
  "ratio": "",
  "language": "",
  "audience_context": "",
  "core_word": "",
  "title_system": {
    "full_title": "",
    "hero_word": "",
    "tags": [],
    "short_judgment": ""
  },
  "main_metaphor": "",
  "type_reconstruction": "",
  "visual_system": "Editorial Magazine | Swiss Consulting",
  "palette": "",
  "layout_skeleton": "",
  "composition_model": "",
  "anchor_words": [],
  "avoid": [],
  "qa_checks": []
}
```

The brief is not user-facing unless the user asks to see it.

## 3. Card Design Operating Rules

Use these rules before any metaphor or module decision:

- One card, one soul: every card needs one memorable judgment sentence.
- Layout first: choose a skeleton before placing text.
- Locked palette: use one curated palette; never invent color mixes in the moment.
- Big type is not loud type: as font size increases, weight must decrease.
- Typography must breathe: title line-height >= 1.08, body line-height >= 1.35.
- No hidden text: captions, bottom bars, metaphors, and overlays must never cover type.
- No card soup: do not put cards inside cards unless the card is a repeated item inside a controlled grid.
- White space is content: leave large quiet fields, especially around the hero word.
- If the page feels merely correct, it is not done; add a point of view, tension, or editorial rhythm.

## 4. Visual Systems

### Editorial Magazine

Best for narrative, culture, organization, trend, and point-of-view content.

- Use one dominant quote or thesis.
- Use asymmetry, generous margins, small editorial metadata, and paper texture.
- Chinese can use a refined serif/sans mix when available; otherwise use lighter modern sans.
- Keep modules minimal; let the headline and negative space carry the mood.
- Failure mode: lifestyle poster with no business structure.

### Swiss Consulting

Best for analysis, product, technology, frameworks, methods, and systems.

- Use grid, hairline rules, strong type contrast, and one anchor color.
- Use sharp rectangles and precise alignment, but avoid looking like a dashboard.
- Large labels must be lighter weight; small labels can be medium weight.
- Failure mode: generic consulting PPT with boxes and arrows.

## 5. Layout Skeletons

Choose one skeleton; do not improvise from scratch.

### Hero Thesis Card

- Top metadata line.
- Huge core phrase.
- One short thesis sentence.
- One quiet metaphor mark.
- Bottom source/action line.

Use for covers and article idea cards.

### Magazine Feature Card

- Editorial masthead.
- Large title occupying 45-60% of the canvas.
- One side rail with 2-3 anchors.
- One strong closing line.

Use for reflective, cultural, or organizational topics.

### Swiss Mechanism Card

- Top title.
- Central mechanism graphic.
- Three supporting modules max.
- Bottom implication.

Use for systems, workflows, and business mechanisms.

### Split Tension Card

- Left: old logic.
- Right: new logic.
- Center: fracture, threshold, or data-flow mark.
- Bottom: what changes.

Use for transitions and paradigm shifts.

### Matrix Spotlight Card

- Two axes.
- One highlighted zone.
- Three labels max outside the zone.
- One conclusion line.

Use only when comparison or positioning is the main story.

### Flow Ribbon Card

- One flowing band across the card.
- 3-5 stations max.
- Labels sit above or below the band, not inside crowded boxes.

Use for process, pipeline, data flow, and operating model.

## 6. Scenario Playbooks

### Quick Social Cover

- Confirm topic, usage, and ratio.
- Keep one core word, one metaphor, one short judgment.
- Avoid full analytical breakdown.
- Generate directly when fields are clear.

### Business Report Or PPT Cover

- Treat as high-stakes.
- Build the full visual brief before generation.
- Preserve exact title and terminology.
- Prefer restraint, white space, thin line systems, and boardroom-ready hierarchy.
- If the direction is uncertain, ask the user to confirm the visual brief before generation.

### Infographic Or Consulting Analysis Page

- Do not start from decoration.
- Define the analytical path first: problem to answer, variables, mechanism, result.
- Compress to 2-4 major information groups when the output is a social card.
- Let the chosen metaphor organize modules, not compete with them.
- If it becomes a dense dashboard, switch to a card skeleton and remove detail.

### Flowchart Or Methodology Diagram

- Respect the requested structure first.
- Use metaphor as the visual language of the flow, not a replacement for the flow.
- Keep each step short and parallel in wording.

### Matrix Diagram

- If the user asks for a matrix, use a matrix.
- The main metaphor can be matrix; do not switch to coordinates unless the axes are strategic positioning.
- Define two dimensions and one recommendation zone.

## 7. Metaphor Design Grammar

Use one main metaphor only.

## 7A. Typography Reconstruction

The original prompt's strongest execution rule is that typography must become part of the business structure. Do not reduce this to "make the title bigger".

Available reconstruction moves:

- Stretch
- Compress
- Cut
- Hollow out
- Offset
- Layer
- Modularize
- Frame
- Path-shape
- Converge
- Stair-step
- Matrix-shape
- Architect
- Data-shape
- Chart-shape
- Spatialize

Choose one or two moves only. Too many reconstruction moves make the card look noisy.

Semantic mapping:

- Growth: expansion, rising, flywheel, compounding.
- Conversion: convergence, filtering, funnel, path.
- Strategy: path, coordinate, fork, decision.
- System: modules, links, nodes, architecture.
- Risk: threshold, defense line, fault line, grading.
- Market: coordinate, window, zones, competitive landscape.
- Value: ladder, scale, container, exchange.
- Efficiency: compression, acceleration, flow, automation.
- Opportunity: opening, window, breakthrough point, growth channel.
- Organization: hierarchy, reorganization, collaboration network, governance.

Typography-metaphor fusion patterns:

- Business graphic passes through letterforms.
- Path line enters the title's internal space.
- Funnel sits in the negative space of the hero word.
- Matrix grid becomes the skeleton of the title.
- Staircase becomes the base of the title.
- Data flow exits from the word.
- Fault line cuts the word.
- Node network connects strokes.
- Coordinate system is embedded into the title.
- The word becomes the business structure itself.

Failure modes:

- Ordinary title with an icon beside it.
- Ordinary title with a separate chart below it.
- Abstract background decoration unrelated to the title.
- Text and metaphor do not affect each other.

### 漏斗

- Cover: make the hero word converge through negative space; use one entry edge and one output edge.
- Infographic: show input, filter, conversion, output; auxiliary modules explain variables, not extra metaphors.
- Failure mode: full sales funnel on a cover; too many layers.

### 路径

- Cover: route line enters, crosses, or exits the hero word.
- Infographic: one route with stages, milestones, decisions, and destination.
- Failure mode: generic roadmap with decorative arrows.

### 阶梯

- Cover: hero word sits on or becomes ascending steps.
- Infographic: levels, maturity, pricing, capability, or value progression.
- Failure mode: noisy bar chart or motivational staircase.

### 矩阵

- Cover: grid or quadrant acts as the typographic skeleton.
- Infographic: two decision dimensions, options, priority zone, or competitive map.
- Failure mode: every item becomes equal; no clear recommendation.

### 坐标

- Cover: axes cut through the hero word with one marked strategic position.
- Infographic: market map, risk-return, opportunity space, or strategic position.
- Failure mode: decorative axes without analytical labels.

### 飞轮

- Cover: one circular motion around the core word; avoid complex loops.
- Infographic: inputs, drivers, feedback, compounding result.
- Failure mode: generic circular arrows with no causality.

### 节点网络

- Cover: nodes connect strokes or edges of the hero word.
- Infographic: roles, resources, systems, connections, dependencies.
- Failure mode: random network decoration.

### 数据流

- Cover: stream enters, passes through, or exits the hero word.
- Infographic: input, processing, automation, output, feedback.
- Failure mode: tech wallpaper or abstract data rain.

### 门槛

- Cover: threshold line divides before/after or pass/fail.
- Infographic: gate criteria, review points, decision standards, next stages.
- Failure mode: looks like a wall with no decision logic.

### 窗口

- Cover: open negative-space window inside or beside the hero word.
- Infographic: timing, entry conditions, opportunity boundary, action path.
- Failure mode: literal window illustration.

### 防线

- Cover: thin defensive boundaries structure the title.
- Infographic: risk source, control layer, governance owner, residual risk.
- Failure mode: shield icon or security cliché.

### 断层

- Cover: controlled break in the title shows old/new, before/after, gap.
- Infographic: structural shift, causes, consequences, opportunity.
- Failure mode: messy broken text that hurts readability.

### 容器

- Cover: word becomes a vessel, pool, or bounded field.
- Infographic: resources in, value stored, output, leakage, boundary.
- Failure mode: generic box diagram.

### 罗盘

- Cover: directional ticks and one clear bearing integrate with the hero word.
- Infographic: strategic choices, principles, tradeoffs, recommended direction.
- Failure mode: compass icon pasted next to a title.

### 建筑结构

- Cover: word becomes facade, foundation, column, or structural frame.
- Infographic: foundation, pillars, governance layer, roof outcome.
- Failure mode: real estate or architecture poster mood.

## 8. Composition Models

### Cover

Use this structure when the output is a cover:

- Top bar: full title, category tag, year, issue number.
- Center: reconstructed hero word and one metaphor.
- Edge anchors: 2-3 terms maximum.
- Bottom: one short judgment, 12-22 Chinese characters when Chinese.

The cover is successful if it remains strong after removing 70% of secondary marks.

### Infographic

Use this structure when the output is analytical, but still keep it card-like:

- Top title and subtitle.
- Central analytical structure.
- Two to four supporting information groups.
- One bottom conclusion or action.
- Tiny legend, numbering, and guide lines.

The infographic is successful if the reading path is obvious in five seconds.

## 9. Rendering Discipline

For text-heavy Chinese cards, prefer a single HTML file rendered to PNG with a browser. HTML/CSS gives better control over line height, font fallback, safe areas, and responsive text than hand-positioned SVG.

Use SVG only for simple vector marks or when every text box has been manually checked. Do not build complex Chinese layouts by absolute SVG coordinates unless there is a strong reason.

Before delivery:

- Render the final image.
- Inspect the actual PNG.
- Check dimensions.
- Check text clipping, overlap, and bottom-bar coverage.
- Revise once if typography or spacing feels crude.

## 10. Prompt Assembly

When calling a host image-generation tool, assemble the prompt from the visual brief:

- State the exact output type and ratio.
- Preserve the exact full title and core word.
- Describe the single metaphor and how it merges with typography.
- Specify composition zones.
- Specify palette, typography, line system, texture, and density.
- List strict negatives.
- Require clean, readable, non-garbled text.
- Require a refined card, not a dense infographic panel.

Do not ask the image model to invent the title, business concept, or module labels.

## 11. QA And Revision

Reject or revise if:

- More than one metaphor competes for attention.
- The image uses decorative business clichés.
- Text is misspelled, garbled, or unreadable.
- The layout looks like a generic PowerPoint template.
- Cover density exceeds the limit.
- Infographic has more than six major modules.
- The metaphor is only beside the title, not integrated with it.
- Color becomes neon, purple-blue sci-fi, or saturated advertising style.
- Font looks crude, heavy, or browser-default.
- Text touches edges, overlaps, or is covered by bars/graphics.
- The result lacks a memorable thesis or emotional point of view.

When text accuracy is poor, reduce text volume and regenerate with fewer labels.
