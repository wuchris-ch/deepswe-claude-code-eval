"""Hidden verification tests — never shown to the agent."""
import json
import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "cli.py", *args], capture_output=True, text=True
    )


def test_json_flag_outputs_valid_json():
    proc = run_cli("--json", "3", "1", "4", "1", "5")
    assert proc.returncode == 0
    payload = json.loads(proc.stdout.strip())
    assert payload == {"count": 5, "mean": 2.8, "min": 1, "max": 5}


def test_json_is_single_line():
    proc = run_cli("--json", "2", "4")
    assert proc.stdout.strip().count("\n") == 0


def test_plain_output_unchanged():
    proc = run_cli("3", "1", "4", "1", "5")
    assert proc.stdout == "count: 5\nmean: 2.8\nmin: 1\nmax: 5\n"
