# kairos-wechat-typeset Design Architecture

## Goal

`kairos-wechat-typeset` is a WeChat article typesetting skill for mobile-first editorial reading. It should make Markdown articles feel like electronic magazine pages with electronic-ink restraint: elegant, artistic, readable, and stable inside the WeChat editor.

V2 reframes the product as a deterministic editorial design system. The goal is not to let an LLM generate taste. The goal is to manually define taste through goldens, theme philosophy, rhythm rules, and bounded components, then reproduce it reliably.

## Core Split

- LLM handles uncertain editorial work: structure, rhythm, headings, emphasis, and whether a paragraph should become a quote, list, divider, or callout.
- The workflow asks whether the user wants layout optimization. If yes, an agent/LLM produces standards-compliant Markdown and scripts save/verify it as `layout.md`; if no, the current Markdown goes straight to rendering after safety verification.
- The workflow asks the user to choose one registered built-in theme before rendering. Users cannot provide theme files, colors, CSS, or templates.
- Semantic analysis emits importance, intent, density, and split hints.
- Art direction resolves theme philosophy into spacing scale, emphasis mode, density, and rhythm.
- Rhythm engine resolves spacing and breathing between blocks.
- Scripts handle deterministic work: Markdown parsing, theme lookup, layout resolving, inline-style HTML rendering, and validation.

## Theme Model

The theme system borrows the `DESIGN.md` idea:

- `themes/<theme-id>/DESIGN.md` is the human design contract.
- `themes/<theme-id>.json` is the deterministic render contract.
- `themes/registry.json` controls what users can choose.

Users cannot extend themes at runtime. Developers extend themes by adding files and registering them.

Runtime article-type, density, and tone controls are not part of the user workflow. Registered theme contracts define the stable visual behavior.

## Golden System

`goldens/song-style.html`, `goldens/mimo-style.html`, and `goldens/claude-style.html` are the highest visual references. They are intentionally handmade or carefully curated. They are not runtime templates and should not be copied blindly by the renderer.

## Component Limits

Allowed editorial components are Paragraph, Insight, Quote, Summary, Divider, List, and CTA, with Code/Table/Heading as technical Markdown support components. Every component may define at most 3 variants per theme.

## Output Contract

User-facing assets are versioned outside the skill directory:

```text
~/.wechat-typeset/
  article-slug/
    v001/
      layout.md
      output.html
      meta.json
```

1. `layout.md` is optional and appears only when the user chooses layout optimization.
2. `output.html` is required and contains themed inline-style HTML.
3. `meta.json` records version, theme, input type, source path, title, layout optimization, layout mode, content hashes, and outputs.

Implement output paths with `Path.home() / ".wechat-typeset"` for macOS, Windows, and Linux compatibility.

## Quality Gates

- Full HTML output must contain no `<style>`, no `class=`, no external stylesheet.
- Fragment output must remain paste-friendly for WeChat.
- All block-level styles must be inline.
- Mobile reading is the priority over desktop flourish.
- Each registered theme must render representative samples with a distinct visual tone and remain aligned with its golden reference.
- Editorial verify must reject skipped heading hierarchy, too many consecutive long paragraphs, too many consecutive emphasis blocks, and high-density sections with no breathing point.
- Markdown safety verify must reject raw HTML, style/class attributes, and scripts for every input.
- Layout contract verify must reject excessive highlighting, deep headings, and overlong paragraphs for generated `layout.md`.
