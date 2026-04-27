#!/usr/bin/env python3
"""
scripts/loop.py — Main Optimization Loop

Orchestrates the full edit → eval → keep/revert cycle.

Workflow per iteration:
1. Snapshot the current SKILL.md state
2. Ask autorelop for one focused experiment
3. Apply the proposed changes to SKILL.md
4. Run harness.py to evaluate the skill
5. Run aggregate.py to compute benchmark metrics
6. Keep or revert the experimental changes
7. Optionally run watchdog.py
8. Record history + results.tsv

Usage:
    python3 scripts/loop.py --skill-path /path/to/target-skill --max-iterations 20
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Optional

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
RUNS_ROOT = WORKSPACE_ROOT / "runs"
MAX_CONSECUTIVE_FAILURES = 3
RESULTS_HEADER = "\t".join([
    "iteration",
    "decision",
    "pass_rate",
    "running_best",
    "delta",
    "is_new_best",
    "effective_epsilon",
    "stddev",
    "skill_lines_before",
    "skill_lines_after",
    "skill_line_delta",
    "stop_reason",
])


def format_pass_rate(value: Optional[float]) -> str:
    """Format pass_rate values for logs and context text."""
    if value is None:
        return "N/A"
    return f"{value:.1%}"


def resolve_runs_root(skill_path: Path) -> Path:
    """Store run artifacts alongside the target skill, not inside this skill repo."""
    return Path(f"{skill_path}-eval").resolve()


def load_json(path: Path, default: Optional[dict] = None) -> dict:
    """Load a JSON file with a safe default."""
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default or {}


def save_json(path: Path, payload: dict) -> None:
    """Write a JSON file with consistent formatting."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def load_history(runs_root: Path, skill_name: str, skill_path: Path, max_iterations: int, epsilon: float) -> dict:
    """Load existing history or initialize a new one for this run root."""
    history_path = runs_root / "history.json"
    history = load_json(history_path, {})
    if history:
        history.setdefault("skill_name", skill_name)
        history.setdefault("skill_path", str(skill_path))
        history["max_iterations"] = max_iterations
        history["epsilon"] = epsilon
        history.setdefault("iterations", [])
        history.setdefault("running_best", 0.0)
        history.setdefault("plateau_count", 0)
        return history

    return {
        "skill_name": skill_name,
        "skill_path": str(skill_path),
        "max_iterations": max_iterations,
        "epsilon": epsilon,
        "iterations": [],
        "running_best": 0.0,
        "plateau_count": 0,
    }


def save_history(runs_root: Path, history: dict) -> Path:
    """Persist cumulative history.json."""
    history_path = runs_root / "history.json"
    save_json(history_path, history)
    return history_path


def append_results_row(runs_root: Path, record: dict) -> Path:
    """Append a compact TSV row for quick manual inspection."""
    results_path = runs_root / "results.tsv"
    if not results_path.exists():
        results_path.write_text(f"{RESULTS_HEADER}\n", encoding="utf-8")

    row = "\t".join([
        str(record.get("iteration", "")),
        str(record.get("decision", "")),
        format_pass_rate(record.get("pass_rate")),
        format_pass_rate(record.get("running_best")),
        format_pass_rate(record.get("delta")),
        "yes" if record.get("is_new_best") else "no",
        format_pass_rate(record.get("effective_epsilon")),
        format_pass_rate(record.get("stddev")),
        str(record.get("skill_lines_before", "")),
        str(record.get("skill_lines_after", "")),
        str(record.get("skill_line_delta", "")),
        str(record.get("stop_reason", "") or ""),
    ])
    with results_path.open("a", encoding="utf-8") as handle:
        handle.write(f"{row}\n")
    return results_path


def compute_skill_metrics(skill_path: Path) -> dict:
    """Measure current SKILL.md size so complexity growth is visible in history."""
    skill_file = skill_path / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")
    return {
        "line_count": len(content.splitlines()),
        "char_count": len(content),
    }


def get_latest_grading_summary(runs_root: Path, before_iteration: int) -> str:
    """Return the most recent grading summary text from an earlier iteration."""
    for candidate in sorted(runs_root.glob("iteration-*/grading_summary.txt"), key=lambda p: p.parent.name, reverse=True):
        try:
            iteration_num = int(candidate.parent.name.split("-")[1])
        except (IndexError, ValueError):
            continue
        if iteration_num < before_iteration:
            return candidate.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Git utilities
# ---------------------------------------------------------------------------

def git_head_ref(skill_path: Path) -> Optional[str]:
    """Return the current HEAD SHA for the target repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except Exception:
        return None


def git_snapshot(skill_path: Path, iteration: int, message: Optional[str] = None) -> Optional[str]:
    """
    Snapshot the current SKILL.md state and return the restore ref.

    The returned ref is the commit we should restore SKILL.md from if the
    experiment is rejected.
    """
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        print(f"[loop] ❌ SKILL.md not found at {skill_file}")
        return None

    msg = message or f"autoresearch iteration-{iteration} snapshot"

    try:
        add_result = subprocess.run(
            ["git", "add", "SKILL.md"],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        if add_result.returncode != 0:
            print(f"[loop] ❌ git add failed: {add_result.stderr}")
            return None

        commit_result = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        combined = (commit_result.stdout + commit_result.stderr).lower()
        if commit_result.returncode == 0:
            print(f"[loop] 📸 Snapshot created for iteration {iteration}")
        elif "nothing to commit" in combined or "nothing added" in combined:
            print(f"[loop] ℹ️  No new snapshot commit needed; reusing current HEAD")
        else:
            print(f"[loop] ❌ git commit failed: {commit_result.stderr}")
            return None

        head_ref = git_head_ref(skill_path)
        if not head_ref:
            print("[loop] ❌ Could not resolve HEAD after snapshot")
            return None
        return head_ref
    except Exception as exc:
        print(f"[loop] ❌ Git snapshot exception: {exc}")
        return None


def git_restore_skill(skill_path: Path, restore_ref: str) -> bool:
    """Restore SKILL.md to a known-good ref without touching unrelated files."""
    try:
        result = subprocess.run(
            ["git", "restore", "--source", restore_ref, "--staged", "--worktree", "--", "SKILL.md"],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            result = subprocess.run(
                ["git", "checkout", restore_ref, "--", "SKILL.md"],
                cwd=str(skill_path),
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                print(f"[loop] ⚠️  Restore failed: {result.stderr}")
                return False

        print(f"[loop] ↩️  Restored SKILL.md to snapshot {restore_ref[:8]}")
        return True
    except Exception as exc:
        print(f"[loop] ❌ Restore exception: {exc}")
        return False


# ---------------------------------------------------------------------------
# Autorelop: spawn subagent to propose an experimental idea
# ---------------------------------------------------------------------------

def build_autorelop_prompt(skill_path: Path, runs_root: Path, iteration: int) -> str:
    """Compose the autorelop prompt from the prompt file plus recent feedback."""
    agent_prompt_path = WORKSPACE_ROOT / "agents" / "autorelop.md"
    base_prompt = agent_prompt_path.read_text(encoding="utf-8").strip() if agent_prompt_path.exists() else ""
    history = load_json(runs_root / "history.json", {"iterations": []})
    latest_grading_summary = get_latest_grading_summary(runs_root, before_iteration=iteration)

    context_sections = []

    iterations = history.get("iterations", [])
    if iterations:
        lines = []
        for item in iterations[-5:]:
            idea = item.get("idea") or item.get("experimental_idea") or "(no description)"
            line = (
                f"- iter {item.get('iteration', '?')}: "
                f"pass_rate={format_pass_rate(item.get('pass_rate'))}, "
                f"decision={item.get('decision', '?')}, "
                f"idea={idea}"
            )
            if item.get("stop_reason"):
                line += f", stop_reason={item['stop_reason']}"
            lines.append(line)
        context_sections.append("## Recent Iteration History\n" + "\n".join(lines))

    if latest_grading_summary:
        context_sections.append("## Latest Grading Summary\n" + latest_grading_summary.strip())

    context_sections.append(
        "\n".join([
            "## Optimization Constraints",
            "- Optimize only `SKILL.md` in the target skill directory.",
            "- Treat `evals/evals.json` and the harness as fixed for this loop.",
            "- Prefer replacing or tightening existing instructions over appending new sections.",
            "- Avoid untested complexity growth unless the failing assertions clearly require it.",
        ])
    )

    context_text = "\n\n".join(section for section in context_sections if section)

    return f"""{base_prompt}

## Current Iteration
- iteration: {iteration}
- target_skill_dir: {skill_path}

{context_text}

Return ONLY the JSON proposal."""


def run_autorelop(skill_path: Path, runs_root: Path, iteration: int) -> Optional[dict]:
    """Spawn the autorelop subagent to propose one focused experiment."""
    prompt = build_autorelop_prompt(skill_path, runs_root, iteration)
    cmd = [
        "claude",
        "-p",
        prompt,
        "--output-format",
        "text",
        "--add-dir",
        str(skill_path),
    ]
    env = {key: value for key, value in os.environ.items() if key != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=120,
            cwd=str(skill_path),
            env=env,
        )
        stdout = result.stdout.strip()
    except subprocess.TimeoutExpired:
        print("[loop] ⚠️  autorelop timed out")
        return None
    except Exception as exc:
        print(f"[loop] ⚠️  autorelop failed: {exc}")
        return None

    json_match = re.search(r"\{[\s\S]*\}", stdout)
    if not json_match:
        print("[loop] ⚠️  autorelop did not return valid JSON")
        print(f"[loop]   Raw output: {stdout[:300]}")
        return None

    try:
        idea = json.loads(json_match.group())
    except json.JSONDecodeError as exc:
        print(f"[loop] ⚠️  autorelop JSON parse failed: {exc}")
        return None

    if "experimental_idea" not in idea or "changes" not in idea:
        print("[loop] ⚠️  autorelop returned invalid structure")
        return None

    return idea


# ---------------------------------------------------------------------------
# Apply changes to SKILL.md
# ---------------------------------------------------------------------------

def insert_after_location(content: str, location: str, proposed: str) -> tuple[str, bool]:
    """Insert proposed text immediately after a case-insensitive location match."""
    if not location:
        return content, False

    idx = content.lower().find(location.lower())
    if idx < 0:
        return content, False

    line_end = content.find("\n", idx)
    if line_end < 0:
        line_end = len(content)

    insertion = proposed.rstrip("\n")
    updated = content[: line_end + 1] + insertion + "\n" + content[line_end + 1 :]
    return updated, True


def apply_changes(skill_path: Path, changes: list[dict[str, Any]]) -> bool:
    """Apply proposed changes to SKILL.md using conservative text edits."""
    skill_file = skill_path / "SKILL.md"
    original_content = skill_file.read_text(encoding="utf-8")
    content = original_content
    applied_count = 0

    for change in changes:
        location = str(change.get("location", "") or "").strip()
        current = str(change.get("current", "") or "").strip()
        proposed = str(change.get("proposed", "") or "").rstrip()

        if not proposed:
            continue
        if current and current != "N/A" and current == proposed:
            continue

        applied = False

        if current and current != "N/A" and current in content:
            content = content.replace(current, proposed, 1)
            applied = True
        else:
            content, applied = insert_after_location(content, location, proposed)

        if not applied and proposed not in content:
            content = content.rstrip() + "\n\n" + proposed + "\n"
            applied = True

        if applied:
            applied_count += 1

    if content == original_content:
        print(f"[loop] ⚠️  Proposed changes were a no-op ({applied_count}/{len(changes)} applied)")
        return False

    skill_file.write_text(content, encoding="utf-8")
    print(f"[loop] ✅ Applied {applied_count}/{len(changes)} proposed changes to SKILL.md")
    return applied_count > 0


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------

def run_loop(
    skill_path: Path,
    max_iterations: int = 20,
    epsilon: float = 0.05,
    skip_revert: bool = False,
    watchdog_interval: int = 5,
    skip_permissions: bool = False,
) -> dict:
    """Run the full optimization loop."""
    skill_name = skill_path.name
    runs_root = resolve_runs_root(skill_path)
    runs_root.mkdir(parents=True, exist_ok=True)

    print(f"[loop] Starting autoresearch loop for: {skill_name}")
    print(
        f"[loop] Max iterations: {max_iterations}, "
        f"epsilon: {epsilon:.1%}, watchdog_interval: {watchdog_interval}"
    )

    history = load_history(runs_root, skill_name, skill_path, max_iterations, epsilon)
    running_best = history.get("running_best", 0.0)
    plateau_count = history.get("plateau_count", 0)
    consecutive_failures = 0
    iteration = 0

    while iteration < max_iterations:
        iteration += 1
        run_dir = runs_root / f"iteration-{iteration}"
        run_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'=' * 60}")
        print(f"[loop] === Iteration {iteration}/{max_iterations} ===")
        print(f"{'=' * 60}")

        skill_metrics_before = compute_skill_metrics(skill_path)
        snapshot_ref = git_snapshot(skill_path, iteration)
        if not snapshot_ref:
            consecutive_failures += 1
            print(f"[loop] ❌ Snapshot failed ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise SystemExit(1)
            continue

        print("[loop] Running autorelop agent...")
        idea = run_autorelop(skill_path, runs_root, iteration)
        if not idea:
            consecutive_failures += 1
            print(f"[loop] ⚠️  autorelop failed ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
            git_restore_skill(skill_path, snapshot_ref)
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise SystemExit(1)
            continue

        print(f"[loop] 💡 Experimental idea: {idea.get('experimental_idea', 'N/A')}")
        for idx, change in enumerate(idea.get("changes", []), 1):
            print(f"[loop]    Change {idx}: {change.get('location', '?')}")

        if not apply_changes(skill_path, idea.get("changes", [])):
            consecutive_failures += 1
            print(f"[loop] ⚠️  No usable changes applied ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
            git_restore_skill(skill_path, snapshot_ref)
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise SystemExit(1)
            continue

        skill_metrics_after = compute_skill_metrics(skill_path)
        idea["skill_metrics_before"] = skill_metrics_before
        idea["skill_metrics_after"] = skill_metrics_after
        save_json(run_dir / "idea_proposal.json", idea)

        print("[loop] Running harness...")
        harness_ok = run_harness(skill_path, iteration, run_dir, skip_permissions=skip_permissions)
        if not harness_ok:
            consecutive_failures += 1
            print(f"[loop] ⚠️  Harness failed ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
            git_restore_skill(skill_path, snapshot_ref)
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise SystemExit(1)
            continue

        benchmark_path = run_dir / "benchmark.json"
        if not benchmark_path.exists():
            consecutive_failures += 1
            print(f"[loop] ❌ Missing benchmark.json ({consecutive_failures}/{MAX_CONSECUTIVE_FAILURES})")
            git_restore_skill(skill_path, snapshot_ref)
            if consecutive_failures >= MAX_CONSECUTIVE_FAILURES:
                raise SystemExit(1)
            continue

        benchmark_payload = load_json(benchmark_path, {})
        benchmark = benchmark_payload.get("benchmark", {})
        quality = benchmark_payload.get("quality", {})
        current_pr = benchmark.get("mean_pass_rate")
        stddev = benchmark.get("stddev") or 0.0
        effective_epsilon = max(epsilon, 2 * stddev) if stddev else epsilon
        if effective_epsilon > epsilon:
            print(
                f"[loop] ℹ️  Effective epsilon this round: {effective_epsilon:.1%} "
                f"(base={epsilon:.1%}, stddev={stddev:.1%})"
            )

        consecutive_failures = 0

        if current_pr is None:
            decision = "revert"
            is_new_best = False
            delta = None
        else:
            delta = current_pr - running_best
            if current_pr > running_best + effective_epsilon:
                decision = "keep"
                is_new_best = True
            elif current_pr >= running_best - effective_epsilon:
                decision = "keep"
                is_new_best = False
            else:
                decision = "revert"
                is_new_best = False

        if decision == "keep":
            if is_new_best and current_pr is not None:
                running_best = current_pr
                plateau_count = 0
            else:
                plateau_count += 1
        else:
            plateau_count += 1

        watchdog_result = None
        watchdog_stop_reason = ""
        if watchdog_interval and iteration % watchdog_interval == 0:
            print("[loop] Running watchdog LLM Judge...")
            watchdog_result = run_watchdog(skill_path, run_dir, watchdog_interval)
            if watchdog_result:
                assessment = watchdog_result.get("judge", {}).get("assessment", "unknown")
                print(f"[loop] Watchdog assessment: {assessment}")
                if watchdog_result.get("judge", {}).get("should_stop"):
                    watchdog_stop_reason = watchdog_result["judge"].get("stop_reason", "watchdog stop")
                    print(f"[loop] 🐕 Watchdog recommends stop: {watchdog_stop_reason}")

        restored = False
        if decision == "keep":
            print(
                f"[loop] ✅ KEEP (pass_rate={format_pass_rate(current_pr)}, "
                f"best={format_pass_rate(running_best)})"
            )
        else:
            print(
                f"[loop] ↩️  REVERT (pass_rate={format_pass_rate(current_pr)} "
                f"vs best={format_pass_rate(running_best)})"
            )
            if skip_revert:
                print("[loop]    Dry run mode: leaving experimental change in place")
            else:
                restored = git_restore_skill(skill_path, snapshot_ref)

        stop_reason = ""
        if watchdog_stop_reason:
            stop_reason = f"Watchdog: {watchdog_stop_reason}"
        elif current_pr is None:
            stop_reason = "No valid grading"
        elif running_best >= 1.0:
            stop_reason = "Perfect score"
        elif plateau_count >= 3:
            stop_reason = "Plateau"
        elif iteration >= max_iterations:
            stop_reason = "Max iterations"

        record = {
            "iteration": iteration,
            "pass_rate": current_pr,
            "running_best": running_best,
            "decision": decision,
            "is_new_best": is_new_best,
            "delta": delta,
            "effective_epsilon": effective_epsilon,
            "stddev": stddev,
            "idea": idea.get("experimental_idea"),
            "benchmark_path": str(benchmark_path),
            "quality_score": quality.get("quality_score"),
            "quality_warnings": quality.get("warnings", []),
            "skill_lines_before": skill_metrics_before["line_count"],
            "skill_lines_after": skill_metrics_after["line_count"],
            "skill_line_delta": skill_metrics_after["line_count"] - skill_metrics_before["line_count"],
            "stop_reason": stop_reason or None,
            "restored": restored,
            "watchdog_assessment": (
                watchdog_result.get("judge", {}).get("assessment")
                if watchdog_result else None
            ),
        }
        history["iterations"].append(record)
        history["running_best"] = running_best
        history["plateau_count"] = plateau_count
        history["epsilon"] = epsilon
        history["last_effective_epsilon"] = effective_epsilon
        if stop_reason:
            history["stop_reason"] = stop_reason

        save_history(runs_root, history)
        append_results_row(runs_root, record)

        if stop_reason:
            print(f"[loop] 🛑 STOP: {stop_reason}")
            break

    print(f"\n[loop] ✅ Loop complete. Best pass_rate: {format_pass_rate(history['running_best'])}")
    return history


def run_harness(skill_path: Path, iteration: int, run_dir: Path, skip_permissions: bool = False) -> bool:
    """Run harness.py and aggregate.py for a single iteration."""
    harness_path = WORKSPACE_ROOT / "scripts" / "harness.py"
    cmd = [
        sys.executable,
        str(harness_path),
        "--skill-path",
        str(skill_path),
        "--iteration",
        str(iteration),
        "--runs-dir",
        str(run_dir.parent),
    ]
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=1800,
    )
    if result.returncode != 0:
        combined = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
        print(f"[loop] ⚠️  Harness failed: {combined[:600]}")
        return False

    aggregate_path = WORKSPACE_ROOT / "scripts" / "aggregate.py"
    aggregate_result = subprocess.run(
        [
            sys.executable,
            str(aggregate_path),
            "--run-dir",
            str(run_dir),
        ],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if aggregate_result.returncode != 0:
        combined = "\n".join(
            part for part in [aggregate_result.stdout.strip(), aggregate_result.stderr.strip()] if part
        )
        print(f"[loop] ⚠️  Aggregate failed: {combined[:600]}")
        return False

    return True


def run_watchdog(skill_path: Path, run_dir: Path, watchdog_interval: int = 5) -> Optional[dict]:
    """Run watchdog.py and return its saved report, if available."""
    watchdog_path = WORKSPACE_ROOT / "scripts" / "watchdog.py"
    result = subprocess.run(
        [
            sys.executable,
            str(watchdog_path),
            "--skill-path",
            str(skill_path),
            "--run-dir",
            str(run_dir),
            "--rounds-since",
            str(watchdog_interval),
            "--watchdog-interval",
            str(watchdog_interval),
        ],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode not in (0, 2):
        combined = "\n".join(part for part in [result.stdout.strip(), result.stderr.strip()] if part)
        print(f"[loop] ⚠️  Watchdog failed: {combined[:600]}")
        return None

    reports = sorted(run_dir.glob("watchdog_report_*.json"), key=lambda path: path.stat().st_mtime)
    if not reports:
        return None

    try:
        return json.loads(reports[-1].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Run the skill-autoresearch optimization loop")
    parser.add_argument(
        "--skill-path",
        type=Path,
        required=True,
        help="Path to the target skill directory",
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=20,
        help="Maximum iterations (default: 20)",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=0.05,
        help="Base epsilon for keep/revert decisions (default: 0.05)",
    )
    parser.add_argument(
        "--skip-revert",
        action="store_true",
        help="Skip actual file restore when an experiment is rejected",
    )
    parser.add_argument(
        "--watchdog-interval",
        type=int,
        default=5,
        help="Run watchdog every N iterations (default: 5, 0 disables it)",
    )
    parser.add_argument(
        "--single-iteration",
        type=int,
        default=None,
        help="Run at most N iterations total (legacy testing flag)",
    )
    parser.add_argument(
        "--dangerously-skip-permissions",
        action="store_true",
        help="Bypass permission checks for bash commands. Use when the skill runs scripts.",
    )
    args = parser.parse_args()

    if not args.skill_path.exists():
        print(f"Error: skill path does not exist: {args.skill_path}")
        return 1

    history = run_loop(
        skill_path=args.skill_path,
        max_iterations=args.single_iteration or args.max_iterations,
        epsilon=args.epsilon,
        skip_revert=args.skip_revert,
        watchdog_interval=args.watchdog_interval,
        skip_permissions=args.dangerously_skip_permissions,
    )

    print("\n=== Final Summary ===")
    print(f"Total iterations: {len(history['iterations'])}")
    print(f"Final running_best: {format_pass_rate(history['running_best'])}")
    if history.get("stop_reason"):
        print(f"Stop reason: {history['stop_reason']}")
    for item in history["iterations"]:
        print(
            f"  iter {item['iteration']}: {item['decision'].upper()} "
            f"({format_pass_rate(item.get('pass_rate'))}) - {item.get('idea', '')[:60]}"
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
