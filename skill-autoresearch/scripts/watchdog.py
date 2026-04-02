#!/usr/bin/env python3
"""
scripts/watchdog.py — LLM Judge Watchdog

Every N rounds (default: 5), runs an LLM Judge to evaluate:
1. Is the skill actually improving?
2. Are the assertions measuring the right things?
3. Is the optimization drifting in the wrong direction?

This is a safety net to catch systemic issues that the grader can't detect.

Usage:
    python3 scripts/watchdog.py --run-dir runs/<skill> --rounds-since-watchdog 5
"""

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()


def run_llm_judge(
    skill_path: Path,
    run_dir: Path,
    history: dict,
) -> Optional[dict]:
    """
    Spawn LLM Judge to evaluate the skill's optimization trajectory.
    """
    iterations = history.get("iterations", [])
    recent = iterations[-5:] if len(iterations) >= 5 else iterations

    # Build history summary for the judge
    history_text = "\n".join(
        f"Iteration {it['iteration']}: pass_rate={it.get('pass_rate', 'N/A'):.1%}, "
        f"decision={it.get('decision', '?')}, idea={it.get('idea', 'N/A')}"
        for it in recent
    )

    # Load the current SKILL.md
    skill_file = skill_path / "SKILL.md"
    skill_content = skill_file.read_text(encoding="utf-8")[:3000]  # Limit size

    # Load latest grading feedback
    grading_feedback = ""
    latest_eval = sorted(run_dir.glob("*/grading_summary.txt"), key=lambda p: p.stat().st_mtime)
    if latest_eval:
        grading_feedback = latest_eval[-1].read_text()[:1000]

    prompt = f"""You are the LLM Judge watchdog for skill-autoresearch.

## Recent optimization history (last {len(recent)} iterations):
{history_text}

## Current SKILL.md (excerpt):
{{skill_content}}

## Recent grading feedback:
{grading_feedback or 'No recent grading feedback available.'}

## Your task
Evaluate whether the skill optimization is heading in the RIGHT DIRECTION.

Answer these questions:
1. Is the skill measurably improving across iterations?
2. Are the assertions actually measuring quality, or are they measuring something irrelevant?
3. Has the optimization drifted away from the intended purpose of the skill?
4. Are there any assertions that are too easy/too hard?

## Output ONLY this JSON (no markdown fences):
{{
  "assessment": "good / marginal / poor",
  "skill_trajectory": "improving / stable / degrading / unclear",
  "assertion_quality": "good / some_issues / poor",
  "key_findings": ["finding 1", "finding 2", "finding 3"],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "should_stop": true_or_false,
  "stop_reason": "reason if should_stop, otherwise null"
}}

Important:
- Be honest and critical
- Look for patterns in the iteration history
- If pass_rate is consistently low, the assertions might be too strict
- If pass_rate is perfect, the assertions might be too loose"""

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
        return {"error": "LLM Judge timed out"}
    except Exception as e:
        return {"error": str(e)}

    # Extract JSON
    json_match = re.search(r'\{[\s\S]*\}', stdout)
    if not json_match:
        return {"error": "No JSON in LLM Judge output", "raw_output": stdout[:500]}

    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        return {"error": "JSON parse failed", "raw_output": stdout[:500]}


def check_assertion_coverage(
    run_dir: Path,
    assertions: list,
) -> dict:
    """
    Check if assertions cover the key aspects of the skill.
    """
    # Group assertions by type
    structure_assertions = [a for a in assertions if any(
        kw in a.lower() for kw in ["存在", "包含", "格式", "字段", "数组", "结构", "必要字段"]
    )]
    semantic_assertions = [a for a in assertions if any(
        kw in a.lower() for kw in ["判断", "是否", "应该", "适当", "合理", "足够"]
    )]
    quality_assertions = [a for a in assertions if any(
        kw in a.lower() for kw in ["质量", "价值", "独特", "差异化", "differentiation"]
    )]

    issues = []
    if len(structure_assertions) == 0:
        issues.append("No structure/format assertions found - skill might produce invalid output")
    if len(semantic_assertions) > 3:
        issues.append("Too many semantic assertions - these may have high variance")
    if len(quality_assertions) == 0:
        issues.append("No differentiation/quality assertions - might not catch low-quality output")

    return {
        "structure_count": len(structure_assertions),
        "semantic_count": len(semantic_assertions),
        "quality_count": len(quality_assertions),
        "issues": issues,
        "coverage_score": "good" if len(issues) == 0 else "partial" if len(issues) <= 1 else "poor",
    }


def run_watchdog(
    skill_path: Path,
    run_dir: Path,
    rounds_since: int,
    watchdog_interval: int = 5,
) -> dict:
    """
    Run watchdog check.
    """
    print(f"[watchdog] Running LLM Judge watchdog (rounds since last: {rounds_since})")

    # Load history
    history_path = run_dir.parent / "history.json"
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding="utf-8"))
    else:
        history = {"iterations": []}

    # Load evals to check assertion coverage
    evals_file = skill_path / "evals" / "evals.json"
    assertions = []
    if evals_file.exists():
        evals = json.loads(evals_file.read_text(encoding="utf-8"))
        for case in evals.get("evals", []):
            assertions.extend(case.get("assertions", []))

    coverage = check_assertion_coverage(run_dir, assertions)
    judge_result = run_llm_judge(skill_path, run_dir, history)

    result = {
        "rounds_since_watchdog": rounds_since,
        "watchdog_interval": watchdog_interval,
        "coverage": coverage,
        "judge": judge_result,
    }

    # Save watchdog report
    watchdog_path = run_dir / f"watchdog_report_r{rounds_since}.json"
    watchdog_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[watchdog] Report saved: {watchdog_path}")

    # Print summary
    assessment = judge_result.get("assessment", "unknown") if judge_result else "error"
    print(f"[watchdog] Assessment: {assessment}")

    findings = judge_result.get("key_findings", []) if judge_result else []
    for f in findings[:3]:
        print(f"[watchdog]   - {f}")

    should_stop = judge_result.get("should_stop", False) if judge_result else False
    if should_stop:
        reason = judge_result.get("stop_reason", "unknown")
        print(f"[watchdog] 🛑 LLM Judge recommends stopping: {reason}")

    return result


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Run watchdog LLM Judge evaluation")
    parser.add_argument(
        "--skill-path",
        type=Path,
        required=True,
        help="Path to the target skill directory",
    )
    parser.add_argument(
        "--run-dir",
        type=Path,
        required=True,
        help="Path to the run directory",
    )
    parser.add_argument(
        "--rounds-since",
        type=int,
        default=5,
        help="Rounds since last watchdog (default: 5)",
    )
    parser.add_argument(
        "--watchdog-interval",
        type=int,
        default=5,
        help="How often to run watchdog (default: 5)",
    )
    args = parser.parse_args()

    result = run_watchdog(
        skill_path=args.skill_path,
        run_dir=args.run_dir,
        rounds_since=args.rounds_since,
        watchdog_interval=args.watchdog_interval,
    )

    # Print final verdict
    judge = result.get("judge", {})
    assessment = judge.get("assessment", "unknown")
    should_stop = judge.get("should_stop", False)

    print(f"\n=== Watchdog Verdict ===")
    print(f"Assessment: {assessment}")
    print(f"Should stop: {should_stop}")

    if should_stop:
        return 2  # Special exit code for "stop the loop"

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
