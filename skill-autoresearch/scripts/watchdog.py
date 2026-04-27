#!/usr/bin/env python3
"""
scripts/watchdog.py — LLM Judge Watchdog

Every N rounds, run a judge model to ask:
1. Is the skill actually improving?
2. Are the assertions measuring the right things?
3. Is the optimization drifting in the wrong direction?
"""

import argparse
import json
import os
import re
import subprocess
from pathlib import Path
from typing import Optional

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()


def format_pass_rate(value: Optional[float]) -> str:
    """Format pass rates safely for prompt context."""
    if value is None:
        return "N/A"
    return f"{value:.1%}"


def load_json(path: Path, default: Optional[dict] = None) -> dict:
    """Load a JSON file with a safe default."""
    if not path.exists():
        return default or {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return default or {}


def load_recent_grading_summary(run_dir: Path) -> str:
    """Read the grading summary created for the current iteration."""
    grading_summary_path = run_dir / "grading_summary.txt"
    if grading_summary_path.exists():
        return grading_summary_path.read_text(encoding="utf-8")
    return ""


def build_history_text(history: dict) -> str:
    """Render recent iteration history for the watchdog prompt."""
    iterations = history.get("iterations", [])
    recent = iterations[-5:] if len(iterations) >= 5 else iterations
    if not recent:
        return "No prior iteration history available."

    lines = []
    for item in recent:
        idea = item.get("idea") or item.get("experimental_idea") or "N/A"
        lines.append(
            f"Iteration {item.get('iteration', '?')}: "
            f"pass_rate={format_pass_rate(item.get('pass_rate'))}, "
            f"decision={item.get('decision', '?')}, "
            f"idea={idea}"
        )
    return "\n".join(lines)


def build_benchmark_text(run_dir: Path) -> str:
    """Render current benchmark stats for the watchdog prompt."""
    benchmark_payload = load_json(run_dir / "benchmark.json", {})
    benchmark = benchmark_payload.get("benchmark", {})
    quality = benchmark_payload.get("quality", {})
    if not benchmark:
        return "No benchmark.json available for this iteration."

    warnings = quality.get("warnings", [])
    warning_text = "; ".join(warnings) if warnings else "None"
    return "\n".join([
        f"mean_pass_rate: {format_pass_rate(benchmark.get('mean_pass_rate'))}",
        f"median_pass_rate: {format_pass_rate(benchmark.get('median_pass_rate'))}",
        f"stddev: {format_pass_rate(benchmark.get('stddev'))}",
        f"quality_score: {quality.get('quality_score', 'unknown')}",
        f"warnings: {warning_text}",
    ])


def run_llm_judge(skill_path: Path, run_dir: Path, history: dict) -> Optional[dict]:
    """Spawn the watchdog judge model."""
    history_text = build_history_text(history)
    skill_file = skill_path / "SKILL.md"
    skill_content = skill_file.read_text(encoding="utf-8")[:4000]
    grading_feedback = load_recent_grading_summary(run_dir)
    benchmark_text = build_benchmark_text(run_dir)

    prompt = f"""You are the watchdog judge for skill-autoresearch.

## Recent optimization history
{history_text}

## Current benchmark
{benchmark_text}

## Current SKILL.md excerpt
{skill_content}

## Current grading feedback
{grading_feedback or "No grading_summary.txt available for this iteration."}

## Your task
Evaluate whether the optimization is heading in the right direction.

Answer:
1. Is the skill measurably improving?
2. Are the assertions measuring the intended quality?
3. Has the optimization drifted from the skill's purpose?
4. Is complexity growing without evidence that the eval suite covers it?

Output ONLY this JSON:
{{
  "assessment": "good / marginal / poor",
  "skill_trajectory": "improving / stable / degrading / unclear",
  "assertion_quality": "good / some_issues / poor",
  "key_findings": ["finding 1", "finding 2"],
  "recommendations": ["recommendation 1", "recommendation 2"],
  "should_stop": true_or_false,
  "stop_reason": "reason if should_stop, otherwise null"
}}

Important:
- Be critical and concrete
- Prefer stopping if the loop is overfitting or drifting
- Flag complexity growth that is not reflected in the current assertions"""

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
        return {"error": "LLM Judge timed out"}
    except Exception as exc:
        return {"error": str(exc)}

    json_match = re.search(r"\{[\s\S]*\}", stdout)
    if not json_match:
        return {"error": "No JSON in LLM Judge output", "raw_output": stdout[:500]}

    try:
        return json.loads(json_match.group())
    except json.JSONDecodeError:
        return {"error": "JSON parse failed", "raw_output": stdout[:500]}


def check_assertion_coverage(assertions: list[str]) -> dict:
    """Approximate whether the eval suite covers structure, semantics, and quality."""
    structure_assertions = [item for item in assertions if any(
        keyword in item.lower()
        for keyword in ["存在", "包含", "格式", "字段", "数组", "结构", "必要字段"]
    )]
    semantic_assertions = [item for item in assertions if any(
        keyword in item.lower()
        for keyword in ["判断", "是否", "应该", "适当", "合理", "足够"]
    )]
    quality_assertions = [item for item in assertions if any(
        keyword in item.lower()
        for keyword in ["质量", "价值", "独特", "差异化", "differentiation"]
    )]

    issues = []
    if not structure_assertions:
        issues.append("No structure/format assertions found")
    if len(semantic_assertions) > 3:
        issues.append("Too many semantic assertions; likely noisy")
    if not quality_assertions:
        issues.append("No quality/differentiation assertions found")

    return {
        "structure_count": len(structure_assertions),
        "semantic_count": len(semantic_assertions),
        "quality_count": len(quality_assertions),
        "issues": issues,
        "coverage_score": "good" if not issues else "partial" if len(issues) == 1 else "poor",
    }


def run_watchdog(
    skill_path: Path,
    run_dir: Path,
    rounds_since: int,
    watchdog_interval: int = 5,
) -> dict:
    """Run the watchdog check and persist a report."""
    print(f"[watchdog] Running watchdog (rounds since last: {rounds_since})")

    history = load_json(run_dir.parent / "history.json", {"iterations": []})

    evals_file = skill_path / "evals" / "evals.json"
    evals_payload = load_json(evals_file, {})
    assertions: list[str] = []
    for case in evals_payload.get("evals", []):
        assertions.extend(case.get("assertions", []))

    coverage = check_assertion_coverage(assertions)
    judge_result = run_llm_judge(skill_path, run_dir, history)

    result = {
        "rounds_since_watchdog": rounds_since,
        "watchdog_interval": watchdog_interval,
        "coverage": coverage,
        "judge": judge_result,
    }

    watchdog_path = run_dir / f"watchdog_report_r{rounds_since}.json"
    watchdog_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[watchdog] Report saved: {watchdog_path}")

    assessment = judge_result.get("assessment", "unknown") if judge_result else "error"
    print(f"[watchdog] Assessment: {assessment}")
    for finding in (judge_result or {}).get("key_findings", [])[:3]:
        print(f"[watchdog]   - {finding}")

    should_stop = (judge_result or {}).get("should_stop", False)
    if should_stop:
        print(f"[watchdog] 🛑 Judge recommends stop: {judge_result.get('stop_reason', 'unknown')}")

    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run watchdog evaluation")
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
        help="Path to the current iteration directory",
    )
    parser.add_argument(
        "--rounds-since",
        type=int,
        default=5,
        help="Rounds since the last watchdog run",
    )
    parser.add_argument(
        "--watchdog-interval",
        type=int,
        default=5,
        help="Configured watchdog interval",
    )
    args = parser.parse_args()

    result = run_watchdog(
        skill_path=args.skill_path,
        run_dir=args.run_dir,
        rounds_since=args.rounds_since,
        watchdog_interval=args.watchdog_interval,
    )

    judge = result.get("judge", {})
    print("\n=== Watchdog Verdict ===")
    print(f"Assessment: {judge.get('assessment', 'unknown')}")
    print(f"Should stop: {judge.get('should_stop', False)}")

    if judge.get("should_stop"):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
