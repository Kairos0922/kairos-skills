#!/usr/bin/env python3
"""
scripts/harness.py — Evaluation Harness

Responsibilities:
1. For each eval case in evals/evals.json:
   a. Spawn executor subagent → run skill → save output + transcript
   b. Spawn grader subagent → grade output → grading.json
2. Output per-eval-case grading.json files

Usage:
    python3 scripts/harness.py --skill-path /path/to/target-skill --iteration 1

Output:
    <skill-path>-eval/iteration-<N>/eval-<case-id>/
        ├── output.json          # raw skill output
        ├── grading.json         # pass/fail per assertion + evidence
        └── metrics.json         # timing, token counts
"""

import argparse
import json
import os
import re
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

WORKSPACE_ROOT = Path(__file__).parent.parent.resolve()
# Default runs root - can be overridden via set_runs_root_from_skill()
RUNS_ROOT = WORKSPACE_ROOT / "runs"


def set_runs_root_from_skill(skill_path: Path) -> None:
    """Set RUNS_ROOT to be alongside the skill being tested (sibling directory)."""
    global RUNS_ROOT
    # skill: /path/to/kairos-collect-signals
    # runs:  /path/to/kairos-collect-signals-eval/
    RUNS_ROOT = Path(str(skill_path) + "-eval").resolve()


def get_run_dir(iteration: int) -> Path:
    # Path: <skill-path>-eval/iteration-{N}/
    # Example: kairos-collect-signals-eval/iteration-1/
    run_dir = RUNS_ROOT / f"iteration-{iteration}"
    run_dir.mkdir(parents=True, exist_ok=True)
    return run_dir


def get_eval_dir(run_dir: Path, case_id: int) -> Path:
    eval_dir = run_dir / f"eval-{case_id}"
    eval_dir.mkdir(parents=True, exist_ok=True)
    return eval_dir


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
    """
    Spawn executor subagent to run the target skill with eval case input.

    Returns dict with keys: success, output_json, transcript_path, duration
    """
    start_time = time.time()

    # If the eval case provides signals, pre-write them to .kairos-temp/signals.json
    # so the skill skips collect.py and uses these signals directly (for cases 2-10)
    signals = eval_case.get("signals")
    if signals:
        signals_file = skill_path / ".kairos-temp" / "signals.json"
        signals_file.parent.mkdir(parents=True, exist_ok=True)
        signals_file.write_text(
            json.dumps({"signals": signals}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    # Build the executor prompt
    prompt = build_executor_prompt(eval_case)

    # Execute via claude -p
    output_text, returncode = run_claude_p(
        prompt=prompt,
        skill_path=skill_path,
        timeout=timeout,
        skip_permissions=skip_permissions,
    )

    duration = time.time() - start_time

    if returncode != 0 or not output_text.strip():
        return {
            "success": False,
            "output_json": None,
            "transcript_path": None,
            "duration": duration,
            "error": f"non-zero exit {returncode}" if returncode != 0 else "empty output",
        }

    # Save raw output
    output_path = eval_dir / "output.json"
    output_path.write_text(output_text, encoding="utf-8")

    # Try to parse as JSON
    parsed = extract_json(output_text)
    if parsed:
        # Save structured output too
        structured_path = eval_dir / "output.structured.json"
        structured_path.write_text(json.dumps(parsed, indent=2, ensure_ascii=False), encoding="utf-8")
        return {
            "success": True,
            "output_json": parsed,
            "output_path": str(output_path),
            "duration": duration,
        }
    else:
        # Output wasn't valid JSON - still save it
        return {
            "success": False,
            "output_json": None,
            "output_path": str(output_path),
            "duration": duration,
            "error": "output was not valid JSON",
        }


def build_executor_prompt(eval_case: dict) -> str:
    """Build the prompt for the executor subagent."""
    case_id = eval_case.get("id", "?")
    user_request = eval_case.get("prompt", "")
    has_signals = "signals" in eval_case and eval_case["signals"]

    signals_note = (
        'Note: signals have been pre-written to `.kairos-temp/signals.json` for this eval case. '
        "When executing the skill, follow SKILL.md's instructions: if `.kairos-temp/signals.json` "
        "already exists, skip the collect step and use the pre-provided signals directly."
    ) if has_signals else ""

    return f"""You are executing a skill for evaluation (case {case_id}).

## Your task
1. Read SKILL.md in your current directory to understand the skill
2. Execute the skill with this user request:
   "{user_request}"
{f"## {signals_note}" if signals_note else ""}

## Important constraints
- Execute the skill exactly as described in SKILL.md
- Do NOT ask for confirmation or clarification
- Do NOT explain what you are doing

## Output
After executing the skill, output the complete result as ONLY this JSON format (no markdown fences, no explanation):

{{
  "skill_output": {{...the full structured output from the skill...}},
  "execution_notes": "brief notes on execution"
}}

If the skill fails to produce output, return:
{{
  "skill_output": null,
  "execution_notes": "what went wrong"
}}"""


def spawn_grader(
    skill_path: Path,
    eval_case: dict,
    output_json: Optional[dict],
    eval_dir: Path,
    timeout: int = 60,
    skip_permissions: bool = False,
) -> dict:
    """
    Spawn grader subagent to grade the skill output against assertions.

    Returns dict with keys: passed, failed, total, pass_rate, expectations, duration
    """
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
            "duration": duration,
            "error": f"non-zero exit {returncode}" if returncode != 0 else "empty output",
        }

    # Parse grading JSON
    grading = extract_json(output_text)

    if grading:
        # Save grading result
        grading_path = eval_dir / "grading.json"
        grading_path.write_text(json.dumps(grading, indent=2, ensure_ascii=False), encoding="utf-8")

        summary = grading.get("summary", {})
        raw_pass_rate = summary.get("pass_rate")
        return {
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
            "total": summary.get("total", 0),
            "pass_rate": normalize_pass_rate(raw_pass_rate),
            "raw_pass_rate": raw_pass_rate,  # preserve for debugging
            "expectations": grading.get("expectations", []),
            "eval_feedback": grading.get("eval_feedback", {}),
            "duration": duration,
        }
    else:
        # Grader didn't return valid JSON - save raw output for debugging
        raw_path = eval_dir / "grading.raw.txt"
        raw_path.write_text(output_text, encoding="utf-8")
        return {
            "passed": 0,
            "failed": 0,
            "total": 0,
            "pass_rate": None,
            "expectations": [],
            "duration": duration,
            "error": "grader did not return valid JSON",
        }


def build_grader_prompt(eval_case: dict, output_json: Optional[dict]) -> str:
    """Build the prompt for the grader subagent."""
    case_id = eval_case.get("id", "?")
    assertions = eval_case.get("assertions", [])

    # Serialize output for prompt
    if output_json:
        output_str = json.dumps(output_json, ensure_ascii=False, indent=2)
    else:
        output_str = '{"error": "no output to grade"}'

    assertions_text = "\n".join(f"- {a}" for a in assertions)

    return f"""You are evaluating a skill's output against assertions.

## Eval Case ID: {case_id}

## Assertions to check:
{assertions_text}

## Skill output (JSON):
{output_str}

## Instructions
1. Check each assertion against the JSON output
2. Output ONLY this JSON (no markdown fences, no explanation):
{{
  "expectations": [
    {{"text": "full assertion text", "passed": true_or_false, "evidence": "what you found"}}
  ],
  "summary": {{"passed": N, "failed": M, "total": K, "pass_rate": 0.0_to_1.0}},
  "eval_feedback": {{"suggestions": []}}
}}

## Important
- pass_rate must be a DECIMAL between 0.0 and 1.0 (e.g., 0.143 for 14.3%)
- passed + failed must equal total
- total is the number of assertions checked"""


def run_claude_p(
    prompt: str,
    skill_path: Path,
    timeout: int = 60,
    skip_permissions: bool = False,
) -> tuple[str, int]:
    """
    Run claude -p with the given prompt, cwd set to skill_path.

    Args:
        prompt: The prompt to send to claude.
        skill_path: Working directory for the claude process.
        timeout: Timeout in seconds.
        skip_permissions: If True, add --dangerously-skip-permissions flag
                          to allow bash command execution.

    Returns (stdout, returncode).
    """
    cmd = ["claude", "-p", prompt, "--output-format", "text"]
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

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
    except Exception as e:
        return f"{{\"error\": \"{str(e)}\"}}", 1


# ---------------------------------------------------------------------------
# JSON extraction utilities
# ---------------------------------------------------------------------------

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
    # If > 1, assume it's a percentage (e.g., 14.3 means 14.3%, not 1430.0%)
    # A valid pass_rate of 1.0 means 100% (all assertions passed)
    if pr > 1:
        return pr / 100.0
    # Already in 0-1 range (including 1.0 = 100%)
    return pr


def extract_json(text: str) -> Optional[dict]:
    """
    Extract JSON object from text using multiple strategies.
    Handles multi-line JSON, truncated output, and embedded JSON strings.
    """
    if not text or not text.strip():
        return None

    # Strategy 1: Try to find a {...} block that contains "summary" key
    # Use non-greedy matching to find the first complete JSON object
    for match in re.finditer(r'\{[\s\S]*?\}', text):
        candidate = match.group()
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, dict) and "summary" in parsed:
                return parsed
        except json.JSONDecodeError:
            continue

    # Strategy 2: Try the first { to last } as a single block (greedy)
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        json_str = json_match.group()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass

    # Strategy 3: Try the whole text as JSON
    try:
        return json.loads(text.strip())
    except json.JSONDecodeError:
        pass

    # Strategy 4: Strip markdown fences and try again
    cleaned = re.sub(r'^```json\s*', '', text.strip())
    cleaned = re.sub(r'^```\s*', '', cleaned)
    cleaned = re.sub(r'\s*```$', '', cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    return None


# ---------------------------------------------------------------------------
# Main harness logic
# ---------------------------------------------------------------------------

def run_harness(skill_path: Path, iteration: int, runs_dir: Optional[Path] = None, skip_permissions: bool = False) -> dict:
    """
    Run the full evaluation harness for a target skill.

    Returns a summary dict with per-eval-case results.
    """
    global RUNS_ROOT
    if runs_dir:
        RUNS_ROOT = runs_dir
    else:
        # By default, put runs alongside the skill being tested (sibling directory)
        set_runs_root_from_skill(skill_path)

    skill_name = skill_path.name
    evals_file = skill_path / "evals" / "evals.json"

    if not evals_file.exists():
        raise FileNotFoundError(f"evals.json not found at {evals_file}")

    evals_data = json.loads(evals_file.read_text(encoding="utf-8"))
    eval_cases = evals_data.get("evals", [])

    if not eval_cases:
        raise ValueError(f"No eval cases found in {evals_file}")

    run_dir = get_run_dir(iteration)
    print(f"[harness] Starting harness for {skill_name} iteration {iteration}")
    print(f"[harness] Run directory: {run_dir}")
    print(f"[harness] {len(eval_cases)} eval cases")

    results = {}
    overall_start = time.time()

    for case in eval_cases:
        case_id = case["id"]
        eval_dir = get_eval_dir(run_dir, case_id)
        print(f"\n[harness] === Eval Case {case_id}: {case.get('name', case.get('prompt', '')[:50])} ===")

        # Step 1: Spawn executor
        print(f"[harness]   Executing skill...")
        exec_result = spawn_executor(skill_path, case, eval_dir, timeout=180, skip_permissions=skip_permissions)

        if exec_result["success"]:
            output_json = exec_result["output_json"]
            print(f"[harness]   ✅ Execution OK ({exec_result['duration']:.1f}s)")
        else:
            output_json = None
            print(f"[harness]   ❌ Execution failed: {exec_result.get('error')}")

        # Step 2: Spawn grader
        print(f"[harness]   Grading output...")
        grading_result = spawn_grader(skill_path, case, output_json, eval_dir, timeout=60, skip_permissions=skip_permissions)

        if grading_result["pass_rate"] is not None:
            print(
                f"[harness]   📊 Grading: {grading_result['passed']}/{grading_result['total']} "
                f"passed ({grading_result['pass_rate']:.1%}) [{grading_result['duration']:.1f}s]"
            )
        else:
            print(f"[harness]   ❌ Grading failed: {grading_result.get('error')}")

        results[case_id] = {
            "case": case,
            "execution": exec_result,
            "grading": grading_result,
            "eval_dir": str(eval_dir),
        }

    overall_duration = time.time() - overall_start

    # Save harness summary
    summary = {
        "skill_name": skill_name,
        "skill_path": str(skill_path),
        "iteration": iteration,
        "run_dir": str(run_dir),
        "total_duration_seconds": overall_duration,
        "case_count": len(eval_cases),
        "results": {
            case_id: {
                "pass_rate": r["grading"].get("pass_rate"),
                "passed": r["grading"].get("passed", 0),
                "total": r["grading"].get("total", 0),
                "execution_success": r["execution"]["success"],
                "grading_success": r["grading"].get("pass_rate") is not None,
            }
            for case_id, r in results.items()
        },
    }

    summary_path = run_dir / "harness_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n[harness] ✅ Done. Summary: {summary_path}")

    return summary


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
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
        help="Root directory for runs (default: <skill-path>-eval/, i.e., alongside the skill being tested)",
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

    summary = run_harness(args.skill_path, args.iteration, args.runs_dir, skip_permissions=args.dangerously_skip_permissions)

    # Print quick summary
    total_pass = sum(1 for r in summary["results"].values() if r["grading_success"])
    total_cases = len(summary["results"])
    print(f"\n=== Harness Summary ===")
    print(f"Skill: {summary['skill_name']}")
    print(f"Iteration: {summary['iteration']}")
    print(f"Cases run: {total_cases}/{total_cases}")
    print(f"Cases with valid grading: {total_pass}/{total_cases}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
