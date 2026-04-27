# Skill Autoresearch

> Automatically optimize any agent skill through edit → eval → keep/revert loops.

**skill-autoresearch** applies the core methodology from [karpathy/autoresearch](https://github.com/karpathy/autoresearch) to agent skill optimization. Given a target skill (`SKILL.md` + `evals/evals.json`), it automatically runs optimization iterations until score convergence or iteration limit.

---

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│  Iteration N                                                │
│                                                             │
│  1. Snapshot current SKILL.md via git                      │
│  2. Autorelop proposes 2–4 related changes                 │
│  3. Apply changes to SKILL.md                              │
│  4. Harness runs all eval cases → grading                  │
│  5. Aggregate → mean pass_rate                             │
│  6. Decision: keep / revert / stop                         │
│       │  if revert: restore SKILL.md to snapshot ref       │
│       ▼                                                    │
└─────────────────────────────────────────────────────────────┘
       │
       │  keep
       ▼
  Next iteration...
```

Every **keep** decision updates the running best. Every **revert** restores only the target `SKILL.md` to the snapshot ref, so the loop can reject bad experiments without resetting unrelated files in the repo.

---

## Key Concepts

### Experimental Idea

One idea = 2–4 related changes serving one goal. Not 4 unrelated changes.

Example:
> "Tighten hot news filtering to match grader's semantic expectations"
> - Change 1: Adjust value_score threshold from <0.5 to <0.3
> - Change 2: Add explicit '快讯' keyword check in rejection reasoning

### Running Best + Epsilon

LLM grading has variance. To avoid thrashing:
- `epsilon = 0.05` (5%) — noise tolerance
- Improvements < 5% don't update running_best
- A **revert** only triggers when pass_rate drops below `running_best - epsilon`

### Autoresearch Constraints

To stay close to the original autoresearch philosophy, this skill keeps the search space intentionally narrow:
- Only the target `SKILL.md` is edited.
- The eval suite is treated as fixed for the loop.
- `grading_summary.txt`, `history.json`, and `results.tsv` make every iteration reviewable.
- Skill size is tracked per iteration so complexity growth is visible to the watchdog and to humans.

### Watchdog

Every N iterations (default: 5), an LLM Judge reviews:
- Is the skill measurably improving?
- Are assertions measuring the right things?
- Is optimization drifting in the wrong direction?

---

## Installation

```bash
# Clone the repo
git clone https://github.com/Kairos0922/kairos-skills.git
cd kairos-skills/skill-autoresearch

# Dependencies
# - Python 3.8+
# - git (in PATH)
# - Agent CLI in PATH (e.g., claude CLI)
```

---

## Quick Start

### 1. Prepare Your Target Skill

Your skill must have:

```
target-skill/
├── SKILL.md            # Skill definition
└── evals/
    └── evals.json      # Test cases + assertions
```

**evals/evals.json format:**

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "User task description",
      "expected_output": "Expected output description",
      "assertions": [
        "Output is valid JSON format",
        "signals is a non-empty array",
        "If topic contains GPT-5, then chase_trend is true or value_score < 0.3"
      ]
    }
  ]
}
```

### 2. Run the Loop

```bash
python3 scripts/loop.py \
  --skill-path /path/to/target-skill \
  --max-iterations 20
```

### 3. Options

| Flag | Default | Description |
|------|---------|-------------|
| `--epsilon` | 0.05 | Noise tolerance for keep/revert decisions |
| `--max-iterations` | 50 | Hard stop after N iterations |
| `--watchdog-interval` | 5 | Run watchdog every N iterations (0 to disable) |
| `--skip-revert` | false | Dry-run mode (don't actually revert) |

---

## Output

Artifacts are written alongside the target skill in `<skill-path>-eval/`:

```
<skill-path>-eval/
├── results.tsv                     # one-line summary per iteration
├── history.json                    # cumulative history
├── iteration-1/
│   ├── eval-1/
│   │   ├── output.json              # raw model output
│   │   ├── output.envelope.json     # executor wrapper (if present)
│   │   ├── output.structured.json   # unwrapped skill output
│   │   ├── grading.json             # pass/fail per assertion
│   │   └── metrics.json             # execution + grading timings
│   ├── benchmark.json               # aggregated results
│   ├── grading_summary.txt          # concise failure summary for next round
│   └── idea_proposal.json           # what autorelop proposed
├── iteration-2/
│   └── ...
```

---

## Architecture

```
skill-autoresearch/
├── SKILL.md                      # This file
├── agents/
│   └── autorelop.md              # Autorelop agent prompt
├── scripts/
│   ├── loop.py                   # Main orchestration
│   ├── harness.py                # Spawn executor + grader subagents
│   ├── aggregate.py              # Compute benchmark from grading results
│   ├── decision.py               # Keep/revert/stop decision logic
│   └── watchdog.py               # LLM Judge quality gate
└── skills/
    └── test-skill-classifier/   # Test skill for validation
```

**Subagent spawning:** Uses `claude -p` subprocess with `cwd=SKILL_DIR`.

---

## Assertions Best Practices

1. **Prefer format/structure assertions** — zero variance, always consistent
2. **Use extreme semantic thresholds** — `value_score < 0.3` not `< 0.5`
3. **Avoid borderline assertions** — "might be hot news" has high variance
4. **Write assertions that match what you actually care about** — assertions determine the ceiling

---

## License

MIT
