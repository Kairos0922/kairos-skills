# Theme Extension Methodology

Theme extension in `kairos-wechat-typeset` is not CSS authoring. It is the process of translating a visual reference into a deterministic WeChat semantic design system.

The Song finalization is the reference process: first define the editorial intent, then encode component semantics, tokens, renderer behavior, fixtures, goldens, and validation gates. A theme is accepted only when the result is reproducible across real article content and mobile WeChat constraints.

## Four-Theme Pattern

The current four themes show the reusable expansion pattern:

| Theme | Reference Translation | Primary Lever | Risk To Avoid |
| --- | --- | --- | --- |
| `song` | literary paper, ink, serif order | warm paper, serif hierarchy, restrained rules | drifting into decorative classical style |
| `wending` | calm white-paper component spec | serif weight, warm white, gray surfaces | becoming a generic card-heavy wellness theme |
| `tech` | blue mobile technology article | explicit blue hierarchy, dark code, light-blue panels | becoming a SaaS landing-page palette |
| `wisme` | strict black-white-red component spec | black typography, red short rules, gray grids | becoming a static design poster instead of article body |

The lesson is that a high-quality theme is not a color palette. It is a repeatable mapping from reference intent to the same body-safe component matrix. Fast theme creation comes from reusing the pipeline, not from skipping decisions.

## Fast Theme Pipeline

Use this sequence when adding a high-quality theme quickly:

1. Name the theme from the reference's strongest identity.
2. Write the one-sentence thesis:

   > This theme expresses `<article types>` through `<visual principles>` while forbidding `<visual anti-patterns>`.

3. Classify the reference into one of the existing implementation archetypes:

   - `paper-literary`: serif, warm paper, restrained lines. Start from `song`.
   - `quiet-spec`: white paper, gray surfaces, serif or calm sans. Start from `wending`.
   - `technical-explicit`: strong accent hierarchy, code-heavy, scan-first. Start from `tech`.
   - `component-spec`: strict black/gray grid, one red/brand accent, documentation tone. Start from `wisme`.

4. Extract only body-safe surfaces:

   - Keep: type scale, section heading mechanics, paragraph rhythm, quote shape, list markers, code block treatment, table style, image/caption relationship, highlight behavior.
   - Translate: cover composition, platform chrome, account badges, side panels, large design-canvas cards, decorative icons, and free positioning into principles.
   - Drop: anything that cannot survive WeChat inline HTML and single-column mobile reading.

5. Draft `themes/<theme-id>/DESIGN.md` before code. The design document must lock:

   - theme position and suitable article types
   - visual language and forbidden moves
   - hard token choices: H1, H2, H3, body, small text, code, accent, line, surface, radius
   - component rules for every shared block
   - mobile rules and quality gates

6. Copy the closest JSON theme and change tokens first. Do not touch the renderer until the token contract is clear.
7. Create one canonical fixture at `fixtures/<theme-id>-style-system.md` that covers the common WeChat body matrix.
8. Add only the renderer branches that tokens cannot express: usually H2, quote/pullquote, insight, table, task list, code, and figure caption.
9. Render directly to `goldens/<theme-id>-style.html` and treat that file as the acceptance artifact.
10. Update registry, README, and SKILL in the same change so the next agent can reproduce the theme. Run `python3 check.py` from the repo root to verify.

This pipeline should make the first useful version fast while keeping the quality ceiling high.

## Quality Bar From Four Themes

A new theme is high quality only if it passes these four tests:

- **Identity Test**: a reader can tell why this theme exists from H1, H2, quote, code, table, and insight alone.
- **Matrix Test**: every shared Markdown/Kairos component has a deliberate treatment, not just inherited defaults.
- **Restraint Test**: one accent color does most of the work; backgrounds, borders, and icons do not compete.
- **Reproducibility Test**: fixture, golden, docs, registry, validation commands, and renderer behavior all agree.

If a theme fails the Identity Test, sharpen typography, H2 mechanics, and quote/insight/table treatments before adding more decoration.

If a theme fails the Matrix Test, extend the renderer for existing components rather than adding new syntax.

If a theme fails the Restraint Test, remove surfaces before tuning colors.

If a theme fails the Reproducibility Test, fix docs and validation before polishing visuals.

## Theme Delivery Template

For a new theme named `<theme-id>`, the normal change set is:

```text
themes/<theme-id>.json
themes/<theme-id>/DESIGN.md
fixtures/<theme-id>-style-system.md
goldens/<theme-id>-style.html
themes/registry.json
scripts/render.py
README.md
SKILL.md
themes/README.md
```

Use the smallest possible renderer patch. In most cases, adding a theme means:

- shared token reuse for body, paragraph, code, image, and list basics
- one H2 branch for the reference's section-heading identity
- one table row/cell style when the grid treatment is theme-defining
- one insight or quote branch when emphasis treatment is theme-defining
- one task checkbox rule if checked/unchecked states must match the reference

Avoid broad rewrites to `render.py`. Add theme helpers near the closest existing theme branch and rerun `rg "<old-theme>|<theme-id>" scripts/render.py` to make sure the branch is intentional.

## Reference Extraction Checklist

When looking at a design image, extract decisions in this order:

1. **Article fit**: what kinds of WeChat articles should use it?
2. **Typography**: H1, H2, H3, body, small text, code sizes and weights.
3. **Hierarchy mechanics**: section numbers, rules, metadata, labels, and title alignment.
4. **Color economy**: paper/background, ink, muted text, line color, one accent, soft accent surface.
5. **Component signatures**: the 3-5 components that make the theme recognizable.
6. **Forbidden moves**: what would make the theme cheap, generic, or unfaithful?
7. **Mobile risks**: table density, code wrapping, heading line length, image/caption rhythm, stacked borders.

Do not start implementation until the extraction can be written as tokens and component rules.

## Core Thesis

Every theme must answer this sentence before implementation:

> This theme expresses `<article types>` through `<visual principles>` while forbidding `<visual anti-patterns>`.

Examples:

- Song expresses technical longform, methodology, humanities, lifestyle, and book reviews through paper warmth, restrained ink, fine lines, clear hierarchy, and compact mobile rhythm while forbidding decorative scenery, seals, gradients, heavy cards, and ad hoc CSS.

## Design-First Checkpoint

For any new theme or major theme polish, do not start by changing `render.py`.

1. Inspect the visual reference and identify what can safely exist inside the WeChat article body.
2. Separate reference mood from literal decoration. Background scenes, platform chrome, cover-like openings, icons, and free positioning usually become principles, not components.
3. Write or update `themes/<theme-id>/DESIGN.md` with theme position, visual language, tokens, component rules, article type strategy, mobile rules, and quality gates.
4. Ask for design confirmation when the task is taste-heavy or reference-driven.

Only after the design contract is clear should implementation begin.

## Semantic Translation

Translate references into the shared component matrix, not into one-off blocks.

Markdown owns technical article structure:

- Headings
- Paragraphs
- Ordered and unordered lists
- Task checklists
- Quotes and callouts
- Code and inline code
- Tables
- Images and links

Kairos semantic components own body-safe editorial expression:

- `:::lead`
- `:::insight`
- `:::pullquote`
- `:::figure`
- `:::soft-list`
- `:::closing-note`

If a visual target cannot be mapped to an existing Markdown element or Kairos component, first decide whether it is a real reusable semantic component. Do not add arbitrary syntax for a single reference image.

## Token Contract

Update `themes/<theme-id>.json` together with `DESIGN.md`.

Tokens must define:

- Typography scale and font families.
- Paper, ink, muted, line, surface, and one accent color.
- Rhythm for paragraphs, headings, quotes, and section breaks.
- Shape constraints such as radius and image radius.
- Article direction defaults such as density, emphasis mode, and section rhythm.
- Component variants, with at most three variants per component.

Token drift is a theme bug. If the rendered HTML introduces unexpected font sizes, background colors, border types, or spacing, either update the documented contract or fix the renderer.

## Renderer Rules

Renderer changes are allowed, but only as deterministic component implementations.

Use tokens first. Add theme-specific renderer branches only when tokens cannot express a reusable component behavior, such as:

- Song code blocks with line numbers.
- Song faux tables with stable mobile grid borders.
- Song task checklists with square states.
- Song quote and pullquote distinction.
- Theme-specific heading treatment.

Renderer branches must not:

- Generate article-specific CSS.
- Depend on private paths or runtime user theme files.
- Add `<style>`, classes, scripts, native wide tables, or arbitrary HTML.
- Make one component accidentally look like several unrelated components.

## Fixture Strategy

Each theme needs one canonical acceptance fixture. Avoid multiple competing fixture sources for the same golden.

The fixture should cover:

- H1, numeric H2, and fallback H3.
- Article byline or meta line, opening lead, FAQ, related reading, and closing note patterns common in WeChat articles.
- Paragraph rhythm and inline emphasis.
- Links, inline code, Latin text, and escaped raw HTML where relevant.
- Ordered, unordered, and task lists.
- Quotes, NOTE/TIP/WARNING callouts, lead, insight, pullquote, figure, soft-list, and closing-note.
- Plain images, figure images with captions, code block, divider, and table.

Song uses `fixtures/song-style-system.md` because it combines the design-system sample with representative article content. Future themes should use `fixtures/<theme-id>-style-system.md` or another single documented canonical source.

## Golden System

`goldens/<theme-id>-style.html` is the visual acceptance standard, not a runtime template.

A golden should be promoted only after:

- The design owner accepts the visible direction.
- The fixture covers the relevant component matrix.
- The output passes HTML verification.
- Mobile previews at 390px and 430px show no horizontal overflow.
- Component-specific alignment issues are measured, not guessed.

When a golden changes, update docs and validation commands so future agents can reproduce the path.

## Visual QA Heuristics

Use this checklist before declaring a theme done:

- Typography: every font size is intentional. Watch inline Latin, inline code, captions, table labels, line numbers, and list markers.
- Rhythm: inspect actual rendered margins. Avoid stacked pauses from divider + heading, quote margin + inner padding, or repeated section gaps.
- Lines: count visible borders. Repeated underlines, dense table rules, and decorative dividers quickly make mobile output noisy.
- Color: keep background fills rare. Prefer paper, ink, muted text, line color, and one accent.
- Component roles: quote, pullquote, callout, code, table, and insight should not all become the same box.
- Alignment: list markers, task boxes, table cells, and code line numbers must align visually with their text.
- Mobile: judge density at phone width, not desktop width.
- Platform boundary: never treat WeChat title, cover, account header, menus, or page chrome as theme surface.

## Validation Path

Run the checks that match the edited surface:

```bash
python3 -m py_compile scripts/render.py
python3 -m json.tool themes/<theme-id>.json
python3 -m json.tool themes/registry.json
python3 scripts/render.py --theme <theme-id> --input fixtures/<theme-id>-style-system.md --output goldens/<theme-id>-style.html --verify
python3 scripts/verify.py --input goldens/<theme-id>-style.html
python3 scripts/audit_visual.py --input goldens/<theme-id>-style.html
python3 scripts/typeset.py --check
```

For Song, keep the strict audit gate:

```bash
python3 scripts/audit_visual.py \
  --input goldens/song-style.html \
  --allowed-font-size 12px \
  --allowed-font-size 14px \
  --allowed-font-size 16px \
  --allowed-font-size 25px \
  --allowed-font-size 28px \
  --max-margin-px 48
```

Also verify mobile rendering at 390px and 430px. For alignment-sensitive components, measure element boxes in a browser:

- Table row widths and cell x/y/width values are stable.
- Task checkbox center and text center are aligned.
- Ordered and unordered marker centers align with text.
- Horizontal overflow is zero.

## Definition Of Done

A theme extension is done only when:

- `themes/<theme-id>/DESIGN.md` explains the theme thesis and component rules.
- `themes/<theme-id>.json` matches the design contract.
- `themes/registry.json` exposes the theme correctly.
- The renderer implements reusable component behavior, not ad hoc styling.
- The canonical fixture renders to the golden.
- HTML verify, visual audit, JSON checks, and mobile preview pass.
- README, SKILL, and validation docs are updated.
- Generated caches and temporary preview files are removed.

The final deliverable should make the next agent able to reproduce the theme without private context.
