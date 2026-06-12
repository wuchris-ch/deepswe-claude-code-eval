"""Run task × instruction-variant evaluations through Claude Code headless mode.

For each (task, variant) pair:
1. copy the task's `workspace/` into a fresh temp sandbox (the agent never
   sees the task dir, its checks, or the hidden `verify/` tests)
2. run `claude -p <task prompt>` in the sandbox, with the variant's
   instructions injected via --append-system-prompt
3. capture the stream-json trajectory to results/<run>/transcript.jsonl
4. run hidden verification checks against the sandbox (scoring.py)
5. emit one schema-valid result JSON per run

`--dry-run` skips the agent entirely (sandbox is scored as-is); used by the
harness's own tests so they need no network or API budget.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .schema import validate_result
from .scoring import score_sandbox
from .trajectory import parse_transcript

AGENT_TIMEOUT_S = 600


def load_task(task_dir: Path) -> dict[str, Any]:
    task = json.loads((task_dir / "task.json").read_text())
    task["_dir"] = task_dir
    return task


def load_variants(variants_path: Path) -> list[dict[str, Any]]:
    """variants.json: [{"id": ..., "file": "name.md" | null}, ...]"""
    variants = json.loads(variants_path.read_text())
    for v in variants:
        if v.get("file"):
            v["_prompt"] = (variants_path.parent / v["file"]).read_text()
        else:
            v["_prompt"] = None
    return variants


def build_agent_cmd(
    task: dict, variant: dict, transcript: Path, model: str,
    effort: str | None = None,
) -> list[str]:
    cmd = [
        "claude", "-p", task["prompt"],
        "--output-format", "stream-json",
        "--verbose",
        "--model", model,
        "--max-turns", str(task.get("max_turns", 30)),
        "--dangerously-skip-permissions",
    ]
    if effort:
        cmd += ["--effort", effort]
    if variant["_prompt"]:
        cmd += ["--append-system-prompt", variant["_prompt"]]
    return cmd


def run_one(
    task: dict[str, Any],
    variant: dict[str, Any],
    out_dir: Path,
    model: str = "haiku",
    effort: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    run_id = f"{task['id']}__{variant['id']}__{uuid.uuid4().hex[:8]}"
    run_dir = out_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    transcript = run_dir / "transcript.jsonl"
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.monotonic()
    exit_code = 0

    sandbox = Path(tempfile.mkdtemp(prefix=f"eval-{task['id']}-"))
    try:
        shutil.copytree(task["_dir"] / "workspace", sandbox, dirs_exist_ok=True)

        if not dry_run:
            cmd = build_agent_cmd(task, variant, transcript, model, effort=effort)
            with transcript.open("w") as fh:
                proc = subprocess.run(
                    cmd, cwd=sandbox, stdout=fh, stderr=subprocess.PIPE,
                    text=True, timeout=task.get("timeout_s", AGENT_TIMEOUT_S),
                )
            exit_code = proc.returncode
            if proc.stderr:
                (run_dir / "stderr.txt").write_text(proc.stderr)

        scored = score_sandbox(task, sandbox, task["_dir"])
        # keep the agent's final workspace for trajectory review
        shutil.copytree(sandbox, run_dir / "workspace_after", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__", ".git"))
    finally:
        shutil.rmtree(sandbox, ignore_errors=True)

    result = {
        "run_id": run_id,
        "task_id": task["id"],
        "variant_id": variant["id"],
        "model": model if not dry_run else "dry-run",
        "effort": effort,
        "started_at": started,
        "duration_s": round(time.monotonic() - t0, 2),
        "agent_exit_code": exit_code,
        **scored,
        "trajectory": parse_transcript(transcript),
    }
    if result["trajectory"].get("api_error_status"):
        print(f"       WARNING: agent hit API error "
              f"{result['trajectory']['api_error_status']} — run is invalid, "
              f"quarantine before aggregating", flush=True)
    errors = validate_result(result)
    if errors:
        raise ValueError(f"result failed schema validation: {errors}")
    (run_dir / "result.json").write_text(json.dumps(result, indent=2))
    return result


def run_matrix(
    tasks_dir: Path,
    variants_path: Path,
    out_dir: Path,
    model: str = "haiku",
    effort: str | None = None,
    dry_run: bool = False,
    only_tasks: list[str] | None = None,
    only_variants: list[str] | None = None,
) -> list[dict[str, Any]]:
    tasks = [
        load_task(d) for d in sorted(tasks_dir.iterdir())
        if (d / "task.json").exists()
    ]
    variants = load_variants(variants_path)
    if only_tasks:
        tasks = [t for t in tasks if t["id"] in only_tasks]
    if only_variants:
        variants = [v for v in variants if v["id"] in only_variants]

    results = []
    for task in tasks:
        for variant in variants:
            print(f"[run] task={task['id']} variant={variant['id']} ...", flush=True)
            res = run_one(task, variant, out_dir, model=model, effort=effort,
                          dry_run=dry_run)
            print(
                f"       score={res['score']:.2f} resolved={res['resolved']} "
                f"turns={res['trajectory']['num_assistant_turns']} "
                f"dur={res['duration_s']}s",
                flush=True,
            )
            results.append(res)

    (out_dir / "all_results.json").write_text(json.dumps(results, indent=2))
    return results
