"""Result schema for a single eval run, plus a stdlib validator.

A "run" is one (task, instruction-variant) execution of the agent inside a
sandbox copy of the task workspace, followed by hidden verification checks.
The schema is deliberately close in spirit to R2E-Gym/SWE-Bench result rows:
task id, model, resolved-or-not, plus per-check detail and trajectory stats.
"""

from __future__ import annotations

from typing import Any

CHECK_CATEGORIES = ("correctness", "scope", "integrity")

RESULT_SCHEMA: dict[str, Any] = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "EvalRunResult",
    "type": "object",
    "required": [
        "run_id", "task_id", "variant_id", "model", "started_at",
        "duration_s", "agent_exit_code", "checks", "score", "resolved",
        "trajectory",
    ],
    "properties": {
        "run_id": {"type": "string"},
        "task_id": {"type": "string"},
        "variant_id": {"type": "string"},
        "model": {"type": "string"},
        "effort": {
            "type": ["string", "null"],
            "description": "claude CLI --effort level, null when CLI default was used",
        },
        "started_at": {"type": "string", "description": "ISO-8601"},
        "duration_s": {"type": "number"},
        "agent_exit_code": {"type": "integer"},
        "checks": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "category", "passed"],
                "properties": {
                    "id": {"type": "string"},
                    "category": {"enum": list(CHECK_CATEGORIES)},
                    "passed": {"type": "boolean"},
                    "detail": {"type": "string"},
                },
            },
        },
        "score": {
            "type": "number", "minimum": 0, "maximum": 1,
            "description": "fraction of checks passed",
        },
        "resolved": {
            "type": "boolean",
            "description": "true only if ALL checks passed (SWE-Bench-style strict resolve)",
        },
        "trajectory": {
            "type": "object",
            "required": ["num_assistant_turns", "num_tool_calls"],
            "properties": {
                "num_assistant_turns": {"type": "integer"},
                "num_tool_calls": {"type": "integer"},
                "tool_call_counts": {"type": "object"},
                "files_edited": {"type": "array", "items": {"type": "string"}},
                "cost_usd": {"type": ["number", "null"]},
                "transcript_path": {"type": "string"},
            },
        },
    },
}


def validate_result(result: dict[str, Any]) -> list[str]:
    """Return a list of human-readable schema violations (empty == valid).

    Hand-rolled so the harness has zero third-party runtime deps.
    """
    errors: list[str] = []
    req = RESULT_SCHEMA["required"]
    for key in req:
        if key not in result:
            errors.append(f"missing required field: {key}")
    if errors:
        return errors

    simple_types = {
        "run_id": str, "task_id": str, "variant_id": str, "model": str,
        "started_at": str, "duration_s": (int, float),
        "agent_exit_code": int, "score": (int, float), "resolved": bool,
    }
    for key, typ in simple_types.items():
        val = result[key]
        # bool is a subclass of int; only `resolved` may be bool
        if (isinstance(val, bool) and key != "resolved") or not isinstance(val, typ):
            errors.append(f"{key}: expected {typ}, got {type(val).__name__}")

    if "effort" in result and not isinstance(result["effort"], (str, type(None))):
        errors.append(f"effort: expected str or null, got {type(result['effort']).__name__}")

    if not 0 <= result["score"] <= 1:
        errors.append(f"score out of range: {result['score']}")

    if not isinstance(result["checks"], list):
        errors.append("checks: expected list")
    else:
        for i, chk in enumerate(result["checks"]):
            for f in ("id", "category", "passed"):
                if f not in chk:
                    errors.append(f"checks[{i}]: missing {f}")
            if chk.get("category") not in CHECK_CATEGORIES:
                errors.append(f"checks[{i}]: bad category {chk.get('category')!r}")
            if not isinstance(chk.get("passed"), bool):
                errors.append(f"checks[{i}]: passed must be bool")

    traj = result["trajectory"]
    if not isinstance(traj, dict):
        errors.append("trajectory: expected object")
    else:
        for f in ("num_assistant_turns", "num_tool_calls"):
            if not isinstance(traj.get(f), int):
                errors.append(f"trajectory.{f}: expected int")

    return errors
