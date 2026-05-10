# Semantic Components

`kairos-wechat-typeset` uses semantic components to express what a piece of content should become in a WeChat article body. Components are not decorative blocks. They are the best editorial expression for a specific content role.

The V3 direction is:

```text
Markdown + Kairos component syntax
  -> Semantic component contract
  -> Theme component implementation
  -> WeChat-compatible inline HTML
```

This contract serves three goals:

- Stable WeChat article output.
- Faster theme expansion through a shared component matrix.
- High-quality magazine-like articles through semantic choice, restraint, whitespace, and reading rhythm.

## Principles

- Mobile first: every component must read well at common WeChat phone widths.
- Semantic first: choose components by content role, not by desired decoration.
- Inline only: renderer output must not require `<style>`, `class`, external CSS, scripts, native tables, native lists, or horizontal overflow.
- Technical writing safe: headings, paragraphs, tables, code, inline code, emphasis, links, images, quotes, and steps must remain clear before they are beautiful.
- Restrained magazine feel: whitespace, rhythm, typography, captions, pullquotes, and section breathing create the magazine quality.
- Theme parity: each registered theme should implement the same core component contract, even when the visual treatment differs.

## Core Components

| Component | Source Syntax | Best For | Avoid For |
| --- | --- | --- | --- |
| `Heading` | `#`, `##`, `###` | Article title and section structure. Numeric `## 01 Title` may become a themed section heading. | Decorative slogans, skipped heading levels, or deep outlines below `###`. |
| `Paragraph` | Plain Markdown paragraph | Normal explanation, reasoning, narrative, and transitions. | Dense paragraphs over 240 characters; split them before rendering. |
| `InlineCode` | `` `code` `` | API names, flags, filenames, commands, short identifiers. | Long code or command sequences; use `CodeBlock`. |
| `Strong` | `**text**` or `__text__` | Important terms or short emphasis. | Whole-article shouting or many consecutive emphasis blocks. |
| `Emphasis` | `*text*` or `_text_` | Soft tone shifts and secondary emphasis. | Content that needs structural importance. |
| `Strike` | `~~text~~` | Correction, removal, or contrast. | Decoration. |
| `Highlight` | `==text==` | Key sentence fragments or core terms that deserve visual attention. | Highlighting more than 8% of the article or repeated full sentences. |
| `List` | `- item` or `1. item` | Parallel points, compact distinctions, and ordered references. | Procedural instructions that need clear steps. |
| `Steps` | Ordered list | Sequential actions where order matters. | Loose conceptual lists. |
| `Quote` | `> quote` | External quotations, cited claims, or clearly quoted speech. | Author's own core insight; use `Insight` or `Pullquote`. |
| `Callout` | `> [!NOTE]`, `> [!TIP]`, `> [!WARNING]` | Notes, tips, warnings, cautions, and implementation reminders. | General decoration or repeated side comments. |
| `CodeBlock` | Fenced code block | Code samples, config, terminal output, multiline commands. | Short identifiers; use `InlineCode`. |
| `TableStack` | Markdown table | Parameters, comparisons, capability matrices, and structured data. | Wide desktop-style tables; rendering must stack safely on mobile. |
| `Figure` | `:::figure` | Image plus caption and editorial context. | Raw image drops with no caption when the image carries meaning. |
| `Divider` | `---`, `***`, or paragraph divider comment | Real rhythm turns, section breathing, or scene changes. | Decorative spacing after every short section. |

## Kairos Components

Kairos components use Markdown container syntax and may not contain raw HTML, CSS, `style`, `class`, scripts, or arbitrary custom tags.

### `lead`

```markdown
:::lead
Opening paragraph that sets the article's voice and reading promise.
:::
```

Use for the opening editorial lead. It should orient the reader and establish tone. Avoid using it in the middle of an article.

### `insight`

```markdown
:::insight
The core judgment the reader should remember.
:::
```

Use for the author's distilled argument or high-value technical conclusion. Avoid using it for external quotes, long explanations, or decorative emphasis.

### `pullquote`

```markdown
:::pullquote
A sentence that can stand alone as a memorable editorial line.
:::
```

Use sparingly for magazine-like extraction. It should be readable out of context. Avoid turning every important sentence into a pullquote.

### `figure`

```markdown
:::figure
![Image alt text](https://example.com/image.png)
Caption that explains why this image matters.
:::
```

Use for images that support explanation, evidence, product state, or atmosphere. The caption is part of the component, not optional decoration.

### `soft-list`

```markdown
:::soft-list
- First quiet point
- Second quiet point
:::
```

Use for non-procedural, editorially paced lists. Use normal ordered lists for steps and hard sequences.

### `closing-note`

```markdown
:::closing-note
A restrained final note that closes the article.
:::
```

Use only near the end. It should leave a controlled aftertaste, not add a new argument.

## Theme Component Matrix

Every theme should provide a deliberate treatment for the same component set:

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

Theme implementations may differ in typography, spacing, line language, accent use, and density. They should not differ in semantic availability. If a theme intentionally treats two components similarly, document the reason in `themes/<theme-id>/DESIGN.md`.

## Rhythm Rules

- Use one opening `lead` at most.
- Use `pullquote` rarely, usually no more than one per major section.
- Keep `insight` for true conclusions or key judgments.
- Keep `Divider` for real rhythm shifts.
- Avoid more than two consecutive emphasis-heavy blocks.
- Split very long paragraphs before rendering.
- Use captions for meaningful images.
- Use ordered lists for steps and unordered lists for parallel points.
- Let code and tables stay clear and stable before adding magazine styling.

## Mobile Rules

- Body text should remain readable around 16px.
- Line height should favor long-form reading.
- Images must use `max-width: 100%` and auto height.
- Tables must render as stacked mobile-safe information blocks.
- Code blocks must not depend on horizontal scrolling.
- Component spacing must come from the rhythm engine, not ad hoc Markdown tricks.
- The output must remain paste-friendly for the WeChat editor.

