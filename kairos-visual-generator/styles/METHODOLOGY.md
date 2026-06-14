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

## Golden Example Convention

Golden examples serve as **rendering templates** for each style. They are not just samples — they are the reference implementation that proves the style works.

### Structure

Each golden example lives in `goldens/<style-name>/` and contains:

| File | Required | Description |
|------|----------|-------------|
| `<name>.html` | Yes | The HTML/CSS template. This IS the rendering logic. |
| `brief.json` | Yes | The Visual Brief that produced this output. |
| `meta.json` | Yes | Version metadata (style_id, theme_id, skeleton_id, ratio). |

### Rules

1. **HTML is the template**: The HTML file defines the exact layout, spacing, and typography. New cards of this style should follow this template.
2. **One golden per skeleton**: Each layout skeleton in `composition.json` should have at least one golden example.
3. **Content must be realistic**: Use real or realistic content, not placeholder text.
4. **Aspect ratio must match real-world**: Use `CONTENT_NATURAL_RATIOS` from `platform.py` to determine the correct ratio.
5. **Render at 3x quality**: Use `device_scale_factor=3` for Retina-quality PNGs.

### Golden Example QA Checklist

Before committing a golden example, verify:

- [ ] HTML opens correctly in browser
- [ ] No text overlap (check absolute-positioned elements)
- [ ] All elements aligned (bottom elements at same vertical position)
- [ ] Spacing follows 8px grid system
- [ ] Content fills the canvas without excessive whitespace
- [ ] PNG rendered at 3x quality
- [ ] brief.json matches the actual content
- [ ] meta.json has correct ratio

## First Principles

These principles should guide all style development and card generation.

### Principle 1: Content Determines Form

The canvas size should be determined by the content volume, not the other way around.

**Process**:
1. List all fields to display
2. Estimate visual weight of each field (font-size × characters)
3. Calculate total visual area
4. Select the smallest canvas ratio from `CONTENT_NATURAL_RATIOS` that can hold the content
5. If content doesn't fit → reduce content, don't enlarge canvas

### Principle 2: Visual Hierarchy = Information Hierarchy

All elements treated equally → visual chaos. Elements must have clear priority levels.

**Process**:
1. Define 3-4 information levels
2. Assign fixed font-size ranges and spacing rules per level
3. Same-level elements use the same spacing
4. Visual weight = font-size × color contrast × spatial proportion

### Principle 3: Alignment Expresses Relationship

Alignment is not about centering relative to the container — it's about centering relative to the content.

**Vertical centering**:
- Wrong: `align-items: center` on a variable-height container
- Right: Fixed-height wrapper with `align-items: center`, or `top: 50%; transform: translateY(-50%)`

**Bottom alignment**:
- Two sections with same-level bottom elements → same `padding-bottom` + `margin-top: auto`

### Principle 4: Quality is Verifiable

Text overlap, misalignment, and blurriness are objectively verifiable issues. Quality should be checked systematically, not by feel.

**Verification layers**:
1. **Structural** (lightweight): Check CSS rules for potential overlaps, alignment consistency
2. **Rendered** (optional): Playwright-based visual checks

### Principle 5: Real-World Proportions

Different content types have natural proportions derived from real-world artifacts. Don't use a single ratio for everything.

**Examples**:
| Content Type | Natural Ratio | Real-World Reference |
|--------------|---------------|----------------------|
| Boarding pass | 3:1 | Airline boarding pass |
| Receipt | 1:2 | Thermal receipt paper |
| Magazine cover | 3:4 | Print magazine |
| X/Twitter header | 5:2 | Social media banner |
| Poster | 1:1 | Square poster |

### Principle 6: Spacing is Systematic

All spacing values should align to an 8px base unit. Use named tokens (`spacing-xs` through `spacing-2xl`) instead of arbitrary pixel values.

See `references/design_system.md` for the full spacing token system.
