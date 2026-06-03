# Kairos Skills

Reusable workflow skills for AI coding agents.

This repository collects practical skills that turn repeatable AI-assisted work into deterministic scripts, contracts, fixtures, and validation commands. The current focus is content-production workflows: use AI for editorial judgment, then rely on code for rendering, verification, and repeatable output.

## Product Direction

Kairos Skills is designed for people who want agent help without losing control of taste, structure, or delivery quality.

| User Need | Repository Answer |
|-----------|-------------------|
| Turn a repeatable workflow into something agents can run reliably | Each skill has `SKILL.md`, docs, scripts, fixtures, and validation commands |
| Keep AI output from drifting between runs | Stable contracts, registered options, deterministic scripts, and goldens |
| Share personal workflows without private machine context | Relative paths, open-source hygiene checks, and self-contained skill directories |
| Maintain taste and product intent over time | Human design notes plus agent-facing operating rules |

---
## Skills

| Skill                   | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| [kairos-wechat-typeset](./kairos-wechat-typeset/) | Deterministic Markdown-to-WeChat semantic editorial design system with four built-in themes |

The machine-readable inventory lives in [`skills.json`](./skills.json).

---

## Usage

### Prerequisites

- Python 3.8+
- Git
- An AI coding agent that supports local skills

### For AI Agents

Start with [`AGENTS.md`](./AGENTS.md). It defines repository conventions, tool preferences, validation expectations, and the skill directory contract.

Use [`skills.json`](./skills.json) as the fast inventory before opening individual skill folders.

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Kairos0922/kairos-skills.git
cd kairos-skills

# Check the current skill surface
cd kairos-wechat-typeset
python3 scripts/check_all.py --smoke
```

Render a Markdown article into HTML suitable for the WeChat editor:

```bash
python3 scripts/render.py --theme song --input article.md --output article.html --verify
```

For a versioned user workflow that writes outputs under `~/.wechat-typeset/`, use:

```bash
python3 scripts/typeset.py --input article.md --theme song --optimize-layout no --non-interactive
```

### Current WeChat Themes

`kairos-wechat-typeset` currently includes four registered themes:

| Theme | Chinese Name | Best For |
|-------|--------------|----------|
| `song` | 宋式美学主题 | 技术长文、方法论、人文评论、生活方式、书评 |
| `wending` | 稳境白纸主题 | 个人成长、心理秩序、生活方式、轻方法论、慢阅读文章 |
| `tech` | 科技主题 | AI 技术文章、工程实践、产品方案、研发实践、工具教程 |
| `wisme` | WISME 规范主题 | 知识科普、研究报告、组件规范、方法论、专业说明 |

Use the registry command to confirm the current public theme surface:

```bash
cd kairos-wechat-typeset
python3 scripts/render.py --list-themes
```

### When To Use This Repository

Use this repository when a workflow is valuable enough to preserve as a reusable skill: it has clear inputs, repeatable outputs, quality rules, and validation commands. Do not add one-off prompts, local scratch files, or workflows that depend on private paths or secrets.

---

## Adding New Skills

Each skill is self-contained with its own directory. New skills should fit the content-production and agent-workflow direction unless the repository strategy changes. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full workflow.

Current repository includes:

```text
kairos-skills/
├── README.md
├── kairos-wechat-typeset/  # Markdown -> WeChat HTML typesetter
└── ...
```

## Repository Maintenance

- Start from [`AGENTS.md`](./AGENTS.md) before changing the repository.
- Keep [`skills.json`](./skills.json) aligned with runnable entrypoints and validation commands.
- For `kairos-wechat-typeset` theme work, read [`themes/METHODOLOGY.md`](./kairos-wechat-typeset/themes/METHODOLOGY.md) before implementation.
- Validate changed areas before committing, and remove generated caches such as `__pycache__`.

---

## Skill Structure

```text
skill-name/
├── SKILL.md            # Required: machine-facing skill instructions
├── README.md           # Required: human-facing documentation
├── agents/             # Optional: role prompts
├── scripts/            # Optional: deterministic helpers
├── fixtures/           # Optional: stable test inputs
├── goldens/            # Optional: curated expected outputs
└── evals/              # Optional: automated evaluation cases
```

---

## License

MIT. See [LICENSE](./LICENSE).
