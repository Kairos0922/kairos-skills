#!/usr/bin/env python3
"""
scripts/loop.py — Main Optimization Loop

Orchestrates the full edit → eval → keep/revert cycle.

Workflow per iteration:
1. Snapshot: git add + commit current SKILL.md
2. Idea: autorelop subagent proposes experimental idea
3. Apply: apply proposed changes to SKILL.md
4. Harness: run harness.py → get grading
5. Aggregate: run aggregate.py → get benchmark
6. Decision: run decision.py → keep/revert/stop
7. If revert: git reset --hard HEAD~1
8. If keep: continue to next iteration
9. If stop: exit

Usage:
    python3 scripts/loop.py --skill-path /path/to/target-skill --max-iterations 20
"""

import argparse
import json
import os
import subprocess
import sys
import re
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
RUNS_ROOT = WORKSPACE_ROOT / "runs"


# ---------------------------------------------------------------------------
# Git utilities
# ---------------------------------------------------------------------------

def git_snapshot(skill_path: Path, iteration: int, message: Optional[str] = None) -> bool:
    """
    Create a git snapshot of the current SKILL.md state.

    Runs: git add SKILL.md && git commit
    """
    skill_file = skill_path / "SKILL.md"
    if not skill_file.exists():
        print(f"[loop] ❌ SKILL.md not found at {skill_file}")
        return False

    msg = message or f"autoresearch iteration-{iteration} snapshot"

    try:
        # git add
        result = subprocess.run(
            ["git", "add", "SKILL.md"],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[loop] ⚠️  git add failed: {result.stderr}")
            # Maybe not a git repo - that's OK, skip snapshot
            return True

        # git commit
        result = subprocess.run(
            ["git", "commit", "-m", msg],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[loop] ⚠️  git commit failed: {result.stderr}")
            return True  # Don't fail the loop for this

        commit = result.stdout.strip()
        print(f"[loop] 📸 Snapshot created: {commit[:40]}")
        return True
    except Exception as e:
        print(f"[loop] ⚠️  Git snapshot failed: {e}")
        return True  # Don't fail the loop


def git_revert(skill_path: Path) -> bool:
    """
    Revert to the previous SKILL.md state via git reset --hard HEAD~1.
    If HEAD~1 doesn't exist (first commit), just undo changes manually.
    """
    try:
        # Check if HEAD~1 exists
        check = subprocess.run(
            ["git", "rev-parse", "HEAD~1"],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        if check.returncode != 0:
            print(f"[loop] ⚠️  Cannot revert: HEAD~1 doesn't exist (first commit)")
            return False

        result = subprocess.run(
            ["git", "reset", "--hard", "HEAD~1"],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"[loop] ❌ git revert failed: {result.stderr}")
            return False
        print(f"[loop] ↩️  Reverted to previous state")
        return True
    except Exception as e:
        print(f"[loop] ❌ git revert exception: {e}")
        return False


def git_is_dirty(skill_path: Path) -> bool:
    """Check if SKILL.md has uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            cwd=str(skill_path),
            capture_output=True,
            text=True,
        )
        return bool(result.stdout.strip())
    except:
        return False


# ---------------------------------------------------------------------------
# Autorelop: spawn subagent to propose experimental idea
# ---------------------------------------------------------------------------

def run_autorelop(skill_path: Path, run_dir: Path, iteration: int) -> Optional[dict]:
    """
    Spawn the autorelop subagent to propose an experimental idea.

    Returns the parsed JSON with changes, or None on failure.
    """
    # Prepare context files for the autorelop agent
    # 1. Grading summary (if exists from previous iteration)
    history_path = run_dir / "history.json"
    grading_summary_path = run_dir / "grading_summary.txt"

    context_parts = []

    # Add grading summary if available
    if grading_summary_path.exists():
        context_parts.append(f"\n\n## Previous Grading Feedback\n{grading_summary_path.read_text()}")

    # Add history if available
    if history_path.exists():
        try:
            history = json.loads(history_path.read_text())
            iterations = history.get("iterations", [])
            if iterations:
                context_parts.append(f"\n\n## Iteration History\n")
                for it in iterations[-5:]:  # last 5
                    pr = it.get("pass_rate")
                    decision = it.get("decision", "?")
                    idea = it.get("experimental_idea", "(no description)")
                    context_parts.append(
                        f"  iter {it['iteration']}: pass_rate={pr:.1% if pr else 'N/A'}, decision={decision}"
                    )
        except:
            pass

    context = "".join(context_parts)

    prompt = f"""You are the autorelop agent for skill-autoresearch iteration {iteration}.

{context}

## Your task
1. Read SKILL.md in your current directory
2. Propose ONE experimental idea (2-4 related changes serving one goal)
3. Output ONLY this JSON:

{{
  "experimental_idea": "brief description of the goal",
  "changes": [
    {{
      "location": "where to change (section/line)",
      "current": "current text (or N/A)",
      "proposed": "new text",
      "reason": "why this helps"
    }}
  ],
  "expected_impact": "expected result",
  "risks": ["risk1", "risk2"]
}}

IMPORTANT: Output ONLY the JSON. No markdown fences, no explanation."""

    # Run via claude -p with autorelop agent
    cmd = [
        "claude", "-p", prompt,
        "--output-format", "text",
        "--add-dir", str(skill_path),
    ]
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

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
        print(f"[loop] ⚠️  autorelop timed out")
        return None
    except Exception as e:
        print(f"[loop] ⚠️  autorelop failed: {e}")
        return None

    # Extract JSON
    json_match = re.search(r'\{[\s\S]*\}', stdout)
    if not json_match:
        print(f"[loop] ⚠️  autorelop didn't return valid JSON")
        print(f"[loop]   Raw output: {stdout[:300]}")
        return None

    try:
        idea = json.loads(json_match.group())
        # Validate structure
        if "changes" not in idea or "experimental_idea" not in idea:
            print(f"[loop] ⚠️  autorelop returned invalid structure")
            return None
        return idea
    except json.JSONDecodeError as e:
        print(f"[loop] ⚠️  autorelop JSON parse failed: {e}")
        return None


# ---------------------------------------------------------------------------
# Apply changes to SKILL.md
# ---------------------------------------------------------------------------

def apply_changes(skill_path: Path, changes: list) -> bool:
    """
    Apply proposed changes to SKILL.md.

    Each change has: location, current, proposed, reason.
    """
    skill_file = skill_path / "SKILL.md"
    content = skill_file.read_text(encoding="utf-8")

    lines = content.split("\n")
    applied = 0

    for change in changes:
        location = change.get("location", "")
        current = change.get("current", "")
        proposed = change.get("proposed", "")

        if not proposed:
            continue

        # Simple line-based replacement
        # Try to find "current" text in the content
        if current and current != "N/A" and current in content:
            # Replace first occurrence with context
            content = content.replace(current, proposed, 1)
            applied += 1
        elif proposed:
            # Just append to the end or find location
            if location.lower() in content.lower():
                # Insert after the location section
                idx = content.lower().find(location.lower())
                # Find end of that line
                endline = content.find("\n", idx)
                if endline > 0:
                    content = content[:endline + 1] + proposed + "\n" + content[endline + 1:]
                    applied += 1
            else:
                # Append at the end
                content = content.rstrip() + "\n\n" + proposed + "\n"
                applied += 1

    skill_file.write_text(content, encoding="utf-8")
    print(f"[loop] ✅ Applied {applied}/{len(changes)} changes to SKILL.md")
    return applied > 0


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
    """
    Run the full optimization loop.
    """
    skill_name = skill_path.name
    print(f"[loop] Starting authorsearch loop for: {skill_name}")
    print(f"[loop] Max iterations: {max_iterations}, epsilon: {epsilon}, watchdog_interval: {watchdog_interval}")

    # Initialize run directory
    iteration = 0
    running_best = 0.0
    plateau_count = 0
    consecutive_failures = 0
    history = {
        "skill_name": skill_name,
        "skill_path": str(skill_path),
        "max_iterations": max_iterations,
        "epsilon": epsilon,
        "iterations": [],
        "running_best": 0.0,
        "plateau_count": 0,
    }

    while iteration < max_iterations:
        iteration += 1
        print(f"\n{'='*60}")
        print(f"[loop] === Iteration {iteration}/{max_iterations} ===")
        print(f"{'='*60}")

        # New behavior: put runs alongside the skill being tested (sibling directory)
        # e.g., /path/to/kairos-collect-signals-eval/iteration-1/
        skill_runs_root = Path(str(skill_path) + "-eval").resolve()
        run_dir = skill_runs_root / f"iteration-{iteration}"
        run_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Git snapshot BEFORE making changes
        if not git_snapshot(skill_path, iteration):
            print(f"[loop] ❌ Snapshot failed, aborting iteration")
            continue

        # Step 2: Run autorelop to get experimental idea
        print(f"[loop] Running autorelop agent...")
        idea = run_autorelop(skill_path, run_dir, iteration)
        if not idea:
            consecutive_failures += 1
            print(f"[loop] ⚠️  autorelop failed ({consecutive_failures}/3), skipping to next iteration")
            git_revert(skill_path)  # Undo any partial changes
            if consecutive_failures >= 3:
                print(f"[loop] ❌ CRASH: {consecutive_failures} consecutive failures — exiting")
                sys.exit(1)
            continue

        print(f"[loop] 💡 Experimental idea: {idea.get('experimental_idea', 'N/A')}")
        for i, change in enumerate(idea.get("changes", []), 1):
            print(f"[loop]    Change {i}: {change.get('location', '?')}")

        # Step 3: Apply changes
        changes = idea.get("changes", [])
        if not apply_changes(skill_path, changes):
            consecutive_failures += 1
            print(f"[loop] ⚠️  No changes applied ({consecutive_failures}/3), skipping iteration")
            git_revert(skill_path)
            if consecutive_failures >= 3:
                print(f"[loop] ❌ CRASH: {consecutive_failures} consecutive failures — exiting")
                sys.exit(1)
            continue

        # Save idea proposal
        idea_path = run_dir / "idea_proposal.json"
        idea_path.write_text(json.dumps(idea, indent=2, ensure_ascii=False), encoding="utf-8")

        # Step 4: Run harness
        print(f"[loop] Running harness...")
        harness_ok = run_harness(skill_path, iteration, run_dir, skip_permissions=skip_permissions)
        if not harness_ok:
            consecutive_failures += 1
            print(f"[loop] ⚠️  Harness failed ({consecutive_failures}/3), reverting")
            git_revert(skill_path)
            if consecutive_failures >= 3:
                print(f"[loop] ❌ CRASH: {consecutive_failures} consecutive failures — exiting")
                sys.exit(1)
            continue

        # Step 5: Run aggregate
        print(f"[loop] Running aggregate...")
        benchmark_path = run_dir / "benchmark.json"
        if not benchmark_path.exists():
            consecutive_failures += 1
            print(f"[loop] ❌ No benchmark.json after harness ({consecutive_failures}/3)")
            git_revert(skill_path)
            if consecutive_failures >= 3:
                print(f"[loop] ❌ CRASH: {consecutive_failures} consecutive failures — exiting")
                sys.exit(1)
            continue

        # Step 6: Run decision
        print(f"[loop] Making decision...")
        benchmark = json.loads(benchmark_path.read_text())
        current_pr = benchmark.get("benchmark", {}).get("mean_pass_rate")

        # Auto-compute epsilon from grading variance if stddev is significant
        stddev = benchmark.get("benchmark", {}).get("stddev", 0)
        if stddev > 0:
            computed_epsilon = max(epsilon, 2 * stddev)
            if computed_epsilon > epsilon:
                print(f"[loop] ℹ️  Epsilon auto-adjusted: {epsilon:.1%} → {computed_epsilon:.1%} (2× stddev={stddev:.1%})")
                epsilon = computed_epsilon

        # Make decision
        consecutive_failures = 0  # Reset on successful iteration
        delta = (current_pr or 0) - running_best
        if current_pr is not None and current_pr >= running_best + epsilon:
            decision = "keep"
            is_new_best = delta > epsilon
        elif current_pr is not None and current_pr >= running_best - epsilon:
            decision = "keep"
            is_new_best = False
        else:
            decision = "revert"
            is_new_best = False

        # Update running_best before stop check (so even if we stop, best is recorded)
        plateau_count = 0 if is_new_best else plateau_count + 1
        running_best = current_pr if is_new_best else running_best

        # Step 6: Run watchdog every watchdog_interval rounds
        watchdog_triggered = False
        watchdog_reason = ""
        if iteration > 0 and iteration % watchdog_interval == 0:
            print(f"[loop] Running watchdog LLM Judge...")
            watchdog_result = run_watchdog(skill_path, run_dir, iteration, watchdog_interval)
            if watchdog_result:
                assessment = watchdog_result.get("judge", {}).get("assessment", "unknown")
                should_stop = watchdog_result.get("judge", {}).get("should_stop", False)
                print(f"[loop] Watchdog assessment: {assessment}")
                if should_stop:
                    watchdog_triggered = True
                    watchdog_reason = watchdog_result.get("judge", {}).get("stop_reason", "watchdog stop")
                    print(f"[loop] 🐕 Watchdog recommends STOP: {watchdog_reason}")

        # Check stop conditions
        stop = False
        stop_reason = ""
        if watchdog_triggered:
            stop = True
            stop_reason = f"Watchdog: {watchdog_reason}"
        elif running_best >= 1.0:
            stop = True
            stop_reason = "Perfect score"
        elif plateau_count >= 3:
            stop = True
            stop_reason = "Plateau"
        elif iteration >= max_iterations:
            stop = True
            stop_reason = "Max iterations"
        elif current_pr is None:
            stop = True
            stop_reason = "No valid grading"

        if stop:
            print(f"[loop] 🛑 STOP: {stop_reason}")
            decision = "stop"
            history["iterations"].append({
                "iteration": iteration,
                "pass_rate": current_pr,
                "running_best": running_best,
                "decision": decision,
                "reason": stop_reason,
                "idea": idea.get("experimental_idea"),
            })
            break

        # Record iteration
        if decision == "keep":
            print(f"[loop] ✅ KEEP (pass_rate={current_pr:.1%}, best={running_best:.1%})")
            history["iterations"].append({
                "iteration": iteration,
                "pass_rate": current_pr,
                "running_best": running_best,
                "decision": "keep",
                "is_new_best": is_new_best,
                "idea": idea.get("experimental_idea"),
            })
        else:
            print(f"[loop] ↩️  REVERT (pass_rate={current_pr:.1%} < {running_best:.1%})")
            if not skip_revert:
                git_revert(skill_path)
            history["iterations"].append({
                "iteration": iteration,
                "pass_rate": current_pr,
                "running_best": running_best,
                "decision": "revert",
                "idea": idea.get("experimental_idea"),
            })

        history["running_best"] = running_best
        history["plateau_count"] = plateau_count
        history["epsilon"] = epsilon  # May have been auto-computed from stddev

        # Save history
        history_path = run_dir.parent / "history.json"
        history_path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"\n[loop] ✅ Loop complete. Best pass_rate: {running_best:.1%}")
    return history


def run_harness(skill_path: Path, iteration: int, run_dir: Path, skip_permissions: bool = False) -> bool:
    """Run harness.py and aggregate.py. Return success status."""
    script_path = WORKSPACE_ROOT / "scripts" / "harness.py"

    # Step 1: Run harness
    cmd = [
        sys.executable, str(script_path),
        "--skill-path", str(skill_path),
        "--iteration", str(iteration),
    ]
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
    )
    if result.returncode != 0:
        print(f"[loop] ⚠️  Harness failed: {result.stderr[:200]}")
        return False

    # Step 2: Run aggregate
    aggregate_path = WORKSPACE_ROOT / "scripts" / "aggregate.py"
    result = subprocess.run(
        [sys.executable, str(aggregate_path),
         "--run-dir", str(run_dir)],
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        print(f"[loop] ⚠️  Aggregate failed: {result.stderr[:200]}")
        return False

    return True


def run_watchdog(
    skill_path: Path,
    run_dir: Path,
    iteration: int,
    watchdog_interval: int = 5,
) -> Optional[dict]:
    """
    Run watchdog.py and return the watchdog result dict, or None on failure.
    """
    watchdog_path = WORKSPACE_ROOT / "scripts" / "watchdog.py"
    result = subprocess.run(
        [sys.executable, str(watchdog_path),
         "--skill-path", str(skill_path),
         "--run-dir", str(run_dir),
         "--rounds-since", str(watchdog_interval),
         "--watchdog-interval", str(watchdog_interval)],
        capture_output=True,
        text=True,
        timeout=180,
    )
    if result.returncode not in (0, 2):
        # exit code 2 means "stop the loop" — still return the result
        print(f"[loop] ⚠️  Watchdog failed: {result.stderr[:200]}")
        return None

    # Parse watchdog result from stdout or find the report
    # The watchdog script saves a report to run_dir/watchdog_report_r{N}.json
    watchdog_reports = sorted(run_dir.glob("watchdog_report_*.json"), key=lambda p: p.stat().st_mtime)
    if watchdog_reports:
        latest = watchdog_reports[-1]
        try:
            return json.loads(latest.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass

    return None


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
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
        help="Epsilon for keep/revert decision (default: 0.05)",
    )
    parser.add_argument(
        "--skip-revert",
        action="store_true",
        help="Skip actual git revert (dry run mode)",
    )
    parser.add_argument(
        "--watchdog-interval",
        type=int,
        default=5,
        help="Run watchdog every N iterations (default: 5, 0 to disable)",
    )
    parser.add_argument(
        "--single-iteration",
        type=int,
        default=None,
        help="Run only this iteration number (for testing)",
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

    # Print final summary
    print(f"\n=== Final Summary ===")
    print(f"Total iterations: {len(history['iterations'])}")
    print(f"Final running_best: {history['running_best']:.1%}")
    for it in history["iterations"]:
        pr = it.get("pass_rate")
        decision = it["decision"].upper()
        idea = it.get("idea", "")[:50]
        pr_str = f"{pr:.1%}" if pr is not None else "N/A"
        print(f"  iter {it['iteration']}: {decision} ({pr_str}) - {idea}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
