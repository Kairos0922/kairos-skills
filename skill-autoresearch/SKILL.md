---
name: skill-autoresearch
description: Automatically optimize any agent skill through edit → eval → keep/revert loops. Use when the user wants to improve a skill's quality, test assertions, or run automated optimization experiments.
---

# Skill Autoresearch

> Automatically optimize any agent skill through automated experimentation.

## Purpose

Given a **target skill** (`SKILL.md` + `evals/evals.json`), automatically run optimization iterations until:
- Pass rate reaches 100% (all assertions pass)
- Running best plateaus for 3 consecutive iterations
- Maximum iterations reached (default: 50)
- Watchdog detects untested complexity growth

## Core Loop

Each iteration executes:

```
1. Snapshot: save the current `SKILL.md` state via git
2. Autorelop: Propose ONE experimental idea (2-4 related changes)
3. Apply: Modify SKILL.md with proposed changes
4. Harness: Run all eval cases → grading.json per case
5. Aggregate: Compute mean pass_rate across eval cases
6. Decision:
   - pass_rate > running_best + epsilon (5%) → KEEP (new best)
   - pass_rate >= running_best - epsilon → KEEP (within noise)
   - pass_rate < running_best - epsilon → REVERT (restore `SKILL.md` to the snapshot ref)
7. Watchdog: Every N iterations, LLM Judge evaluates if optimization is heading the right direction
```

## Key Concepts

### Experimental Idea

One coherent goal = 2-4 related changes. NOT 4 unrelated changes.

Example of a good idea:
> "Tighten hot news filtering to match grader's semantic expectations"
> - Change 1: Adjust value_score threshold from <0.5 to <0.3
> - Change 2: Add explicit '快讯' keyword check in rejection reasoning
> - Change 3: Add time-sensitivity flag for topics with '刚刚', '发布'

### Running Best + Epsilon

Because LLM grading has variance (especially on semantic assertions), we use epsilon-greedy:
- `epsilon = 0.05` (5%) — default noise tolerance
- Improvements < 5% are treated as "within noise" and don't update running_best

### Search Space Discipline

To stay aligned with the original autoresearch idea:
- Only the target `SKILL.md` is edited inside the loop
- `evals/evals.json` is treated as fixed measurement, not something the optimizer can patch
- `grading_summary.txt`, `history.json`, and `results.tsv` make each iteration auditable
- Skill size is tracked so complexity growth is visible to the watchdog

### Watchdog

Every N iterations (default: 5), an LLM Judge reviews:
1. Is the skill measurably improving?
2. Are assertions measuring the right things?
3. Is optimization drifting in the wrong direction?
4. Are there untested features being added?

If watchdog returns `should_stop: true`, the loop terminates.

## Usage

### Basic

```
/skill-autoresearch --skill-path /path/to/target-skill --max-iterations 20
```

### With Options

```
/skill-autoresearch \
  --skill-path /path/to/target-skill \
  --max-iterations 50 \
  --epsilon 0.05 \
  --watchdog-interval 5
```

### Python API

```python
import subprocess
import json

result = subprocess.run([
    "python3", "scripts/loop.py",
    "--skill-path", "/path/to/target-skill",
    "--max-iterations", "20",
    "--epsilon", "0.05",
    "--watchdog-interval", "5"
], capture_output=True, text=True)

history = json.loads(open("/path/to/target-skill-eval/history.json").read())
print(f"Final best: {history['running_best']:.1%}")
```

## Input Requirements

The target skill must have:
- `SKILL.md` — the skill definition
- `evals/evals.json` — test cases + assertions

### evals/evals.json Format

```json
{
  "skill_name": "target-skill",
  "evals": [
    {
      "id": 1,
      "prompt": "user task description",
      "expected_output": "what good output looks like",
      "assertions": [
        "输出是有效的JSON格式",
        "signals 是非空数组",
        "如果包含GPT-5相关topic，则 chase_trend 为 true 或 value_score < 0.3"
      ]
    }
  ]
}
```

## Output

Artifacts are written alongside the target skill in `<skill-path>-eval/`:
```
<skill-path>-eval/
├── results.tsv                    # one-line summary per iteration
├── history.json                   # cumulative history
├── iteration-1/
│   ├── eval-1/
│   │   ├── output.json           # raw model output
│   │   ├── output.envelope.json  # executor wrapper (if present)
│   │   ├── output.structured.json # unwrapped skill output
│   │   ├── grading.json          # pass/fail per assertion
│   │   └── metrics.json          # timing info
│   ├── benchmark.json            # aggregated results
│   ├── grading_summary.txt       # compact failure summary for autorelop/watchdog
│   └── idea_proposal.json        # what autorelop proposed
├── iteration-2/
│   └── ...
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--epsilon` | 0.05 | Noise tolerance for keep/revert |
| `--max-iterations` | 50 | Hard stop after N iterations |
| `--watchdog-interval` | 5 | Run watchdog every N iterations (0 to disable) |
| `--skip-revert` | false | Dry-run mode (don't actually revert) |

## Assertions Best Practices

1. **Prefer format/structure assertions** — zero variance, always consistent
2. **Use extreme semantic thresholds** — value_score < 0.3 instead of < 0.5
3. **Avoid borderline assertions** — "might be hot news" has high variance
4. **Keep assertions testable** — if you add self-reflection rules, add eval cases that test them

## How It Works

```
┌─────────────────────────────────────────────────────────┐
│  Autorelop Agent                                        │
│  • Reads SKILL.md + history + grading feedback           │
│  • Proposes one experimental idea (2-4 related changes)│
│  • Output: JSON changes[] + expected_impact            │
└────────────────────┬────────────────────────────────────┘
                     │ propose
                     ▼
┌─────────────────────────────────────────────────────────┐
│  Skill Autoresearch Loop                                │
│                                                         │
│  ┌─────────┐   ┌─────────┐   ┌────────────┐            │
│  │ Snapshot │──▶│  Apply  │──▶│  Harness  │            │
│  │ (git)   │   │Changes  │   │(eval+grade)│            │
│  └─────────┘   └─────────┘   └─────┬──────┘            │
│                                   │                    │
│                          ┌────────▼────────┐            │
│                          │   Aggregate   │            │
│                          │(mean pass_rate)│            │
│                          └─────┬──────────┘            │
│                                │                       │
│                          ┌─────▼──────┐   ┌─────────┐ │
│                          │  Decision  │──▶│ Keep/   │ │
│                          │(running_best│   │ Revert │ │
│                          └─────┬──────┘   └─────────┘ │
│                                │                       │
│                    ┌───────────▼───────────┐            │
│                    │      Watchdog        │            │
│                    │  (every N rounds)   │            │
│                    └───────────▲───────────┘            │
│                                │ stop if poor         │
└────────────────────────────────┘
```

## Files

```
skill-autoresearch/
├── SKILL.md                      # This file
├── agents/
│   └── autorelop.md              # Autorelop agent prompt
├── scripts/
│   ├── loop.py                   # Main orchestration
│   ├── harness.py                # Eval harness
│   ├── aggregate.py              # Result aggregation
│   ├── decision.py               # Keep/revert/stop
│   └── watchdog.py               # LLM Judge watchdog
└── runs/                         # Runtime data
```

## Dependencies

- `claude` CLI in PATH (for spawning subagents)
- `git` in PATH (for snapshot/revert)
- Python 3.8+
- Target skill must be in a git repository (for snapshot isolation)
