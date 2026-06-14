# Consulting Visual Card Design System

This reference is the design system for `kairos-visual-generator`. It turns "make it refined" into concrete choices: visual system, theme preset, typography, grid, layout skeleton, and render QA.

Use it before writing any HTML/CSS or image prompt.

## 1. Design System Contract

Every card must lock these decisions before composition:

- `visual_system`: `Editorial Magazine` or `Swiss Consulting`.
- `theme_preset`: one preset from this file. Do not invent custom hex colors.
- `layout_skeleton`: one skeleton from this file. Do not improvise from a blank canvas.
- `type_scale`: one scale from this file based on canvas ratio.
- `safe_area`: fixed margins and no-text zones.
- `content_density`: cover, light card, standard infographic, or deep analysis card.
- `render_path`: HTML/CSS first for text-heavy Chinese cards; image generation only for background/illustration assets.

If a visual choice is not in this file, do not use it unless the user explicitly asks for an experiment.

Reference model: this system follows the same product logic as high-quality card/deck skills: fewer knobs, named themes, named layouts, HTML/CSS text rendering, browser preview, and visual QA. The goal is not to describe taste, but to prevent bad taste from entering the output path.

## 2. Theme Presets

### Editorial Magazine Themes

Use for narrative, culture, organization, reflective analysis, people, and article idea cards.

| Preset | Colors | Best for |
| --- | --- | --- |
| `Ink Classic` | `#0a0a0b`, `#f1efea`, `#6f767d` | Default, business ideas, serious essays |
| `Indigo Porcelain` | `#0a1f3d`, `#f1f3f5`, `#8a96a3` | AI, research, technology, knowledge cards |
| `Forest Ink` | `#1a2e1f`, `#f5f1e8`, `#8a7f68` | Organization, sustainability, long-termism |
| `Kraft Paper` | `#2a1e13`, `#eedfc7`, `#9b7b55` | History, reading, humanistic topics |
| `Dune` | `#1f1a14`, `#f0e6d2`, `#b79b6f` | Design, creativity, art, gallery mood |
| `Midnight Ink` | `#0e0d0c`, `#ece2cf`, `#d4a04a` | Dark cinematic topics, high-contrast covers |
| `Graphite Red` | `#181818`, `#f3f0ea`, `#b33a2e` | Risk, governance, sharp judgment |
| `Olive Editorial` | `#23301f`, `#f2ecdf`, `#8d9374` | Culture, institutions, slow strategy |
| `Kami Paper` | `#191813`, `#f5f4ed`, `#6f6a5f`, `#1947a3` | Print-like Chinese cards, elegant long-form synthesis |

### Swiss Consulting Themes

Use for methods, frameworks, product analysis, AI tools, operating models, metrics, and diagrams.

| Preset | Anchor | Best for |
| --- | --- | --- |
| `IKB` | `#002FA7` | Default Swiss, AI product, methodology |
| `Lemon` | `#FFD500` | Youth, retail, sports, consumer |
| `Lemon Green` | `#C5E803` | Health, ecology, Gen Z, green brands |
| `Safety Orange` | `#FF6B35` | Risk, warning, industry, news, urgency |

Rules:

- One card uses one preset only.
- Accent color may cover at most 8% of the canvas.
- Do not use purple-blue sci-fi gradients.
- CSS must expose colors as variables: `--ink`, `--paper`, `--muted`, `--accent`, `--line`.
- The preset name must be visible in the internal visual brief.
- Do not add a second accent for charts, badges, arrows, or footers.
- If a chart needs multiple series, use line style, opacity, labels, or position before adding color.
- Kami-inspired cards use warm paper and ink-blue sparingly: accent should stay below 5% of the canvas and never become a blue UI theme.

## 3. Typography System

Use these font stacks. Do not use one generic Chinese stack for every text layer.

```css
--font-display-zh: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Source Han Sans SC", sans-serif;
--font-text-zh: "Noto Sans SC", -apple-system, BlinkMacSystemFont, "PingFang SC", "Source Han Sans SC", sans-serif;
--font-en: "Inter", "Helvetica Neue", Helvetica, Arial, sans-serif;
--font-serif: "Noto Serif SC", "Songti SC", "Source Han Serif SC", Georgia, serif;
```

Font recipes:

| Recipe | Display | Thesis / module title | Body | Best for |
| --- | --- | --- | --- | --- |
| `Swiss Sans` | `--font-display-zh`, 500-580 | `--font-display-zh`, 540-620 | `--font-text-zh`, 390-460 | AI, product, consulting analysis |
| `Editorial Serif` | `--font-serif`, 560-680 | `--font-display-zh`, 500-600 | `--font-text-zh`, 380-450 | magazine covers, culture, institutions |
| `Hybrid Report` | `--font-display-zh`, 520-600 | `--font-serif`, 520-620 | `--font-text-zh`, 390-460 | report covers with a refined literary tone |
| `Kami Editorial` | `--font-serif`, 500-620 | `--font-serif`, 500-600 | `--font-text-zh`, 380-430 | warm paper cards, Chinese article synthesis, print-like reports |

Selection:

- Swiss Consulting defaults to `Swiss Sans`.
- Editorial Magazine defaults to `Editorial Serif` unless the topic is highly technical.
- Long Chinese article synthesis or high-end card reports may use `Kami Editorial`.
- AI / engineering / product information cards should use `Swiss Sans`; do not use heavy display fonts.
- If Chinese display text feels clumsy, first reduce weight by 40-80 and increase line-height slightly before changing size.
- Never use synthetic bold for serif Chinese. If the serif looks weak, increase size or contrast, not weight.

Typography roles:

- `display`: the memorable word or phrase. Editorial may use `--font-serif` for literary authority; Swiss should use `--font-display-zh` or `--font-en`.
- `headline`: the thesis sentence. It must support the display word, not repeat it.
- `section`: short module labels. Use only when the card has real structure.
- `body`: explanation or insight. Keep it short; never let body text become the visual center.
- `caption`: metadata, labels, source notes, small coordinates, numbering.

Kami-inspired typography rhythm:

- Use one serif-led hierarchy for the hero and thesis, then keep body text calm and light.
- Prefer 500-600 serif display weight over thick sans-serif hero type for reflective business writing.
- Keep English metadata small, widely tracked, and quiet; do not let all-caps labels compete with Chinese headings.
- Avoid equal-weight Chinese blocks. At least three visible text tones are required: hero, module title, body/caption.

CSS token blueprint:

```css
:root {
  --ink: #0a0a0b;
  --paper: #f1efea;
  --muted: #6f767d;
  --accent: #002FA7;
  --line: color-mix(in srgb, var(--ink) 16%, transparent);
  --font-display-zh: "Noto Sans SC", "PingFang SC", "Hiragino Sans GB", "Source Han Sans SC", sans-serif;
  --font-text-zh: "Noto Sans SC", -apple-system, BlinkMacSystemFont, "PingFang SC", "Source Han Sans SC", sans-serif;
  --font-en: "Inter", "Helvetica Neue", Helvetica, Arial, sans-serif;
  --font-serif: "Noto Serif SC", "Songti SC", "Source Han Serif SC", Georgia, serif;
}
```

### Font Loading

咨询卡片通过浏览器渲染后截图，Web 字体会正常加载。在生成的 HTML `<head>` 中加入字体加载声明：

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-sans-sc/index.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/noto-serif-sc/index.css" />
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/inter/index.css" />
```

如果生成 Editorial 风格卡片（衬线为主），额外加载：

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@fontsource/playfair-display/index.css" />
```

加载字体后再截图，确保所有设备上渲染一致。如果字体加载失败，回退到系统字体（PingFang SC / Songti SC）。

### 4:5 Card Scale, 1080 x 1350

| Token | Size | Weight | Line height | Use |
| --- | ---: | ---: | ---: | --- |
| `display` | 76-96 | 520-620 | 1.04-1.12 | Main hero word |
| `headline` | 42-56 | 540-650 | 1.12-1.22 | Thesis / subtitle |
| `section` | 22-28 | 600-680 | 1.18-1.3 | Module titles |
| `body` | 19-24 | 380-480 | 1.38-1.58 | Body text |
| `caption` | 14-17 | 450-600 | 1.25-1.45 | Metadata, labels |

### 1:1 Card Scale, 1080 x 1080

| Token | Size | Weight | Line height |
| --- | ---: | ---: | ---: |
| `display` | 62-78 | 520-620 | 1.06-1.14 |
| `headline` | 34-46 | 540-650 | 1.14-1.24 |
| `section` | 20-25 | 600-680 | 1.2-1.32 |
| `body` | 18-22 | 380-480 | 1.38-1.56 |
| `caption` | 13-16 | 450-600 | 1.25-1.45 |

### 3:4 Vertical Scale, 1080 x 1440

| Token | Size | Weight | Line height |
| --- | ---: | ---: | ---: |
| `display` | 78-104 | 500-620 | 1.04-1.12 |
| `headline` | 40-54 | 520-640 | 1.12-1.24 |
| `section` | 22-28 | 580-660 | 1.18-1.3 |
| `body` | 19-24 | 380-480 | 1.4-1.58 |
| `caption` | 14-17 | 450-600 | 1.25-1.45 |

### 16:9 Slide Scale, 1600 x 900

| Token | Size | Weight | Line height |
| --- | ---: | ---: | ---: |
| `display` | 58-82 | 500-620 | 1.04-1.12 |
| `headline` | 30-44 | 520-640 | 1.12-1.24 |
| `section` | 18-24 | 580-660 | 1.18-1.3 |
| `body` | 15-20 | 380-480 | 1.38-1.56 |
| `caption` | 11-14 | 450-600 | 1.25-1.45 |

### 21:9 / 5:2 Wide Scale

| Token | Size | Weight | Line height |
| --- | ---: | ---: | ---: |
| `display` | 64-92 | 520-620 | 1.02-1.1 |
| `headline` | 30-44 | 540-650 | 1.12-1.22 |
| `body` | 17-21 | 380-480 | 1.35-1.5 |
| `caption` | 12-15 | 450-600 | 1.25-1.4 |

Typography rules:

- Big Chinese type must not be too black. If `font-size >= 56px`, keep `font-weight <= 600` for Swiss Sans and `<= 680` for serif display.
- Swiss labels can be uppercase English with letter spacing `0.08em-0.14em`.
- Do not use negative letter spacing.
- Do not fake refinement with thin unreadable type; body text must stay readable on mobile.
- If text feels crude, reduce weight before reducing size.
- Large Chinese text should usually fit in 1-3 lines. If it needs 4 lines, the title has not been reconstructed enough.
- Do not place Chinese display text on top of dense shapes, charts, or images.
- Avoid browser default bold. Always set explicit `font-weight`, `line-height`, and `max-width`.
- Do not use `font-weight: 700` or browser `bold` for large Chinese display type in consulting cards.
- Body text should normally sit at 390-460 weight. If the body looks dark or crowded, reduce weight before reducing information.
- Mixed Chinese/English titles need separate spans when possible: English can use `--font-en` at 520-650, Chinese should stay lighter.
- Kami-style body text should usually sit at 380-430 weight with line-height 1.45-1.62.
- Do not put thick borders around text modules in warm paper cards; use hairline separators, reserved whitespace, and subtle panels instead.

Density typography rule:

- Cover: display may dominate 45-60% of visual attention.
- Light Card: display may dominate 30-45%.
- Standard Infographic: display should dominate 18-30%; body/module content must carry real information.
- Deep Analysis Card: display is a header or anchor only; the main structure and content modules carry the page.

## 4. Grid And Spacing

### Safe Areas

| Ratio | Canvas | Outer margin | Inner grid | Bottom no-cover zone |
| --- | --- | ---: | --- | ---: |
| `4:5` | 1080 x 1350 | 72-96 | 12 columns, 24 gap | 96 |
| `3:4` | 1080 x 1440 | 80-104 | 12 columns, 24 gap | 104 |
| `1:1` | 1080 x 1080 | 64-84 | 12 columns, 20 gap | 80 |
| `5:2` | 1500 x 600 or 2100 x 840 | 56-80 | 16 columns, 20 gap | 56 |
| `16:9` | 1600 x 900 | 64-88 | 12 columns, 24 gap | 72 |

Spacing rhythm:

- Use an 8px base unit.
- Section gaps: 40, 56, 72, 96.
- Hairlines: 1px, never 2px unless used as a deliberate accent.
- No text block may touch an edge, footer, figure, or decorative mark.
- The hero area should usually occupy 40-60% of the card.
- A footer is a reserved zone, not an overlay. It must never sit above flowing text.
- If a visual metaphor crosses text, it must pass behind low-contrast negative space or through deliberate letter gaps, not over strokes needed for reading.
- Do not rely on a flexible `1fr` row to contain unknown Chinese copy. If a row contains body text, give it enough fixed/minmax height or shorten the copy.
- Footer conclusions must sit in their own reserved grid row after all body modules have ended. If the footer visually touches module text, reduce modules before reducing margins.
- Lines, borders, nodes, arrows, and metaphor marks need a text exclusion zone of at least 16px from any Chinese glyph bounding box and 12px from captions.
- A horizontal rule may align with the top or bottom of a text band, but must not visually cut through the x-height or baseline zone of adjacent text.
- If a module title wraps to two lines, increase the module height or reduce the number of modules; do not let body copy start too close under it.
- Text exclusion zones are mandatory for labels inside structures. A layer tag, axis label, or status chip must live in a reserved corner with at least 18px from the nearest title glyph.
- For serif Chinese titles, increase visual clearance around vertical rules to at least 22px because strokes and punctuation feel optically wider.

### Spacing Tokens

All spacing values should align to an 8px base unit. Use these named tokens instead of arbitrary pixel values:

| Token | Value | Use |
| --- | ---: | --- |
| `spacing-2xs` | 2px | Micro gaps (between icon and label) |
| `spacing-xs` | 4px | Tight gaps (between related items) |
| `spacing-sm` | 8px | Small gaps (between same-level elements) |
| `spacing-md` | 16px | Medium gaps (between sections) |
| `spacing-lg` | 24px | Large gaps (between major blocks) |
| `spacing-xl` | 32px | Extra large gaps (hero to content) |
| `spacing-2xl` | 48px | Maximum gaps (top/bottom margins) |

Rules:
- All spacing values must be multiples of 8px (except `spacing-2xs` at 2px and `spacing-xs` at 4px).
- Same-level elements use the same spacing token.
- Bottom alignment: use `margin-top: auto` on footer elements in flex containers.
- Vertical centering: use a fixed-height wrapper with `align-items: center`, not just `align-items: center` on a variable-height container.


Layout rules from social-card practice:

- Start by placing the largest text block and safe area, not by drawing modules.
- Use one dominant alignment axis. Mixed left/center/right alignment usually looks amateur.
- Keep at least one clear empty region of 15-25% canvas area.
- Make every decorative line terminate on a grid edge, a text edge, or a metaphor node.
- Do not create more than three horizontal bands on covers or five on structure cards.

Content density rules:

- `Cover`: 1 visual thesis, 2-3 anchors, 1 conclusion.
- `Light Card`: 3-4 content atoms, each with one concrete phrase or data point.
- `Standard Infographic`: 4-6 content atoms grouped into 3-5 modules, plus one central mechanism.
- `Deep Analysis Card`: 6-10 content atoms grouped into 5-7 modules or a matrix/flow with annotations.
- Do not call a card an infographic if it has fewer than 4 concrete content atoms.
- Do not invent filler content. If the source is thin, ask for context or make a cover instead of a fake infographic.
- High density does not mean long sentences. Compress each content atom before reducing spacing.
- A dense 4:5 card should usually use 45-75 Chinese characters per module at most, including title and body.
- If 6 modules plus metrics do not fit, split into primary modules and secondary evidence; do not force all modules into equal boxes.

## 5. Layout Skeletons

Choose one skeleton per card.

### `E01 Hero Thesis`

- Top metadata line.
- Large hero phrase.
- One thesis sentence.
- Sparse metaphor mark.
- Bottom source/action line.
- Use `display` at 50-58% of canvas width, with the thesis no wider than 62% of the canvas.

Best for article insights, thought leadership, and covers.

### `E02 Magazine Feature`

- Editorial masthead.
- Large title occupying 45-60% of canvas.
- Side rail with 2-3 anchors.
- One strong closing line.
- Use serif display only if the topic benefits from literary or institutional weight.

Best for culture, organization, people, and long-form essays.

### `E03 Split Tension`

- Left old logic.
- Right new logic.
- Center fracture, threshold, or data-flow mark.
- Bottom implication.
- Keep both sides asymmetric: one side can be quieter, smaller, or more fragmented.

Best for paradigm shifts and before/after topics.

### `S01 Swiss Mechanism`

- Top title and metadata.
- One central mechanism graphic.
- Three to five supporting modules depending on content density.
- Bottom implication.
- The mechanism should occupy at least 35% of canvas area; supporting modules must not compete with it.
- For 6 or more content atoms, use nested hierarchy: 3 primary modules plus secondary labels, or switch to `S07 Annotated Field` / `S08 Evidence Ladder`.

Best for systems, operating models, and methods.

### `S02 Flow Ribbon`

- One flowing band or line.
- 4-6 stations for a standard infographic; 3 stations only for a light card.
- Labels above/below the band, not inside cramped boxes.
- One outcome at the end.
- Stations should use numbers or short verbs, not paragraph labels.

Best for process, path, data flow, and transformation.

### `S03 Matrix Spotlight`

- Two axes.
- One highlighted zone.
- Four quadrants or zones may be labeled if the user asked for a matrix.
- One recommendation line.
- Axis labels must be shorter than 8 Chinese characters or 2 English words.

Best for positioning, prioritization, and choices.

### `S04 KPI Editorial`

- One hero metric or contrast.
- Two to three supporting facts.
- Editorial note or implication.
- Use only when the card has real numbers; do not invent metrics for visual effect.

Best for data-backed but still card-like content.

### `S05 Executive Ladder`

- One vertical or diagonal ladder.
- 3-5 levels max.
- Each level has one short capability, value, or maturity label.
- One top-level destination statement.

Best for maturity, pricing, capability progression, and value upgrade.

### `S06 Architecture Stack`

- One structural base, pillar, or stack.
- 3-5 layers max.
- Bottom layer is foundation, top layer is result.
- Side annotations explain constraints or governance.

Best for operating models, governance frameworks, organization, and technology architecture.

### `S07 Annotated Field`

- One open field or map.
- 4-6 annotated regions.
- Each region has a short label and one specific implication.
- Use when the topic is a report/article synthesis with several distinct insights that do not form a strict process.

Best for article summaries, market views, research notes, and strategic memos.

### `S08 Evidence Ladder`

- One thesis at top.
- 3-5 evidence bands below.
- Each band pairs one source fact or observation with one implication.
- Final band becomes the recommended action or conclusion.

Best for transforming long-form articles into dense but readable insight cards.

## 6. Component Rules

- Prefer text, line, grid, shape, and negative space over icons.
- Cards inside cards are usually forbidden. Use panels only when they are repeated units inside a controlled grid.
- Use one figure metaphor, not decorative background shapes.
- Bottom bars must never cover content; use separated footer zones instead.
- Page numbers and metadata are small, aligned, and quiet.
- If using images, apply overlay masks and keep text off faces or subject centers.
- Rounded cards, drop shadows, glassmorphism, and floating badges are forbidden unless the user explicitly asks for a non-consulting style.
- Icons are optional and should be tiny. Never use business people, handshake icons, robot heads, or cartoon characters.
- For information graphics, modules must be named by business function, not generic labels like "Part 1" unless numbering itself is the structure.
- Each information module needs at least one concrete content atom: actor, mechanism, variable, evidence, trade-off, or action.
- Decorative lines and nodes must not overlap, touch, or visually slice through text. If a line is near text, add padding or move the line to a grid boundary.
- Module bodies must have a reserved bottom padding of at least 20px before the next rule, axis, or band.
- Never let a rule line become the visual baseline of body copy. If the last line of body text is closer than 16px to a rule, the layout fails QA.

## 7. HTML/CSS Rendering Rules

Text-heavy cards should be single-file HTML rendered to PNG.

HTML contract:

- One root `.card` with fixed width/height.
- CSS variables for theme.
- Classes for type tokens: `.display`, `.headline`, `.body`, `.caption`.
- CSS Grid or flex for structure; avoid absolute positioning for large text blocks.
- Absolute positioning is allowed for quiet decorative marks only.
- Every text block needs a `max-width`.
- Use `box-sizing: border-box` globally.
- Use `overflow: hidden` only on the root card or decorative marks; never hide overflowing text to pass QA.
- Prefer `text-wrap: balance` for large headings when available, but still manually inspect the PNG.
- For grid rows that contain variable Chinese copy, use `minmax(content-height, auto)` or fixed row budgets; never let copy overflow into the next visual band.

Render QA:

- Check actual PNG dimensions.
- Inspect the rendered PNG visually.
- Check that no text is clipped, hidden, or overlapped.
- Check that no rule, axis, node, arrow, chart, or decorative mark touches text.
- Check that module body text has visible breathing room above and below; no text should look pinned between two rules.
- Check that each horizontal band either contains content or intentional white space.
- Check large text weight and line-height against this file.
- Run a thumbnail test: at 25% size, the display word and main structure must still be recognizable.
- Run a squint test: the eye should see one dominant word/structure, one supporting statement, and one conclusion.
- If the screenshot looks like a dashboard, a slide template, or a poster with random decoration, revise the skeleton before tuning colors.
- If the screenshot looks too empty for an infographic, revise the content architecture before enlarging typography.

## 8. Common Failure Modes

- Looks like a dashboard instead of a card.
- Too many modules or all modules equal weight.
- Too few content atoms for an infographic.
- Generic module text that could apply to any topic.
- Big Chinese title is too heavy.
- Bottom action bar covers metrics or body text.
- Hairlines or chart marks cut through text.
- Layer tags or metadata visually collide with module titles.
- Thick borders make a warm editorial card feel boxed and heavy.
- Decorative metaphor competes with the thesis.
- Color system drifts beyond one preset.
- Layout starts from boxes instead of a skeleton.
- Generated image contains title/labels that should have been rendered as HTML text.
