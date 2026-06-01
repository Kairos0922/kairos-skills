# Kairos Skills

Personal skill collection for AI coding agents.

This repository is where I collect reusable skills from daily work. I plan and design the skills; AI agents help implement, verify, document, and maintain them. The goal is to keep each skill useful for my own workflow while making the repository clear enough for future AI agents and open-source users to understand quickly.

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

# Example: kairos-wechat-typeset renders Markdown to HTML suitable for WeChat editor
cd kairos-wechat-typeset
python3 scripts/render.py --theme song --input article.md --output article.html --verify
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

---

## Adding New Skills

Each skill is self-contained with its own directory. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full workflow.

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
