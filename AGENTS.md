# AGENTS.md

This repository is a personal skill collection maintained by the owner and executed with help from AI agents. The owner sets direction, product taste, and final intent. AI agents implement, refactor, verify, and document the skills so the repository stays usable by both humans and future agents.

## Repository Purpose

- Collect reusable skills that the owner uses in daily work.
- Keep every runnable skill self-contained and understandable without private context.
- Prefer deterministic scripts, tests, fixtures, and verification over one-off prompt magic.
- Preserve the owner's design intent while making each skill practical for open-source users.

## First Steps For Agents

1. Read this file first.
2. Read the root `README.md` for repository overview.
3. Read `skills.json` for a machine-readable inventory of runnable skills.
4. Read the target skill's `SKILL.md` and `README.md` before editing it.
5. Inspect the existing directory structure and scripts before proposing new structure.
6. Check `git status --short` before edits and avoid overwriting unrelated user changes.

## Tooling Preferences

- Use the OpenAI Docs MCP server for OpenAI API, Codex, and SDK documentation.
- Use the GitHub MCP server for repositories, issues, and pull requests. Do not use browser tools for GitHub if MCP can handle it.
- Use Playwright MCP for browser automation, navigation, clicking, and scraping.
- Use Chrome DevTools MCP only for debugging DOM, network, performance, or console issues.
- Prefer MCP tools and local repository inspection over guessing. If one relevant tool fails, try another relevant tool.
- Use `rg` / `rg --files` for repository search whenever available.

## Skill Directory Contract

Every skill directory should be self-contained and should avoid relying on private machine paths.

Required:

- `SKILL.md`: machine-facing skill instructions with YAML frontmatter.
- `README.md`: human-facing usage and maintenance notes.

Recommended when useful:

- `scripts/`: deterministic executable helpers.
- `agents/`: role prompts or sub-agent instructions.
- `themes/`, `assets/`, `goldens/`, `fixtures/`, or `evals/`: only when they directly support the skill.

Avoid:

- Local-only paths such as `/Users/...`, `/tmp/...`, or machine-specific URLs.
- Runtime caches, generated throwaway examples, `.DS_Store`, `__pycache__`, `.env`, or secrets.
- Large auxiliary docs that duplicate `SKILL.md` or `README.md`.

## Design And Implementation Rules

- Keep skills focused. A skill should solve one coherent workflow well.
- Put stable behavior into scripts or structured config instead of relying on LLM improvisation.
- Keep `SKILL.md` concise enough for agents to load quickly. Move deep implementation detail into scripts or targeted reference files.
- Treat themes, golden outputs, fixtures, and evals as product assets, not scratch files.
- When changing a runnable skill, update its validation commands and run them.
- When deleting examples or generated files, update all docs that referenced them.
- For open-source readiness, search for personal paths, secrets, stale commands, and private assumptions before committing.

## Validation Checklist

Before finishing a change, run the checks that match the edited area:

- Python syntax: `python3 -m py_compile ...`
- JSON validity: `python3 -m json.tool path/to/file.json >/dev/null`
- Skill-specific verify scripts, such as `python3 scripts/verify.py ...`
- Repository hygiene search for personal paths or stale examples when docs are edited.

Always remove caches created by validation before committing:

```bash
find . -type d -name __pycache__ -prune -exec rm -rf {} +
```

## Git Discipline

- Keep unrelated changes out of a commit.
- Do not revert user changes unless explicitly asked.
- Use clear commit messages that describe the skill or repository workflow being changed.
- Prefer one coherent commit per user-requested task.

## Current Skills

- `skill-autoresearch`: automated edit/eval/keep-revert loop for optimizing skills.
- `kairos-wechat-typeset`: deterministic Markdown-to-WeChat editorial HTML design system.

Keep `skills.json` updated when adding, removing, renaming, or materially changing a skill.
