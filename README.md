# Kairos Skills

Reusable skills for AI coding agents.

This repository contains self-contained skills that enhance AI coding agents with automated workflows, deterministic tools, and specialized domain capabilities.

---
## Skills

| Skill                   | Description                                                                 |
|-------------------------|-----------------------------------------------------------------------------|
| [skill-autoresearch](./skill-autoresearch/) | Automatically optimize any agent skill through edit → eval → keep/revert loops |
| [kairos-wechat-typeset](./kairos-wechat-typeset/) | Deterministic Markdown-to-WeChat editorial HTML typesetting |

---

## Usage

### Prerequisites

- Python 3.8+
- Git
- An AI coding agent that supports local skills

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

Each skill is self-contained with its own directory. Current repository includes:

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
├── SKILL.md            # Required: skill definition with YAML frontmatter
├── README.md           # Required: human-readable documentation
├── agents/             # Optional: sub-agent prompts
├── scripts/            # Optional: executable scripts
└── evals/              # Optional: test cases for optimization
```

---

## License

MIT. See [LICENSE](./LICENSE).
