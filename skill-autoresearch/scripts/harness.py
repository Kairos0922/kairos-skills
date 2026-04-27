#!/usr/bin/env python3
"""
scripts/harness.py — Evaluation Harness

Responsibilities:
1. For each eval case in evals/evals.json:
   a. Spawn executor subagent → run skill → save output artifacts
   b. Spawn grader subagent → grade output → grading.json
   c. Save metrics.json for the case
2. Write harness_summary.json + grading_summary.txt for the iteration

Usage:
    python3 scripts/harness.py --skill-path /path/to/target-skill --iteration 1
"""

import argparse
import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
RUNS_ROOT = WORKSPACE_ROOT / "runs"


def set_runs_root_from_skill(skill_path: Path) -> None:
    """Store run artifacts alongside the skill being evaluated."""
    global RUNS_ROOT
    RUNS_ROOT = Path(f"{skill_path}-eval").resolve()


def get_run_dir(iteration: int) -> Path:
    """Return the iteration directory under the configured RUNS_ROOT."""
    run_dir = RUNS_ROOT / f"iteration-{iteration}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def get_eval_dir(run_dir: Path, case_id: int) -> Path:
    """Return a per-case directory for iteration artifacts."""
    eval_dir = run_dir / f"eval-{case_id}"
    eval_dir.mkdir(parents=True, exist_ok=True)
    return eval_dir


def format_pass_rate(value: Optional[float]) -> str:
    """Format pass rates for logs and summary text."""
    if value is None:
        return "N/A"
    return f"{value:.1%}"


def clip(text: str, limit: int = 180) -> str:
    """Trim long evidence strings for readable summaries."""
    text = (text or "").strip().replace("\n", " ")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def load_json(path: Path) -> Optional[dict]:
    """Load a JSON file if it exists."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


# ---------------------------------------------------------------------------
# Input preparation
# ---------------------------------------------------------------------------

def write_eval_inputs(skill_path: Path, eval_case: dict) -> None:
    """
    Prepare case-specific input files.

    If the case defines `signals`, write them to `.kairos-temp/signals.json`.
    Otherwise remove any stale file from the previous case.
    """
    signals_file = skill_path / ".kairos-temp" / "signals.json"
    signals = eval_case.get("signals")

    if signals is not None:
        signals_file.parent.mkdir(parents=True, exist_ok=True)
        signals_file.write_text(
            json.dumps({"signals": signals}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    elif signals_file.exists():
        signals_file.unlink()


def clear_eval_inputs(skill_path: Path) -> None:
    """Delete transient eval inputs after the harness completes."""
    signals_file = skill_path / ".kairos-temp" / "signals.json"
    if signals_file.exists():
        signals_file.unlink()


def unwrap_skill_output(payload: Optional[dict]) -> Any:
    """
    Extract the actual skill output from the executor envelope.

    The executor is asked to return:
      {"skill_output": ..., "execution_notes": "..."}
    For grading we want the inner `skill_output` payload.
    """
    if isinstance(payload, dict) and "skill_output" in payload:
        return payload.get("skill_output")
    return payload


# ---------------------------------------------------------------------------
# Subagent spawning
# ---------------------------------------------------------------------------

def spawn_executor(
    skill_path: Path,
    eval_case: dict,
    eval_dir: Path,
    timeout: int = 180,
    skip_permissions: bool = False,
) -> dict:
    """Execute the target skill for one eval case."""
    start_time = time.time()
    write_eval_inputs(skill_path, eval_case)

    prompt = build_executor_prompt(eval_case)
    output_text, returncode = run_claude_p(
        prompt=prompt,
        skill_path=skill_path,
        timeout=timeout,
        skip_permissions=skip_permissions,
    )
    duration = time.time() - start_time

    output_path = eval_dir / "output.json"
    output_path.write_text(output_text or "", encoding="utf-8")

    if returncode != 0 or not output_text.strip():
        return {
            "success": False,
            "output_json": None,
            "raw_output_json": None,
            "output_path": str(output_path),
            "duration": duration,
            "error": f"non-zero exit {returncode}" if returncode != 0 else "empty output",
        }

    parsed = extract_json(output_text)
    if parsed is None:
        return {
            "success": False,
            "output_json": None,
            "raw_output_json": None,
            "output_path": str(output_path),
            "duration": duration,
            "error": "output was not valid JSON",
        }

    core_output = unwrap_skill_output(parsed)
    if isinstance(parsed, dict) and "skill_output" in parsed:
        envelope_path = eval_dir / "output.envelope.json"
        envelope_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")

    if core_output is not None:
        structured_path = eval_dir / "output.structured.json"
        structured_path.write_text(json.dumps(core_output, indent=2, ensure_ascii=False), encoding="utf-8")

    return {
        "success": core_output is not None,
        "output_json": core_output,
        "raw_output_json": parsed,
        "output_path": str(output_path),
        "duration": duration,
        "error": None if core_output is not None else "skill_output was null",
    }


def build_executor_prompt(eval_case: dict) -> str:
    """Build the prompt for the executor subagent."""
    case_id = eval_case.get("id", "?")
    user_request = eval_case.get("prompt", "")
    has_signals = eval_case.get("signals") is not None

    signals_note = (
        "Signals have been pre-written to `.kairos-temp/signals.json` for this eval case. "
        "Follow SKILL.md: if that file exists, skip any collection step and use the pre-provided signals."
    ) if has_signals else ""

    return f"""You are executing a skill for evaluation (case {case_id}).

## Your task
1. Read SKILL.md in your current directory
2. Execute the skill with this user request:
   "{user_request}"
{f"## Input note\n{signals_note}" if signals_note else ""}

## Important constraints
- Execute the skill exactly as described in SKILL.md
- Do NOT ask for confirmation or clarification
- Do NOT explain what you are doing

## Output
Return ONLY this JSON (no markdown fences):
{{
  "skill_output": {{...the full structured output from the skill...}},
  "execution_notes": "brief notes on execution"
}}

If the skill fails, return:
{{
  "skill_output": null,
  "execution_notes": "what went wrong"
}}"""


def spawn_grader(
    skill_path: Path,
    eval_case: dict,
    output_json: Any,
    eval_dir: Path,
    timeout: int = 60,
    skip_permissions: bool = False,
) -> dict:
    """Grade one eval case against its assertions."""
    start_time = time.time()
    prompt = build_grader_prompt(eval_case, output_json)

    output_text, returncode = run_claude_p(
        prompt=prompt,
        skill_path=skill_path,
        timeout=timeout,
        skip_permissions=skip_permissions,
    )
    duration = time.time() - start_time

    if returncode != 0 or not output_text.strip():
        return {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "pass_rate": None,
            "expectations": [],
            "eval_feedback": {},
            "duration": duration,
            "error": f"non-zero exit {returncode}" if returncode != 0 else "empty output",
        }

    grading = extract_json(output_text)
    if grading is None:
        raw_path = eval_dir / "grading.raw.txt"
        raw_path.write_text(output_text, encoding="utf-8")
        return {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "pass_rate": None,
            "expectations": [],
            "eval_feedback": {},
            "duration": duration,
            "error": "grader did not return valid JSON",
        }

    grading_path = eval_dir / "grading.json"
    grading_path.write_text(json.dumps(grading, indent=2, ensure_ascii=False), encoding="utf-8")

    summary = grading.get("summary", {})
    raw_pass_rate = summary.get("pass_rate")
    return {
        "passed": summary.get("passed", 0),
        "failed": summary.get("failed", 0),
        "total": summary.get("total", 0),
        "pass_rate": normalize_pass_rate(raw_pass_rate),
        "raw_pass_rate": raw_pass_rate,
        "expectations": grading.get("expectations", []),
        "eval_feedback": grading.get("eval_feedback", {}),
        "duration": duration,
        "error": None,
    }


def build_grader_prompt(eval_case: dict, output_json: Any) -> str:
    """Build the prompt for the grader subagent."""
    case_id = eval_case.get("id", "?")
    assertions = eval_case.get("assertions", [])
    expected_output = eval_case.get("expected_output", "")
    output_str = json.dumps(output_json, ensure_ascii=False, indent=2) if output_json is not None else '{"error": "no output to grade"}'
    assertions_text = "\n".join(f"- {assertion}" for assertion in assertions)

    return f"""You are evaluating a skill's output against assertions.

## Eval Case ID
{case_id}

## Expected output
{expected_output or "Not provided."}

## Assertions to check
{assertions_text}

## Skill output (JSON)
{output_str}

## Instructions
1. Check each assertion against the JSON output
2. Output ONLY this JSON (no markdown fences):
{{
  "expectations": [
    {{"text": "full assertion text", "passed": true_or_false, "evidence": "what you found"}}
  ],
  "summary": {{"passed": N, "failed": M, "total": K, "pass_rate": 0.0_to_1.0}},
  "eval_feedback": {{"suggestions": []}}
}}

## Important
- pass_rate must be a decimal between 0.0 and 1.0
- passed + failed must equal total
- total is the number of assertions checked"""


def run_claude_p(
    prompt: str,
    skill_path: Path,
    timeout: int = 60,
    skip_permissions: bool = False,
) -> tuple[str, int]:
    """Run `claude -p` in the target skill directory."""
    cmd = ["claude", "-p", prompt, "--output-format", "text", "--add-dir", str(skill_path)]
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    env = {key: value for key, value in os.environ.items() if key != "CLAUDECODE"}

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(skill_path),
            env=env,
        )
        return result.stdout.strip(), result.returncode
    except subprocess.TimeoutExpired:
        return "", -1
    except Exception as exc:
        return f'{{"error": "{str(exc)}"}}', 1


# ---------------------------------------------------------------------------
# JSON helpers
# ---------------------------------------------------------------------------

def normalize_pass_rate(value: Optional[float]) -> Optional[float]:
    """Normalize pass_rate values into the 0-1 range."""
    if value is None:
        return None
    if value < 0:
        return None
    if value > 1:
        return value / 100.0
    return value


def extract_json(text: str) -> Optional[dict]:
    """
    Extract a JSON object from free-form model output.

    We try a few increasingly permissive strategies because the CLI may prepend
    explanatory text even when asked not to.
    """
    if not text or not text.strip():
        return None

    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    cleaned = re.sub(r"^```json\s*", "", text.strip())
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    decoder = json.JSONDecoder()
    for index, char in enumerate(text):
        if char != "{":
            continue
        try:
            parsed, _ = decoder.raw_decode(text[index:])
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            continue

    return None


# ---------------------------------------------------------------------------
# Summary generation
# ---------------------------------------------------------------------------

def build_grading_summary(iteration: int, results: dict[int, dict]) -> str:
    """Create a compact text summary for autorelop and watchdog consumption."""
    lines = [
        f"Iteration {iteration} grading summary",
        "",
    ]

    for case_id in sorted(results):
        result = results[case_id]
        case = result["case"]
        exec_result = result["execution"]
        grading = result["grading"]
        case_name = case.get("name", case.get("prompt", f"case-{case_id}"))
        passed = grading.get("passed", 0)
        total = grading.get("total", 0)

        lines.append(
            f"Case {case_id} - {case_name}: pass_rate={format_pass_rate(grading.get('pass_rate'))} "
            f"({passed}/{total})"
        )

        if exec_result.get("error"):
            lines.append(f"  execution_error: {clip(exec_result['error'])}")
        if grading.get("error"):
            lines.append(f"  grading_error: {clip(grading['error'])}")

        failed_assertions = [
            expectation
            for expectation in grading.get("expectations", [])
            if not expectation.get("passed")
        ]
        for expectation in failed_assertions[:3]:
            lines.append(
                f"  fail: {clip(expectation.get('text', ''))} | evidence: {clip(expectation.get('evidence', ''))}"
            )

        for suggestion in grading.get("eval_feedback", {}).get("suggestions", [])[:2]:
            lines.append(f"  suggestion: {clip(suggestion)}")

        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def save_case_metrics(eval_dir: Path, execution: dict, grading: dict) -> None:
    """Write per-case runtime and success metrics."""
    payload = {
        "execution_success": execution.get("success", False),
        "execution_error": execution.get("error"),
        "execution_duration_seconds": execution.get("duration"),
        "grading_success": grading.get("pass_rate") is not None,
        "grading_error": grading.get("error"),
        "grading_duration_seconds": grading.get("duration"),
        "pass_rate": grading.get("pass_rate"),
        "timestamp": time.time(),
    }
    metrics_path = eval_dir / "metrics.json"
    metrics_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


# ---------------------------------------------------------------------------
# Main harness logic
# ---------------------------------------------------------------------------

def run_harness(
    skill_path: Path,
    iteration: int,
    runs_dir: Optional[Path] = None,
    skip_permissions: bool = False,
) -> dict:
    """Run the full evaluation harness for a target skill."""
    global RUNS_ROOT
    if runs_dir is not None:
        RUNS_ROOT = runs_dir
    else:
        set_runs_root_from_skill(skill_path)

    evals_file = skill_path / "evals" / "evals.json"
    if not evals_file.exists():
        raise FileNotFoundError(f"evals.json not found at {evals_file}")

    evals_data = load_json(evals_file)
    eval_cases = (evals_data or {}).get("evals", [])
    if not eval_cases:
        raise ValueError(f"No eval cases found in {evals_file}")

    skill_name = skill_path.name
    run_dir = get_run_dir(iteration)
    print(f"[harness] Starting harness for {skill_name} iteration {iteration}")
    print(f"[harness] Run directory: {run_dir}")
    print(f"[harness] {len(eval_cases)} eval cases")

    results: dict[int, dict] = {}
    overall_start = time.time()

    try:
        for case in eval_cases:
            case_id = case["id"]
            eval_dir = get_eval_dir(run_dir, case_id)
            case_label = case.get("name", case.get("prompt", ""))[:80]
            print(f"\n[harness] === Eval Case {case_id}: {case_label} ===")

            print("[harness]   Executing skill...")
            exec_result = spawn_executor(
                skill_path,
                case,
                eval_dir,
                timeout=180,
                skip_permissions=skip_permissions,
            )
            if exec_result["success"]:
                print(f"[harness]   ✅ Execution OK ({exec_result['duration']:.1f}s)")
            else:
                print(f"[harness]   ❌ Execution failed: {exec_result.get('error')}")

            print("[harness]   Grading output...")
            grading_result = spawn_grader(
                skill_path,
                case,
                exec_result.get("output_json"),
                eval_dir,
                timeout=60,
                skip_permissions=skip_permissions,
            )
            if grading_result["pass_rate"] is not None:
                print(
                    f"[harness]   📊 Grading: {grading_result['passed']}/{grading_result['total']} "
                    f"passed ({grading_result['pass_rate']:.1%}) [{grading_result['duration']:.1f}s]"
                )
            else:
                print(f"[harness]   ❌ Grading failed: {grading_result.get('error')}")

            save_case_metrics(eval_dir, exec_result, grading_result)

            results[case_id] = {
                "case": case,
                "execution": exec_result,
                "grading": grading_result,
                "eval_dir": str(eval_dir),
            }
    finally:
        clear_eval_inputs(skill_path)

    duration = time.time() - overall_start
    valid_pass_rates = [
        result["grading"]["pass_rate"]
        for result in results.values()
        if result["grading"].get("pass_rate") is not None
    ]

    summary = {
        "skill_name": skill_name,
        "skill_path": str(skill_path),
        "iteration": iteration,
        "run_dir": str(run_dir),
        "case_count": len(eval_cases),
        "execution_success_count": sum(1 for result in results.values() if result["execution"]["success"]),
        "grading_success_count": sum(1 for result in results.values() if result["grading"].get("pass_rate") is not None),
        "mean_pass_rate": (
            sum(valid_pass_rates) / len(valid_pass_rates)
            if valid_pass_rates else None
        ),
        "total_duration_seconds": duration,
        "results": {
            case_id: {
                "pass_rate": result["grading"].get("pass_rate"),
                "passed": result["grading"].get("passed", 0),
                "total": result["grading"].get("total", 0),
                "execution_success": result["execution"].get("success", False),
                "grading_success": result["grading"].get("pass_rate") is not None,
            }
            for case_id, result in results.items()
        },
    }

    summary_path = run_dir / "harness_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    grading_summary_path = run_dir / "grading_summary.txt"
    grading_summary_path.write_text(build_grading_summary(iteration, results), encoding="utf-8")

    print(f"\n[harness] ✅ Done. Summary: {summary_path}")
    print(f"[harness] ✅ Grading summary: {grading_summary_path}")
    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Run evaluation harness for a target skill")
    parser.add_argument(
        "--skill-path",
        type=Path,
        required=True,
        help="Path to the target skill directory",
    )
    parser.add_argument(
        "--iteration",
        type=int,
        required=True,
        help="Iteration number (for run directory naming)",
    )
    parser.add_argument(
        "--runs-dir",
        type=Path,
        default=None,
        help="Root directory for runs (default: <skill-path>-eval/)",
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

    summary = run_harness(
        args.skill_path,
        args.iteration,
        args.runs_dir,
        skip_permissions=args.dangerously_skip_permissions,
    )

    total_cases = len(summary["results"])
    print("\n=== Harness Summary ===")
    print(f"Skill: {summary['skill_name']}")
    print(f"Iteration: {summary['iteration']}")
    print(f"Cases run: {total_cases}/{total_cases}")
    print(f"Cases with valid grading: {summary['grading_success_count']}/{total_cases}")
    print(f"Mean pass_rate: {format_pass_rate(summary.get('mean_pass_rate'))}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
