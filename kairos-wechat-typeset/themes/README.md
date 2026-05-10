# Theme Extension Guide

Themes are developer-maintained design systems. Users select one registered built-in theme during the workflow, but they cannot provide custom colors, CSS, HTML templates, runtime theme files, or arbitrary theme paths.

## Add a Theme

1. Create `themes/<theme-id>/DESIGN.md`.
2. Create `themes/<theme-id>.json`.
3. Add the theme to `themes/registry.json`.
4. Render `fixtures/visual-matrix.md` with `--verify`.
5. Compare the output against the nearest `goldens/` reference.
6. Review mobile output at 390px and 430px.

## Required Files

- `DESIGN.md`: human-readable theme philosophy, fit, tokens, component rules, mobile rules, and quality gates.
- `<theme-id>.json`: deterministic visual philosophy, constraints, rhythm, components, and tokens consumed by `scripts/render.py`.
- `registry.json`: the only source of themes visible to users.

The high-level workflow reads this registry when asking the user which theme to use. Runtime art-direction overrides are not part of the public user workflow because each registered theme must remain stable and reproducible.

## Required Theme Contract

Each JSON theme must define:

- `philosophy`: `mood`, `density`, `rhythm`, and `hierarchy`.
- `constraints`: one accent color, highlight frequency limit, component variant limit, and forbidden visual moves.
- `art_direction`: deterministic defaults for spacing scale, emphasis mode, visual density, and section rhythm.
- `rhythm`: paragraph gap, heading top/bottom, quote breathing, and section break values.
- `components`: bounded component variants, maximum 3 per component.

## Theme Polishing Workflow

Theme quality comes from a repeatable design pass, not one-off CSS edits.

1. Define the theme thesis in `DESIGN.md`: audience, mood, typography, color limits, forbidden moves, and component language.
2. Decide whether the visual target is a normal Markdown block or a Kairos component. Markdown owns article semantics; components own body-safe magazine layout such as lead, pullquote, figure, soft-list, and closing-note.
3. Tune the deterministic tokens in `themes/<theme-id>.json`: fonts, ink, paper, one accent color, rhythm, shape, and component variants.
4. Render the shared visual matrix:

```bash
python3 scripts/render.py \
  --theme <theme-id> \
  --input fixtures/visual-matrix.md \
  --output /tmp/<theme-id>-visual-matrix.html \
  --verify
```

5. If tokens are not enough, add small theme-specific renderer branches for existing components only.
6. Promote the reviewed result into `goldens/<theme-id>-style.html`.
7. Re-run HTML verification and inspect 390px and 430px mobile previews.

Use the visual matrix to judge component completeness: H1, numeric H2, fallback headings, paragraph rhythm, inline emphasis, links, lists, quote, NOTE/TIP/WARNING, Kairos lead, pullquote, figure, soft-list, closing-note, image caption, code block, table fallback, divider, and escaped raw HTML.

Run the visual audit after every polish pass:

```bash
python3 scripts/audit_visual.py \
  --input goldens/<theme-id>-style.html
```

For themes with strict type or spacing rules, pass explicit gates:

```bash
python3 scripts/audit_visual.py \
  --input goldens/song-style.html \
  --allowed-font-size 16px \
  --allowed-font-size 18px \
  --max-margin-px 44
```

## Polish Heuristics

Use these checks before accepting a theme:

- Typography: decide the type scale first. Avoid accidental font-size drift from inline Latin, captions, code labels, table labels, list markers, or callout tags.
- Rhythm: inspect actual rendered margins, not just JSON tokens. Watch for stacked pauses such as divider bottom plus heading top, or quote margin plus inner padding.
- Lines: count visible borders. Repeated underlines, table field rules, image-caption rules, and decorative divider lines quickly make a mobile article feel noisy.
- Color: keep background fills rare. Prefer paper, ink, one accent, and subtle line color over multiple tinted surfaces.
- Components: each block should have a role. If quote, code, table, and callout all look like similar boxes, the theme is not specific enough.
- Platform boundary: WeChat body themes cannot control the article title, cover image, account header, menus, or external page chrome. Translate references into body-safe components instead of adding seals, free positioning, or cover-like decoration.
- Mobile first: judge density at phone width. A spacing system that feels elegant on desktop can become fragmented on WeChat mobile.

`song` is the reference example for an intentionally restrained theme: two font sizes, no gradients, minimal borders, compact mobile rhythm, and no decorative horizontal divider rules.

## Rules

- Keep the total WeChat article shape mobile-first and single-column.
- Keep all output styles inline.
- Do not add `<style>`, external CSS, classes, or JavaScript.
- Tables must remain stacked cards, not native wide tables.
- Accent color count is 1.
- Highlight frequency target is <= 8%.
- Gradients are forbidden in all themes unless a future theme explicitly documents a strong product reason and still passes WeChat compatibility review.
- High-density sections need breathing through a divider, quote, or list.
- Heading hierarchy may not skip levels.
- A theme is accepted only after representative rendering, verification, golden comparison, and mobile review pass.
