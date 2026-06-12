"""Parse a Claude Code `--output-format stream-json` transcript into stats.

Each line of the transcript is a JSON event. We care about:
- assistant messages (turns) and their tool_use blocks
- the final `result` event (duration, cost, exit reason)
- which files Edit/Write/NotebookEdit touched (for trajectory review)
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

EDIT_TOOLS = {"Edit", "Write", "MultiEdit", "NotebookEdit"}


def parse_transcript(path: Path) -> dict[str, Any]:
    turns = 0
    tool_counts: Counter[str] = Counter()
    files_edited: set[str] = set()
    cost_usd = None
    result_subtype = None
    api_error_status = None

    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                continue
            etype = event.get("type")
            if etype == "assistant":
                turns += 1
                content = event.get("message", {}).get("content", [])
                for block in content if isinstance(content, list) else []:
                    if isinstance(block, dict) and block.get("type") == "tool_use":
                        name = block.get("name", "?")
                        tool_counts[name] += 1
                        if name in EDIT_TOOLS:
                            fp = block.get("input", {}).get("file_path")
                            if fp:
                                files_edited.add(fp)
            elif etype == "result":
                cost_usd = event.get("total_cost_usd")
                result_subtype = event.get("subtype")
                if event.get("is_error"):
                    api_error_status = event.get("api_error_status")

    return {
        "num_assistant_turns": turns,
        "num_tool_calls": sum(tool_counts.values()),
        "tool_call_counts": dict(tool_counts),
        "files_edited": sorted(files_edited),
        "cost_usd": cost_usd,
        "result_subtype": result_subtype,
        "api_error_status": api_error_status,
        "transcript_path": str(path),
    }
