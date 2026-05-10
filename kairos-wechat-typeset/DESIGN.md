# kairos-wechat-typeset Design Architecture

## Goal

`kairos-wechat-typeset` is a WeChat article typesetting skill for mobile-first editorial reading. It should make Markdown articles feel like electronic magazine pages with electronic-ink restraint: elegant, artistic, readable, and stable inside the WeChat editor.

V3 reframes the product as a semantic component system for WeChat article bodies. The goal is not to let an LLM generate taste. The goal is to manually define taste through semantic components, goldens, theme philosophy, rhythm rules, and bounded renderers, then reproduce it reliably.

The product goals are:

1. Stable output for WeChat public account articles.
2. Low-cost theme expansion through a shared component matrix.
3. High-quality, magazine-like articles through semantic expression, whitespace, and reading rhythm.

## Core Split

- LLM handles uncertain editorial work: structure, rhythm, headings, emphasis, and which semantic component is the best expression for a piece of content.
- The workflow asks whether the user wants layout optimization. If yes, an agent/LLM produces standards-compliant Markdown and scripts save/verify it as `layout.md`; if no, the current Markdown goes straight to rendering after safety verification.
- The workflow asks the user to choose one registered built-in theme before rendering. Users cannot provide theme files, colors, CSS, or templates.
- Semantic analysis emits importance, intent, density, and split hints.
- The semantic component contract maps Markdown and Kairos syntax into a bounded set of editorial components.
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

## Semantic Component Contract

`COMPONENTS.md` is the stable contract for Markdown elements and Kairos components. A semantic component is not a decorative block. It is the best editorial expression for a specific content role inside a WeChat article body.

The core component matrix includes:

```text
Heading
Paragraph
InlineCode
Strong
Emphasis
Strike
Highlight
List
Steps
Quote
Callout
CodeBlock
TableStack
Figure
Divider
Lead
Insight
Pullquote
SoftList
ClosingNote
```

Every registered theme should provide a deliberate treatment for this shared matrix. Theme expansion should mostly mean implementing the same components with a different philosophy, not inventing new syntax or adding one-off renderer branches.

## Component Limits

Allowed semantic components are Heading, Paragraph, InlineCode, Strong, Emphasis, Strike, Highlight, List, Steps, Quote, Callout, CodeBlock, TableStack, Figure, Divider, Lead, Insight, Pullquote, SoftList, and ClosingNote. Every component may define at most 3 variants per theme.

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
- Technical article elements must stay complete and readable: headings, body text, tables, code blocks, inline code, strong, emphasis, strike, highlight, lists, steps, quote, insight, divider, and images.
- Magazine feel should come from lead, pullquote, figure captions, whitespace, section rhythm, restrained emphasis, and closing notes.
- Each registered theme must render representative samples with a distinct visual tone and remain aligned with its golden reference.
- Editorial verify must reject skipped heading hierarchy, too many consecutive long paragraphs, too many consecutive emphasis blocks, and high-density sections with no breathing point.
- Markdown safety verify must reject raw HTML, style/class attributes, and scripts for every input.
- Layout contract verify must reject excessive highlighting, deep headings, and overlong paragraphs for generated `layout.md`.
