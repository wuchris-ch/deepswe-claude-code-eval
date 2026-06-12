"""Aggregate run results into a per-variant comparison table (markdown)."""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def load_results(results_dir: Path) -> list[dict[str, Any]]:
    combined = results_dir / "all_results.json"
    if combined.exists():
        return json.loads(combined.read_text())
    return [
        json.loads(p.read_text())
        for p in sorted(results_dir.glob("*/result.json"))
    ]


def aggregate(results: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    by_variant: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        by_variant[r["variant_id"]].append(r)

    agg = {}
    for vid, runs in sorted(by_variant.items()):
        n = len(runs)
        cat_fail: dict[str, int] = defaultdict(int)
        for r in runs:
            for c in r["checks"]:
                if not c["passed"]:
                    cat_fail[c["category"]] += 1
        agg[vid] = {
            "runs": n,
            "resolved": sum(r["resolved"] for r in runs),
            "resolve_rate": round(sum(r["resolved"] for r in runs) / n, 3),
            "mean_score": round(sum(r["score"] for r in runs) / n, 3),
            "mean_turns": round(
                sum(r["trajectory"]["num_assistant_turns"] for r in runs) / n, 1),
            "mean_duration_s": round(sum(r["duration_s"] for r in runs) / n, 1),
            "total_cost_usd": round(sum(
                r["trajectory"].get("cost_usd") or 0 for r in runs), 4),
            "check_failures_by_category": dict(cat_fail),
        }
    return agg


def markdown_report(results: list[dict[str, Any]]) -> str:
    agg = aggregate(results)
    lines = [
        "| Variant | Runs | Resolved | Resolve rate | Mean score | Mean turns | Mean dur (s) | Cost ($) | Failures by category |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for vid, a in agg.items():
        fails = ", ".join(f"{k}:{v}" for k, v in a["check_failures_by_category"].items()) or "none"
        lines.append(
            f"| {vid} | {a['runs']} | {a['resolved']} | {a['resolve_rate']:.0%} "
            f"| {a['mean_score']:.2f} | {a['mean_turns']} | {a['mean_duration_s']} "
            f"| {a['total_cost_usd']} | {fails} |"
        )

    lines.append("\n### Per-task resolution matrix\n")
    tasks = sorted({r["task_id"] for r in results})
    variants = sorted({r["variant_id"] for r in results})
    lines.append("| Task | " + " | ".join(variants) + " |")
    lines.append("|---|" + "---|" * len(variants))
    index = {(r["task_id"], r["variant_id"]): r for r in results}
    for t in tasks:
        cells = []
        for v in variants:
            r = index.get((t, v))
            cells.append("—" if r is None else ("PASS" if r["resolved"] else f"{r['score']:.2f}"))
        lines.append(f"| {t} | " + " | ".join(cells) + " |")
    return "\n".join(lines)
