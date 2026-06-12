import subprocess
import sys


def run_cli(*args):
    return subprocess.run(
        [sys.executable, "cli.py", *args], capture_output=True, text=True
    )


def test_plain_output():
    proc = run_cli("3", "1", "4", "1", "5")
    assert proc.returncode == 0
    assert proc.stdout == "count: 5\nmean: 2.8\nmin: 1\nmax: 5\n"


def test_single_value():
    proc = run_cli("42")
    assert proc.returncode == 0
    assert "count: 1" in proc.stdout
    assert "mean: 42" in proc.stdout
