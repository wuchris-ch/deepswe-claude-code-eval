"""End-to-end dry-run: full matrix without invoking the agent.

Pristine (still-buggy) workspaces must score < 1 on every task, results must
be schema-valid, and the report must render. Needs no network or API budget.
"""
import json
from pathlib import Path

from harness.report import markdown_report
from harness.runner import load_variants, run_matrix
from harness.schema import validate_result

ROOT = Path(__file__).resolve().parent.parent


def test_variants_config_loads():
    variants = load_variants(ROOT / "variants" / "variants.json")
    ids = [v["id"] for v in variants]
    assert "baseline" in ids and "deprecated-global-full" in ids
    assert next(v for v in variants if v["id"] == "baseline")["_prompt"] is None
    full = next(v for v in variants if v["id"] == "deprecated-global-full")
    assert "Surgical Changes" in full["_prompt"]


def test_dry_run_matrix(tmp_path):
    results = run_matrix(
        ROOT / "tasks",
        ROOT / "variants" / "variants.json",
        tmp_path,
        dry_run=True,
        only_variants=["baseline"],
    )
    n_tasks = sum(1 for d in (ROOT / "tasks").iterdir() if (d / "task.json").exists())
    assert len(results) == n_tasks == 9  # one per task fixture
    for res in results:
        assert validate_result(res) == []
        assert not res["resolved"], f"{res['task_id']} resolved without an agent!"
        run_dir = tmp_path / res["run_id"]
        assert (run_dir / "result.json").exists()
        assert (run_dir / "workspace_after").is_dir()
    saved = json.loads((tmp_path / "all_results.json").read_text())
    assert len(saved) == len(results)
    report = markdown_report(results)
    assert "baseline" in report and "Per-task resolution matrix" in report
