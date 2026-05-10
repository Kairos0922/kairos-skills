# Theme Extension Guide

Themes are developer-maintained design systems. Users select one registered built-in theme during the workflow, but they cannot provide custom colors, CSS, HTML templates, runtime theme files, or arbitrary theme paths.

## Add a Theme

1. Create `themes/<theme-id>/DESIGN.md`.
2. Create `themes/<theme-id>.json`.
3. Add the theme to `themes/registry.json`.
4. Render representative developer-owned Markdown samples with `--verify`.
5. Review mobile output at 390px and 430px.

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

## Rules

- Keep the total WeChat article shape mobile-first and single-column.
- Keep all output styles inline.
- Do not add `<style>`, external CSS, classes, or JavaScript.
- Tables must remain stacked cards, not native wide tables.
- Accent color count is 1.
- Highlight frequency target is <= 8%.
- High-density sections need breathing through a divider, quote, or list.
- Heading hierarchy may not skip levels.
- A theme is accepted only after representative rendering, verification, golden comparison, and mobile review pass.
