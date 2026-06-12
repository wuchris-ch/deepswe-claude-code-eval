"""CLI entry point.

Examples:
    python -m harness run --out results/$(date +%Y%m%d-%H%M%S)
    python -m harness run --dry-run --out /tmp/dryrun
    python -m harness run --tasks-filter fix-pagination --variants-filter baseline
    python -m harness report results/20260611-180000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .report import load_results, markdown_report
from .runner import run_matrix

ROOT = Path(__file__).resolve().parent.parent


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harness")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="run the task x variant eval matrix")
    p_run.add_argument("--tasks", type=Path, default=ROOT / "tasks")
    p_run.add_argument("--variants", type=Path, default=ROOT / "variants" / "variants.json")
    p_run.add_argument("--out", type=Path, required=True)
    p_run.add_argument("--model", default="haiku")
    p_run.add_argument("--effort", default=None,
                       help="claude CLI effort level (e.g. low/medium/high); omit for CLI default")
    p_run.add_argument("--dry-run", action="store_true",
                       help="skip the agent; score pristine sandboxes (harness self-test)")
    p_run.add_argument("--tasks-filter", nargs="*", default=None)
    p_run.add_argument("--variants-filter", nargs="*", default=None)

    p_rep = sub.add_parser("report", help="print markdown report for a results dir")
    p_rep.add_argument("results_dir", type=Path)

    args = parser.parse_args(argv)

    if args.cmd == "run":
        results = run_matrix(
            args.tasks, args.variants, args.out, model=args.model,
            effort=args.effort,
            dry_run=args.dry_run, only_tasks=args.tasks_filter,
            only_variants=args.variants_filter,
        )
        print()
        print(markdown_report(results))
        report_path = args.out / "report.md"
        report_path.write_text(markdown_report(results) + "\n")
        print(f"\nreport written to {report_path}")
    elif args.cmd == "report":
        print(markdown_report(load_results(args.results_dir)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
