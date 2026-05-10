# Kairos Skills

Personal skill collection for AI coding agents.

This repository is where I collect reusable skills from daily work. I plan and design the skills; AI agents help implement, verify, document, and maintain them. The goal is to keep each skill useful for my own workflow while making the repository clear enough for future AI agents and open-source users to understand quickly.

---
## Skills

| Skill                   | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| [skill-autoresearch](./skill-autoresearch/) | Automatically optimize any agent skill through edit → eval → keep/revert loops |
| [kairos-wechat-typeset](./kairos-wechat-typeset/) | Deterministic Markdown-to-WeChat editorial HTML typesetting |

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

# Examples for included skills

# 1) skill-autoresearch: run the optimization loop for a target skill
cd skill-autoresearch
python3 scripts/loop.py --skill-path ../my-skill --max-iterations 20

# 2) kairos-wechat-typeset: render a Markdown file to HTML suitable for WeChat editor
cd ../kairos-wechat-typeset
python3 scripts/render.py --theme song --input article.md --output article.html --verify
```

---

## Adding New Skills

Each skill is self-contained with its own directory. See [`CONTRIBUTING.md`](./CONTRIBUTING.md) for the full workflow.

Current repository includes:

```text
kairos-skills/
├── README.md
├── skill-autoresearch/     # Optimization loop for improving agent skills
├── kairos-wechat-typeset/  # Markdown -> WeChat HTML typesetter
└── ...
```

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
