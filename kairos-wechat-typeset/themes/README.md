# Theme Extension Guide

Themes are developer-maintained design systems. Users select one registered built-in theme during the workflow, but they cannot provide custom colors, CSS, HTML templates, runtime theme files, or arbitrary theme paths.

Themes implement the shared semantic component contract in [`../COMPONENTS.md`](../COMPONENTS.md). Expanding a theme should mean giving the same component matrix a deliberate visual treatment, not adding new user syntax or one-off decorative blocks.

Read [`METHODOLOGY.md`](METHODOLOGY.md) before adding or substantially polishing a theme. It captures the Song finalization process: visual reference translation, semantic component mapping, token contracts, fixture/golden promotion, browser QA, and validation gates.

## Add a Theme

1. Create `themes/<theme-id>/DESIGN.md`.
2. Create `themes/<theme-id>.json`.
3. Add the theme to `themes/registry.json`.
4. Render a real article fixture with `--verify`; for `song`, use `fixtures/song-style-system.md`.
5. Compare the output against the nearest `goldens/` reference.
6. Review mobile output at 390px and 430px.

## Required Files

- `DESIGN.md`: human-readable theme philosophy, fit, semantic component rules, mobile rules, and quality gates.
- `<theme-id>.json`: deterministic visual philosophy, constraints, rhythm, components, and tokens consumed by `scripts/render.py`.
- `registry.json`: the only source of themes visible to users.

The high-level workflow reads this registry when asking the user which theme to use. Runtime art-direction overrides are not part of the public user workflow because each registered theme must remain stable and reproducible.

## Required Theme Contract

Each JSON theme must define:

- `philosophy`: `mood`, `density`, `rhythm`, and `hierarchy`.
- `constraints`: one accent color, highlight frequency limit, component variant limit, and forbidden visual moves.
- `art_direction`: deterministic defaults for spacing scale, emphasis mode, visual density, and section rhythm.
- `rhythm`: paragraph gap, heading top/bottom, quote breathing, and section break values.
- `components`: bounded semantic component variants, maximum 3 per component.

## Theme Polishing Workflow

Theme quality comes from a repeatable design pass, not one-off CSS edits.

1. Define the theme thesis in `DESIGN.md`: audience, mood, typography, color limits, forbidden moves, component language, article type strategy, mobile rules, and quality gates.
2. Decide whether the visual target is a normal Markdown block or a Kairos semantic component. Markdown owns technical article structure; semantic components own body-safe magazine expression such as lead, insight, pullquote, figure, soft-list, and closing-note.
3. Tune the deterministic tokens in `themes/<theme-id>.json`: fonts, ink, paper, one accent color, rhythm, shape, and component variants.
4. Render the theme's real article fixture:

```bash
python3 scripts/render.py \
  --theme <theme-id> \
  --input fixtures/<theme-id>-style-system.md \
  --output /tmp/<theme-id>-article.html \
  --verify
```

5. If tokens are not enough, add small theme-specific renderer branches for existing components only.
6. Promote the reviewed result into `goldens/<theme-id>-style.html`.
7. Re-run HTML verification and inspect 390px and 430px mobile previews.

Use a realistic article fixture to judge component completeness: H1, numeric H2, fallback headings, paragraph rhythm, inline emphasis, links, lists, steps, quote, NOTE/TIP/WARNING, Kairos lead, insight, pullquote, figure, soft-list, closing-note, image caption, code block, faux table layout, divider, and escaped raw HTML.

`goldens/song-style.html` is rendered from `fixtures/song-style-system.md` so the Song reference stays close to its design-system master and article sample.

`goldens/wending-style.html` is rendered from `fixtures/wending-style-system.md` so the Wending reference stays aligned with the attached mobile component specification: 28px H1, 22px H2, 18px H3, 16px body text, 14px auxiliary/code text, dark code blocks, fine-line tables, 8px image radius, and shallow gray quote surfaces.

Run the visual audit after every polish pass:

```bash
python3 scripts/audit_visual.py \
  --input goldens/<theme-id>-style.html
```

For themes with strict type or spacing rules, pass explicit gates:

```bash
python3 scripts/audit_visual.py \
  --input goldens/song-style.html \
  --allowed-font-size 14px \
  --allowed-font-size 16px \
  --allowed-font-size 20px \
  --allowed-font-size 28px \
  --max-margin-px 48
```

## Polish Heuristics

Use these checks before accepting a theme:

- Typography: decide the type scale first. Avoid accidental font-size drift from inline Latin, captions, code labels, table labels, list markers, or callout tags.
- Rhythm: inspect actual rendered margins, not just JSON tokens. Watch for stacked pauses such as divider bottom plus heading top, or quote margin plus inner padding.
- Lines: count visible borders. Repeated underlines, table field rules, image-caption rules, and decorative divider lines quickly make a mobile article feel noisy.
- Color: keep background fills rare. Prefer paper, ink, one accent, and subtle line color over multiple tinted surfaces.
- Components: each block should have a role. If quote, code, table, and callout all look like similar boxes, the theme is not specific enough.
- Platform boundary: WeChat body themes cannot control the article title, cover image, account header, menus, or external page chrome. Translate references into body-safe components instead of adding seals, free positioning, or cover-like decoration.
- Alignment: measure table cells, task checkboxes, ordered markers, and unordered markers against their text when the component uses inline faux layout.
- Mobile first: judge density at phone width. A spacing system that feels elegant on desktop can become fragmented on WeChat mobile.

`song` is the reference example for an intentionally restrained theme: bounded type scale, no gradients, minimal borders, compact mobile rhythm, stable faux tables, aligned list/checklist markers, and no decorative horizontal divider noise.

## Rules

- Keep the total WeChat article shape mobile-first and single-column.
- Keep all output styles inline.
- Do not add `<style>`, external CSS, classes, or JavaScript.
- Tables must remain WeChat-mobile-safe faux layouts, not native wide tables.
- Accent color count is 1.
- Highlight frequency target is <= 8%.
- Gradients are forbidden in all themes unless a future theme explicitly documents a strong product reason and still passes WeChat compatibility review.
- High-density sections need breathing through a divider, quote, or list.
- Heading hierarchy may not skip levels.
- A theme is accepted only after representative rendering, verification, golden comparison, and mobile review pass.
