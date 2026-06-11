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
- Image planning is agent-mediated: the skill defines the visual contract, the host agent decides and generates or prompts, and the renderer only receives normal `Figure` components.

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

## Image Direction Contract

Image direction happens before rendering. The host agent reads the article, chosen theme, and theme `image_direction` rules, then decides whether the article needs any images at all. Zero images is valid when the article does not benefit from visual explanation.

The skill itself does not configure or call an image model. If the host agent has image-generation capability, it may generate assets from the plan and write them into the article output. If the host agent has no such capability, it outputs prompts for the user.

Allowed image roles:

| Visual Type | Best For | Avoid For |
| --- | --- | --- |
| `concept_diagram` | Abstract ideas, frameworks, mental models, and high-level relationships. | Decorative illustrations or claims that need real evidence. |
| `process_diagram` | Workflows, pipelines, implementation steps, and cause-effect chains. | Loose non-sequential ideas. |
| `comparison_diagram` | Tradeoffs, before/after states, capability matrices, and contrastive arguments. | Subjective mood setting. |
| `evidence_figure` | Source-backed screenshots, research visuals, product states, or data-derived visuals. | Any generated image that could be mistaken for factual evidence. |
| `atmosphere_still` | Sparse opening mood for literary, lifestyle, or reflective articles. | Technical explanation, specifications, or filler between sections. |

Every planned image must include:

- `necessity`: `high` or `medium`; low-value images should be omitted.
- `purpose`: what reader problem the image solves.
- `why_needed`: why text alone is weaker here.
- `theme_fit`: how the image follows the selected theme.
- `aspect_ratio`: defaults to `16:9`.
- `alt`, `caption`, and `prompt`.
- `avoid`: concrete visual moves to avoid, including theme-specific forbidden moves.
- `source_note` for every `evidence_figure`.

Prompts must forbid readable text inside the image unless the source image is supplied and the text is part of the evidence. Generated images must not invent product screenshots, metrics, charts, logos, citations, UI states, or factual evidence.

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
- Use image plans only when images reduce understanding cost, add evidence, clarify a structure, or establish article tone.
- Use ordered lists for steps and unordered lists for parallel points.
- Let code and tables stay clear and stable before adding magazine styling.

## Density Standards

量化密度指标，用于 editorial_verify.py 和 audit_visual.py 自动检查。

| 指标 | 目标值 | 检查方式 | 说明 |
| --- | --- | --- | --- |
| Highlight 占比 | <= 8% | audit_visual.py 统计 `==` 标记占全文字符比 | 过多 highlight 破坏克制感 |
| 连续长段落 | <= 3 段 | editorial_verify.py 检测连续 > 240 字段落 | 移动端阅读节奏 |
| 连续 emphasis | <= 2 段 | editorial_verify.py 检测连续 `**` / `*` 段落 | 避免全文"喊叫" |
| 高密度区块 breathing | 必须有 divider / quote / list | editorial_verify.py 检测 | 高密度段后需要呼吸 |
| Heading 层级 | 禁止跳级 | editorial_verify.py 检测 | H1 → H3 不允许 |
| 移动端横向滚动 | 0 | html_verify.py 检测 390px / 430px 宽度 | 表格和代码块不能溢出 |
| Kairos 组件频率 | 每 500 字 <= 2 个 | editorial_verify.py 统计 | 组件是语义选择，不是装饰 |

### Breathing Rule

高密度区块（连续 3 段以上长文字、代码块、表格）之后必须出现以下之一作为呼吸：
- `Divider`（`---` 或 `***`）
- `Quote`（`>` 引用块）
- `List`（有序或无序列表）
- `Callout`（`> [!NOTE]` 等）

### Highlight Budget

全文 `==` 标记的字符总数 / 全文字符总数 <= 8%。超过此阈值时，editorial_verify.py 应发出警告。

典型分布：
- 短文（< 1000 字）：最多 2-3 处 highlight
- 中文（1000-3000 字）：最多 5-8 处 highlight
- 长文（> 3000 字）：最多 10-15 处 highlight

## Mobile Rules

- Body text should remain readable around 16px.
- Line height should favor long-form reading.
- Images must use `max-width: 100%` and auto height.
- Tables must render as stacked mobile-safe information blocks.
- Code blocks must not depend on horizontal scrolling.
- Component spacing must come from the rhythm engine, not ad hoc Markdown tricks.
- The output must remain paste-friendly for the WeChat editor.
