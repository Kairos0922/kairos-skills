#!/usr/bin/env python3
"""
scripts/decision.py — Keep/Revert Decision Logic

Implements the Running Best + epsilon greedy decision mechanism.

Decision rules:
  - if current_pass_rate > running_best + epsilon: KEEP (new best!)
  - if current_pass_rate >= running_best - epsilon: KEEP (within noise margin)
  - else: REVERT (worse than best)

Usage:
    python3 scripts/decision.py --run-dir <skill-path>-eval/iteration-<N> --benchmark benchmark.json
"""

import argparse
import json
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Decision logic
# ---------------------------------------------------------------------------

EPSILON_DEFAULT = 0.05  # 5% noise tolerance
PLATEAU_LIMIT = 3       # consecutive no-improvement iterations before stop
MAX_ITERATIONS = 50     # hard upper bound


def decide(
    current_pass_rate: float,
    running_best: float,
    epsilon: float = EPSILON_DEFAULT,
) -> dict:
    """
    Make a keep/revert/stop decision based on current vs running best pass_rate.

    Returns dict with:
      - decision: "keep" | "revert" | "stop"
      - is_new_best: bool
      - delta: float (current - running_best)
      - message: str
    """
    if current_pass_rate is None:
        return {
            "decision": "revert",  # Treat failed grading as revert
            "is_new_best": False,
            "delta": 0.0,
            "message": "No valid grading - treating as revert",
        }

    delta = current_pass_rate - running_best

    if delta > epsilon:
        # Significant improvement
        return {
            "decision": "keep",
            "is_new_best": True,
            "delta": delta,
            "message": f"New best! {current_pass_rate:.1%} > {running_best:.1%} + {epsilon:.1%}",
        }
    elif delta >= -epsilon:
        # Within noise margin - keep but not new best
        return {
            "decision": "keep",
            "is_new_best": False,
            "delta": delta,
            "message": f"Within noise margin. {current_pass_rate:.1%} vs best {running_best:.1%}",
        }
    else:
        # Worse than running best by more than epsilon
        return {
            "decision": "revert",
            "is_new_best": False,
            "delta": delta,
            "message": f"Revert. {current_pass_rate:.1%} < {running_best:.1%} - {epsilon:.1%} (delta={delta:.1%})",
        }


def should_stop(
    iteration: int,
    plateau_count: int,
    running_best: float,
    current_pass_rate: Optional[float],
    max_iterations: int = MAX_ITERATIONS,
    plateau_limit: int = PLATEAU_LIMIT,
) -> tuple[bool, str]:
    """
    Check if the optimization loop should stop.

    Returns (should_stop, reason).
    """
    if iteration >= max_iterations:
        return True, f"Hard stop: reached max iterations ({max_iterations})"

    if plateau_count >= plateau_limit:
        return True, f"Plateau: {plateau_count} consecutive iterations without improvement"

    if running_best >= 1.0:
        return True, "Perfect score achieved (100%)"

    if running_best >= 0.95:
        return True, f"Excellent score achieved ({running_best:.1%})"

    if current_pass_rate is None:
        return True, "No valid grading for multiple consecutive cases"

    return False, ""


def update_running_best(
    running_best: float,
    current_pass_rate: float,
    is_new_best: bool,
) -> float:
    """Update running best pass rate."""
    if is_new_best:
        return current_pass_rate
    return running_best


# ---------------------------------------------------------------------------
# History management
# ---------------------------------------------------------------------------

def load_history(run_dir: Path) -> dict:
    """Load history.json from run directory."""
    history_path = run_dir / "history.json"
    if history_path.exists():
        try:
            return json.loads(history_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass
    return {
        "iterations": [],
        "running_best": 0.0,
        "plateau_count": 0,
    }


def save_history(run_dir: Path, history: dict) -> Path:
    """Save history.json to run directory."""
    history_path = run_dir / "history.json"
    history_path.write_text(json.dumps(history, indent=2, ensure_ascii=False), encoding="utf-8")
    return history_path


def record_iteration(
    history: dict,
    iteration: int,
    benchmark: dict,
    decision_result: dict,
) -> dict:
    """Record an iteration in the history."""
    entry = {
        "iteration": iteration,
        "pass_rate": benchmark.get("mean_pass_rate"),
        "running_best": history.get("running_best", 0.0),
        "decision": decision_result["decision"],
        "is_new_best": decision_result["is_new_best"],
        "delta": decision_result["delta"],
        "per_case": [
            {
                "case_id": c.get("case_id"),
                "pass_rate": c.get("pass_rate"),
            }
            for c in benchmark.get("per_case", [])
        ],
        "quality_score": benchmark.get("quality", {}).get("quality_score", "unknown"),
    }
    history["iterations"].append(entry)
    return history


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Make keep/revert decision for an iteration")
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Path to run directory",
    )
    parser.add_argument(
        "--iteration",
        type=int,
        required=True,
        help="Current iteration number",
    )
    parser.add_argument(
        "--epsilon",
        type=float,
        default=EPSILON_DEFAULT,
        help=f"Epsilon value (default: {EPSILON_DEFAULT})",
    )
    parser.add_argument(
        "--skip-revert",
        action="store_true",
        help="Skip actual git revert (just show what would happen)",
    )
    args = parser.parse_args()

    run_dir = args.run_dir

    # Load history
    history = load_history(run_dir)
    running_best = history.get("running_best", 0.0)
    plateau_count = history.get("plateau_count", 0)

    # Load benchmark for current iteration
    benchmark_path = run_dir / "benchmark.json"
    if not benchmark_path.exists():
        print(f"[decision] ❌ No benchmark.json found at {benchmark_path}")
        print(f"[decision]    Cannot make decision without grading results")
        return 1

    benchmark = json.loads(benchmark_path.read_text(encoding="utf-8"))
    current_pr = benchmark.get("benchmark", {}).get("mean_pass_rate")

    if current_pr is None:
        print(f"[decision] ❌ No valid pass_rate in benchmark")
        return 1

    # Make decision
    decision_result = decide(current_pr, running_best, epsilon=args.epsilon)

    # Check stop conditions
    stop, stop_reason = should_stop(
        iteration=args.iteration,
        plateau_count=plateau_count,
        running_best=running_best,
        current_pass_rate=current_pr,
    )

    if stop:
        print(f"[decision] 🛑 STOP: {stop_reason}")
        decision_result = {"decision": "stop", "reason": stop_reason}
    else:
        print(f"[decision] Decision: {decision_result['decision'].upper()}")
        print(f"[decision] {decision_result['message']}")
        print(f"[decision] Current: {current_pr:.1%}, Best: {running_best:.1%}, Delta: {decision_result['delta']:+.1%}")

    # Update running best if keep
    if decision_result["decision"] == "keep":
        is_new_best = decision_result["is_new_best"]
        new_running_best = update_running_best(running_best, current_pr, is_new_best)

        if is_new_best:
            plateau_count = 0
            print(f"[decision] ⭐ New running best: {new_running_best:.1%}")
        else:
            plateau_count += 1
            print(f"[decision] Plateaus since improvement: {plateau_count}")

        running_best = new_running_best
    elif decision_result["decision"] == "revert":
        plateau_count += 1
        print(f"[decision] ↩️  Would revert (git reset --hard HEAD~1)")
        if not args.skip_revert:
            print(f"[decision]    Use --skip-revert to see this without executing")
        print(f"[decision] Plateaus since improvement: {plateau_count}")

    # Record in history
    history["running_best"] = running_best
    history["plateau_count"] = plateau_count
    record_iteration(history, args.iteration, benchmark.get("benchmark", {}), decision_result)
    save_history(run_dir, history)

    print(f"\n[decision] History updated: {run_dir / 'history.json'}")

    # Print decision for script consumption
    print(f"\n=== DECISION: {decision_result['decision'].upper()} ===")
    if decision_result['decision'] == 'stop':
        print(f"Reason: {stop_reason}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
