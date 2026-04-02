# Skill Autoresearch

> Automatically optimize any agent skill through edit → eval → keep/revert loops.

[![MIT License](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**skill-autoresearch** applies the core methodology from [karpathy/autoresearch](https://github.com/karpathy/autoresearch) to agent skill optimization. Given a target skill (`SKILL.md` + `evals/evals.json`), it automatically runs optimization iterations until score convergence or iteration limit.

---

## What It Does

```
Your Skill's SKILL.md
       │
       ▼
┌──────────────────────────────────────────────┐
│  Iteration N                                  │
│                                               │
│  1. Git snapshot (git add + commit)           │
│  2. Autorelop proposes 2-4 related changes  │
│  3. Apply changes to SKILL.md                 │
│  4. Harness runs all eval cases → grading     │
│  5. Aggregate → mean pass_rate                │
│  6. Decision: keep / revert / stop             │
│       │                                      │
│       │  if revert: git reset --hard HEAD~1  │
│       ▼                                      │
└──────────────────────────────────────────────┘
       │
       │ keep
       ▼
  Next iteration...
```

Every **keep** decision updates the running best. Every **revert** discards the changes via `git reset --hard HEAD~1`. This means you can sleep while the system experiments — if it breaks something, it automatically reverts.

---

## Key Concepts

### Experimental Idea (Autorelop)

One idea = 2-4 related changes serving one goal. Not 4 unrelated changes.

Good example:
> "Tighten hot news filtering to match grader's semantic expectations"
> - Change 1: Adjust value_score threshold from <0.5 to <0.3
> - Change 2: Add explicit '快讯' keyword check in rejection reasoning

### Running Best + Epsilon

LLM grading has variance (especially on semantic assertions). To avoid thrashing:

- `epsilon = 0.05` (5%) — noise tolerance
- Improvements < 5% are treated as "within noise" and don't update running_best
- A **revert** only triggers when pass_rate drops below `running_best - epsilon`

### Watchdog

Every N iterations (default: 5), an LLM Judge reviews the optimization trajectory:

- Is the skill measurably improving?
- Are assertions measuring the right things?
- Is the optimization drifting in the wrong direction?
- Are there untested features being added?

If the watchdog returns `should_stop: true`, the loop terminates.

---

## Installation

```bash
# Clone the repo
git clone https://github.com/your-username/skill-autoresearch.git
cd skill-autoresearch

# No external dependencies beyond:
# - Python 3.8+
# - claude CLI (in PATH)
# - git (in PATH)
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
      "prompt": "用户任务描述",
      "expected_output": "期望的输出是什么样的",
      "assertions": [
        "输出是有效的JSON格式",
        "signals 是非空数组",
        "如果包含GPT-5相关topic，则 chase_trend 为 true 或 value_score < 0.3"
      ]
    }
  ]
}
```

**Assertion best practices:**
- Prefer **format/structure** assertions — zero grading variance
- Use **extreme semantic thresholds** — `value_score < 0.3` not `< 0.5`
- Avoid **borderline assertions** — "might be hot news" has high variance

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

Example with all options:

```bash
python3 scripts/loop.py \
  --skill-path /path/to/target-skill \
  --max-iterations 50 \
  --epsilon 0.05 \
  --watchdog-interval 5
```

---

## Output

After each iteration:

```
runs/<skill-name>/
├── iteration-0/
│   ├── eval-1/
│   │   ├── output.json              # Raw skill output
│   │   ├── grading.json             # Pass/fail per assertion
│   │   └── output.structured.json   # Parsed JSON
│   ├── eval-2/
│   │   └── ...
│   ├── benchmark.json               # Aggregated results
│   ├── history.json                 # All iterations so far
│   └── idea_proposal.json          # What autorelop proposed
├── iteration-1/
│   └── ...
└── history.json                     # Cumulative history
```

**benchmark.json:**

```json
{
  "benchmark": {
    "mean_pass_rate": 0.917,
    "stddev": 0.08,
    "per_case": [...]
  },
  "quality": {
    "quality_score": "good",
    "warnings": []
  }
}
```

---

## Architecture

```
skill-autoresearch/
├── SKILL.md                      # This file (agent skill format)
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

**Subagent spawning:** Uses `claude -p` subprocess with `cwd=SKILL_DIR`. Output parsing via regex (`\{[\s\S]*\}`) instead of stream-json for reliability.

---

## How It Compares to karpathy/autoresearch

| Aspect | karpathy | skill-autoresearch |
|--------|----------|-------------------|
| **Optimizing** | `train.py` (ML training code) | `SKILL.md` (prompt/instructions) |
| **Evaluator** | Fixed math function (`val_bpb`) | LLM grader (assertions-based) |
| **Evaluator variance** | Zero (deterministic) | Non-zero (LLM has variance) |
| **Decision rule** | Adjacent comparison | Running best + epsilon |
| **Isolation** | Git snapshot | Git snapshot |
| **Idea strategy** | Batch (1 idea = N related changes) | Batch (1 idea = 2-4 related changes) |

The key adaptation is the **Running Best + Epsilon** decision rule, which compensates for LLM grading variance that doesn't exist in karpathy's fixed math function evaluator.

---

## Limitations

1. **Skill must not depend on external Python scripts.** The harness runs subagents with `cwd=SKILL_DIR`, which restricts access to parent directories. Skills should be pure LLM-inference or pre-collect data before calling the harness.

2. **Assertions determine the ceiling.** If assertions only test JSON format/structure, the system will optimize format at the expense of actual decision quality. Write assertions that match what you actually care about.

3. **LLM grading variance.** Semantic assertions (especially borderline ones) have high variance (~19% stddev on boundary cases). Use extreme thresholds to avoid this.

4. **Git required.** Snapshot isolation requires the target skill to be in a git repository.

---

## Credits

- **Core methodology:** [karpathy/autoresearch](https://github.com/karpathy/autoresearch) by Andrej Karpathy
- **Inspiration:** The "can sleep while it runs" philosophy — human just watches and reads results
- **Built on:** Agent skill framework

---

## License

MIT
