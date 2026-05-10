# Contributing

This repository is primarily a personal skill collection, but it is maintained in an open-source-friendly shape. Contributions should make skills easier for both humans and AI agents to understand, run, verify, and extend.

## Operating Model

- The owner defines priorities, product direction, and taste.
- AI agents may implement, refactor, document, verify, and clean up.
- Skills should be useful outside the owner's machine and should not depend on private context.

## Adding A Skill

Create a new top-level directory with a short, stable, lowercase name:

```text
new-skill/
├── SKILL.md
├── README.md
└── scripts/
```

Minimum requirements:

- `SKILL.md` has YAML frontmatter with `name` and `description`.
- `README.md` explains purpose, prerequisites, usage, validation, and maintenance.
- Root `skills.json` includes the skill id, path, status, summary, entrypoints, and validation commands.
- Commands use relative paths or placeholders like `article.md`, not personal absolute paths.
- Any deterministic workflow that may be repeated lives in `scripts/`.

Optional directories:

- `agents/` for role prompts.
- `assets/` for reusable static assets.
- `fixtures/` for stable test inputs.
- `goldens/` for curated expected outputs.
- `evals/` for automated evaluation cases.

## Updating A Skill

1. Read the skill's `SKILL.md`, `README.md`, and relevant scripts.
2. Preserve existing workflow contracts unless the task explicitly changes them.
3. Update docs and validation commands alongside code changes.
4. Update root `skills.json` if entrypoints, status, summary, or validation changed.
5. Remove obsolete examples, generated output, or references.
6. Run the relevant validation commands.

## Documentation Standards

- Keep root docs about the repository as a whole.
- Keep skill docs inside the skill directory.
- Use relative commands from the skill directory, such as `python3 scripts/render.py`.
- Avoid private paths, local hostnames, secrets, machine-specific assumptions, and stale sample references.
- Prefer concise docs that tell future agents where to look next.

## Open-Source Hygiene

Before committing, check for:

- `.DS_Store`, `__pycache__`, `*.pyc`, `.env`, or generated runtime outputs.
- Personal paths such as `/Users/...`.
- Dead references to deleted examples or old file names.
- Missing license or misleading README usage.
- JSON syntax errors in config files.

Useful scans:

```bash
rg -n "/Users/|/private/|/tmp/|absolute/path|API_KEY|SECRET|TOKEN|PASSWORD" .
find . -type d -name __pycache__ -o -name ".DS_Store" -o -name "*.pyc" -o -name ".env" -o -name ".env.*"
```

## Commit Style

Use concise conventional-style messages when possible:

- `feat: add <skill-name> skill`
- `feat: upgrade <skill-name> workflow`
- `fix: repair <skill-name> validation`
- `docs: clarify skill maintenance rules`
- `chore: clean generated artifacts`
