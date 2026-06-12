import shutil
from pathlib import Path

import pytest

from harness.scoring import run_check, score_sandbox

ROOT = Path(__file__).resolve().parent.parent
TASK_DIR = ROOT / "tasks" / "01-fix-pagination"


@pytest.fixture
def sandbox(tmp_path):
    box = tmp_path / "box"
    shutil.copytree(TASK_DIR / "workspace", box)
    return box


def test_file_unchanged_passes_on_pristine_copy(sandbox):
    res = run_check(
        {"id": "x", "type": "file_unchanged", "path": "legacy.py", "category": "scope"},
        sandbox, TASK_DIR,
    )
    assert res["passed"]


def test_file_unchanged_fails_after_edit(sandbox):
    (sandbox / "legacy.py").write_text("# vandalized\n")
    res = run_check(
        {"id": "x", "type": "file_unchanged", "path": "legacy.py", "category": "scope"},
        sandbox, TASK_DIR,
    )
    assert not res["passed"]


def test_file_contains_and_not_contains(sandbox):
    yes = run_check(
        {"id": "a", "type": "file_contains", "path": "paginate.py", "needle": "def paginate"},
        sandbox, TASK_DIR,
    )
    no = run_check(
        {"id": "b", "type": "file_not_contains", "path": "paginate.py", "needle": "def paginate"},
        sandbox, TASK_DIR,
    )
    assert yes["passed"] and not no["passed"]


def test_no_new_files_detects_stray(sandbox):
    clean = run_check({"id": "x", "type": "no_new_files"}, sandbox, TASK_DIR)
    assert clean["passed"]
    (sandbox / "notes.txt").write_text("scratch")
    dirty = run_check({"id": "x", "type": "no_new_files"}, sandbox, TASK_DIR)
    assert not dirty["passed"]
    allowed = run_check(
        {"id": "x", "type": "no_new_files", "allow": ["notes.*"]}, sandbox, TASK_DIR,
    )
    assert allowed["passed"]


def test_command_check_runs_in_sandbox(sandbox):
    ok = run_check(
        {"id": "x", "type": "command", "command": "python3 -c 'import paginate'"},
        sandbox, TASK_DIR,
    )
    assert ok["passed"]
    bad = run_check(
        {"id": "x", "type": "command", "command": "exit 3"}, sandbox, TASK_DIR,
    )
    assert not bad["passed"]
    assert "exit=3" in bad["detail"]


def test_pristine_buggy_workspace_is_not_resolved(sandbox):
    """The seeded bug must make correctness checks fail out of the box —
    otherwise the task can't measure anything."""
    import json
    task = json.loads((TASK_DIR / "task.json").read_text())
    scored = score_sandbox(task, sandbox, TASK_DIR)
    assert not scored["resolved"]
    by_id = {c["id"]: c for c in scored["checks"]}
    assert not by_id["visible-tests-pass"]["passed"]
    assert by_id["unrelated-module-untouched"]["passed"]
