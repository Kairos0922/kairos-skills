#!/usr/bin/env python3
"""
scripts/aggregate.py — Result Aggregator

Responsibilities:
1. Read grading.json from each eval case in a run directory
2. Compute aggregate benchmark (mean pass_rate across cases)
3. Detect assertion quality issues (from eval_feedback.suggestions)
4. Output benchmark.json

Usage:
    python3 scripts/aggregate.py --run-dir runs/<skill>/iteration-<N>
"""

import argparse
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import Optional


WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
RUNS_ROOT = WORKSPACE_ROOT / "runs"


def normalize_pass_rate(pr: Optional[float]) -> Optional[float]:
    """
    Normalize pass_rate to 0-1 decimal range.

    The grader returns pass_rate as a decimal between 0.0 and 1.0 (e.g., 0.143 for 14.3%).
    Older runs may have stored percentages (e.g., 14.3 for 14.3%). Detect and normalize.
    """
    if pr is None:
        return None
    if pr < 0:
        return None
    # If > 1, assume it's a percentage (e.g., 14.3 means 14.3%)
    # 1.0 means 100% (all assertions passed), keep as-is
    if pr > 1:
        return pr / 100.0
    return pr


def find_eval_dirs(run_dir: Path) -> list[Path]:
    """Find all eval-* directories in a run directory."""
    eval_dirs = sorted(run_dir.glob("eval-*"), key=lambda p: p.name)
    return [d for d in eval_dirs if d.is_dir()]


def load_grading(eval_dir: Path) -> Optional[dict]:
    """Load grading.json from an eval directory."""
    grading_path = eval_dir / "grading.json"
    if not grading_path.exists():
        return None
    try:
        return json.loads(grading_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, IOError):
        return None


def compute_benchmark(run_dir: Path) -> dict:
    """
    Compute aggregate benchmark from all eval case grading results.

    Returns a dict with:
      - pass_rates: list of per-case pass rates
      - mean_pass_rate: float
      - median_pass_rate: float
      - stddev: float (population std dev)
      - total_passed: int
      - total_assertions: int
      - per_case: list of per-case details
      - eval_feedback_suggestions: aggregated suggestions from grader
    """
    eval_dirs = find_eval_dirs(run_dir)
    if not eval_dirs:
        return {
            "error": f"No eval directories found in {run_dir}",
            "pass_rates": [],
            "mean_pass_rate": None,
        }

    per_case = []
    pass_rates = []
    all_suggestions = []
    total_passed = 0
    total_assertions = 0

    for eval_dir in eval_dirs:
        grading = load_grading(eval_dir)
        if grading is None:
            per_case.append({
                "case_id": extract_case_id(eval_dir.name),
                "eval_dir": str(eval_dir),
                "grading_loaded": False,
                "pass_rate": None,
            })
            pass_rates.append(None)
            continue

        summary = grading.get("summary", {})
        raw_pass_rate = summary.get("pass_rate")
        pass_rate = normalize_pass_rate(raw_pass_rate)
        passed = summary.get("passed", 0)
        total = summary.get("total", 0)

        if pass_rate is not None:
            pass_rates.append(pass_rate)

        total_passed += passed
        total_assertions += total

        # Collect suggestions
        eval_feedback = grading.get("eval_feedback", {})
        suggestions = eval_feedback.get("suggestions", [])
        all_suggestions.extend(suggestions)

        # Per-assertion details
        expectations = grading.get("expectations", [])

        per_case.append({
            "case_id": extract_case_id(eval_dir.name),
            "eval_dir": str(eval_dir),
            "grading_loaded": True,
            "pass_rate": pass_rate,
            "raw_pass_rate": raw_pass_rate,
            "passed": passed,
            "total": total,
            "expectations": expectations,
            "suggestions": suggestions,
        })

    # Filter out None values for statistics
    valid_pass_rates = [pr for pr in pass_rates if pr is not None]

    if not valid_pass_rates:
        return {
            "error": "No valid grading results found",
            "pass_rates": pass_rates,
            "per_case": per_case,
            "mean_pass_rate": None,
        }

    mean_pr = statistics.mean(valid_pass_rates)
    stddev = statistics.stdev(valid_pass_rates) if len(valid_pass_rates) > 1 else 0.0
    median_pr = statistics.median(valid_pass_rates) if valid_pass_rates else None

    return {
        "pass_rates": pass_rates,
        "valid_case_count": len(valid_pass_rates),
        "mean_pass_rate": mean_pr,
        "median_pass_rate": median_pr,
        "stddev": stddev,
        "total_passed": total_passed,
        "total_assertions": total_assertions,
        "all_suggestions": all_suggestions,
        "per_case": per_case,
    }


def extract_case_id(eval_dir_name: str) -> int:
    """Extract case ID from eval directory name (e.g., 'eval-1' -> 1)."""
    try:
        return int(eval_dir_name.split("-")[1])
    except (IndexError, ValueError):
        return -1


def check_assertion_quality(benchmark: dict) -> dict:
    """
    Analyze assertion quality based on grader feedback.

    Returns quality assessment with warnings.
    """
    suggestions = benchmark.get("all_suggestions", [])
    stddev = benchmark.get("stddev", 0)
    per_case = benchmark.get("per_case", [])

    warnings = []
    quality_score = "good"  # good / marginal / poor

    # High variance warning
    if stddev >= 0.10:
        warnings.append(f"High variance across eval cases (stddev={stddev:.1%})")
        quality_score = "marginal"
    elif stddev >= 0.05:
        warnings.append(f"Moderate variance across eval cases (stddev={stddev:.1%})")
        if quality_score == "good":
            quality_score = "marginal"

    # Suggestion count warning
    if len(suggestions) > 3:
        warnings.append(f"Multiple assertion quality suggestions ({len(suggestions)} total)")
        quality_score = "marginal"

    # Check per-case for failures
    failed_cases = [
        c for c in per_case
        if c.get("grading_loaded") and c.get("pass_rate", 1.0) < 0.5
    ]
    if failed_cases:
        warnings.append(f"{len(failed_cases)} eval cases with pass_rate < 50%")
        if quality_score in ("good", "marginal"):
            quality_score = "marginal"

    # Check for borderline assertions (those that might cause noise)
    borderline_count = 0
    for case in per_case:
        for exp in case.get("expectations", []):
            text = exp.get("text", "").lower()
            evidence = exp.get("evidence", "").lower()
            # Check for borderline semantic language
            if any(word in text for word in ["可能", "也许", "是否", "够不够", "判断"]):
                borderline_count += 1

    if borderline_count > 0:
        warnings.append(f"{borderline_count} assertions with borderline semantic language")

    return {
        "quality_score": quality_score,
        "warnings": warnings,
        "suggestions": suggestions[:10],  # Top 10 most relevant
        "borderline_assertions": borderline_count,
    }


def save_benchmark(run_dir: Path, benchmark: dict, quality: dict) -> Path:
    """Save benchmark.json to run directory."""
    output = {
        "run_dir": str(run_dir),
        "benchmark": benchmark,
        "quality": quality,
        "timestamp": datetime.now().isoformat(),
    }
    output_path = run_dir / "benchmark.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    return output_path


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Aggregate eval case results into a benchmark"
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Path to run directory (e.g., runs/kairos-collect-signals/iteration-1)",
    )
    args = parser.parse_args()

    if not args.run_dir.exists():
        print(f"Error: run directory does not exist: {args.run_dir}")
        return 1

    print(f"[aggregate] Aggregating results from: {args.run_dir}")

    benchmark = compute_benchmark(args.run_dir)

    if "error" in benchmark and not benchmark.get("per_case"):
        print(f"[aggregate] Error: {benchmark['error']}")
        return 1

    quality = check_assertion_quality(benchmark)
    output_path = save_benchmark(args.run_dir, benchmark, quality)

    # Print summary
    mean_pr = benchmark.get("mean_pass_rate")
    stddev = benchmark.get("stddev", 0)
    valid = benchmark.get("valid_case_count", 0)
    total_cases = len(benchmark.get("per_case", []))

    print(f"\n=== Benchmark Summary ===")
    print(f"Eval cases: {valid}/{total_cases} with valid grading")
    if mean_pr is not None:
        print(f"Mean pass_rate: {mean_pr:.1%}")
        print(f"StdDev: {stddev:.1%}")
    print(f"Quality score: {quality['quality_score']}")
    if quality['warnings']:
        print(f"Warnings: {'; '.join(quality['warnings'])}")
    print(f"\nBenchmark saved: {output_path}")

    # Print per-case breakdown
    print(f"\n=== Per-Case Results ===")
    for case in benchmark.get("per_case", []):
        case_id = case.get("case_id", "?")
        pr = case.get("pass_rate")
        if pr is not None:
            print(f"  Case {case_id}: {pr:.1%} ({case.get('passed', 0)}/{case.get('total', 0)})")
        else:
            print(f"  Case {case_id}: no grading")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
