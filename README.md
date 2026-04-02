# Kairos Skills

> Personal skill collection for AI coding agents.

This repository contains reusable skills that enhance AI coding agents (Claude Code, Cursor, VS Code, etc.) with automated workflows, optimizations, and specialized capabilities.

---

## Skills

| Skill | Description |
|-------|-------------|
| [skill-autoresearch](./skill-autoresearch/) | Automatically optimize any agent skill through edit → eval → keep/revert loops |

---

## Usage

### Prerequisites

- Python 3.8+
- Git
- An AI agent CLI (e.g., Claude Code CLI) in PATH

### Quick Start

```bash
# Clone the repository
git clone https://github.com/Kairos0922/kairos-skills.git
cd kairos-skills

# Navigate to the skill you want to use
cd skill-autoresearch

# Run the optimization loop for your target skill
python3 scripts/loop.py --skill-path /path/to/your/target-skill --max-iterations 20
```

---

## Adding New Skills

Each skill is self-contained with its own directory:

```
kairos-skills/
├── README.md              # This file
├── skill-autoresearch/
│   ├── SKILL.md           # Skill definition (used by AI agents)
│   ├── README.md          # Skill documentation
│   ├── agents/            # Sub-agent prompts
│   └── scripts/           # Executable scripts
└── another-skill/
    ├── SKILL.md
    └── ...
```

---

## Skill Structure

```
skill-name/
├── SKILL.md            # Required: skill definition with YAML frontmatter
├── README.md           # Required: human-readable documentation
├── agents/             # Optional: sub-agent prompts
├── scripts/            # Optional: executable scripts
└── evals/             # Optional: test cases for optimization
```

---

## License

MIT
