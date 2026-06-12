"""Hidden-verification scoring for a completed sandbox workspace.

Checks live in the task's `task.json` and run AFTER the agent finishes,
against the sandbox copy. Verification tests are kept in the task dir's
`verify/` folder (never copied into the sandbox), mirroring how R2E-Gym /
SWE-Bench keep golden tests hidden from the agent so they can't be gamed.

Check types
-----------
command         run a shell command in the sandbox; pass iff exit 0.
                `{verify}` in the command expands to the task's verify/ dir.
file_unchanged  sandbox file must be byte-identical to the original fixture.
file_contains   sandbox file must contain `needle`.
file_not_contains  sandbox file must NOT contain `needle`.
no_new_files    no files in sandbox beyond the original fixture set,
                except paths listed in `allow` (glob patterns).
"""

from __future__ import annotations

import fnmatch
import subprocess
from pathlib import Path
from typing import Any

CHECK_TIMEOUT_S = 120


def _iter_files(root: Path) -> set[str]:
    return {
        str(p.relative_to(root))
        for p in root.rglob("*")
        if p.is_file() and "__pycache__" not in p.parts
        and not any(part.startswith(".") for part in p.parts)
    }


def run_check(check: dict[str, Any], sandbox: Path, task_dir: Path) -> dict[str, Any]:
    """Execute one check; returns a result row for the schema's checks[]."""
    ctype = check["type"]
    original = task_dir / "workspace"
    verify = task_dir / "verify"
    passed, detail = False, ""

    try:
        if ctype == "command":
            cmd = check["command"].replace("{verify}", str(verify))
            proc = subprocess.run(
                cmd, shell=True, cwd=sandbox, capture_output=True,
                text=True, timeout=CHECK_TIMEOUT_S,
            )
            passed = proc.returncode == 0
            tail = (proc.stdout + proc.stderr).strip().splitlines()[-3:]
            detail = f"exit={proc.returncode} " + " | ".join(tail)
        elif ctype == "file_unchanged":
            a, b = sandbox / check["path"], original / check["path"]
            passed = a.exists() and b.exists() and a.read_bytes() == b.read_bytes()
            detail = "identical" if passed else "modified or missing"
        elif ctype == "file_contains":
            p = sandbox / check["path"]
            passed = p.exists() and check["needle"] in p.read_text()
            detail = "found" if passed else "needle absent or file missing"
        elif ctype == "file_not_contains":
            p = sandbox / check["path"]
            passed = p.exists() and check["needle"] not in p.read_text()
            detail = "clean" if passed else "needle still present or file missing"
        elif ctype == "no_new_files":
            allow = check.get("allow", [])
            extras = sorted(
                f for f in _iter_files(sandbox) - _iter_files(original)
                if not any(fnmatch.fnmatch(f, pat) for pat in allow)
            )
            passed = not extras
            detail = "no unexpected files" if passed else f"unexpected: {extras[:5]}"
        else:
            detail = f"unknown check type: {ctype}"
    except subprocess.TimeoutExpired:
        detail = f"check timed out after {CHECK_TIMEOUT_S}s"
    except OSError as exc:
        detail = f"check error: {exc}"

    return {
        "id": check["id"],
        "category": check.get("category", "correctness"),
        "passed": passed,
        "detail": detail[:500],
    }


def score_sandbox(task: dict[str, Any], sandbox: Path, task_dir: Path) -> dict[str, Any]:
    """Run all of a task's checks; return checks list, score, resolved flag."""
    checks = [run_check(c, sandbox, task_dir) for c in task["checks"]]
    n_pass = sum(c["passed"] for c in checks)
    return {
        "checks": checks,
        "score": round(n_pass / len(checks), 4) if checks else 0.0,
        "resolved": bool(checks) and n_pass == len(checks),
    }
