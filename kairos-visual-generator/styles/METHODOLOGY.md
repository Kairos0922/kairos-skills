# Visual Style Extension Methodology

Style extension in `kairos-visual-generator` is the process of adding a new visual system with its own design rules, composition patterns, and theme tokens.

## Style Contract

Every style must provide:

| File | Required | Description |
|------|----------|-------------|
| `DESIGN.md` | Yes | Visual DNA, color system, typography, grid, texture, anti-patterns |
| `composition.json` | Yes | Layout skeletons, density models, text reconstruction, metaphors, QA checklist |
| `themes/registry.json` | Yes | Theme index |
| `themes/*.json` | Yes | Theme tokens with `css_mapping` field |

## Fast Style Pipeline

1. Name the style from its strongest visual identity.
2. Write the one-sentence thesis:

   > This style expresses `<content types>` through `<visual principles>` while forbidding `<anti-patterns>`.

3. Define the visual DNA: color philosophy, structural elements, texture, density.
4. Write `DESIGN.md` before any code.
5. Create `composition.json` with layout skeletons and QA checklist.
6. Create at least 1 theme token file with `css_mapping`.
7. Register in `styles/registry.json`.
8. Add routing keywords to `SKILL.md`.
9. Create 1 golden example.
10. Run verification.

## Quality Bar

A new style is high quality only if it passes:

- **Identity Test**: a user can tell why this style exists from the output alone.
- **Token Test**: all visual attributes are locked in JSON tokens, no improvisation.
- **Composition Test**: at least 2 layout skeletons; if supporting infographics, must cover both cover and infographic.
- **Reproducibility Test**: same input + same theme = same output.
- **QA Test**: global + style-specific checklist passes.
- **Print Test**: output PNG at 100% zoom — text clarity, color block edges, grid alignment.
