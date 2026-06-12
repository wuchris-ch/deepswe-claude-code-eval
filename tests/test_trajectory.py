import json

from harness.trajectory import parse_transcript


def write_transcript(path, events):
    path.write_text("\n".join(json.dumps(e) for e in events))


def test_parse_counts_turns_tools_files(tmp_path):
    t = tmp_path / "transcript.jsonl"
    write_transcript(t, [
        {"type": "system", "subtype": "init"},
        {"type": "assistant", "message": {"content": [
            {"type": "text", "text": "looking"},
            {"type": "tool_use", "name": "Read", "input": {"file_path": "/x/a.py"}},
        ]}},
        {"type": "user", "message": {"content": []}},
        {"type": "assistant", "message": {"content": [
            {"type": "tool_use", "name": "Edit",
             "input": {"file_path": "/x/a.py", "old_string": "a", "new_string": "b"}},
            {"type": "tool_use", "name": "Bash", "input": {"command": "pytest"}},
        ]}},
        {"type": "result", "subtype": "success", "total_cost_usd": 0.0123},
    ])
    stats = parse_transcript(t)
    assert stats["num_assistant_turns"] == 2
    assert stats["num_tool_calls"] == 3
    assert stats["tool_call_counts"] == {"Read": 1, "Edit": 1, "Bash": 1}
    assert stats["files_edited"] == ["/x/a.py"]
    assert stats["cost_usd"] == 0.0123
    assert stats["result_subtype"] == "success"


def test_missing_transcript_is_empty_stats(tmp_path):
    stats = parse_transcript(tmp_path / "nope.jsonl")
    assert stats["num_assistant_turns"] == 0
    assert stats["num_tool_calls"] == 0


def test_garbage_lines_skipped(tmp_path):
    t = tmp_path / "t.jsonl"
    t.write_text('not json\n{"type": "assistant", "message": {"content": []}}\n')
    assert parse_transcript(t)["num_assistant_turns"] == 1
