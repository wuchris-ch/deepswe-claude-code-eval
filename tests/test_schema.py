from harness.schema import validate_result


def make_valid():
    return {
        "run_id": "t__v__abc",
        "task_id": "t",
        "variant_id": "v",
        "model": "haiku",
        "started_at": "2026-06-11T00:00:00+00:00",
        "duration_s": 1.5,
        "agent_exit_code": 0,
        "checks": [
            {"id": "c1", "category": "correctness", "passed": True, "detail": ""},
        ],
        "score": 1.0,
        "resolved": True,
        "trajectory": {"num_assistant_turns": 3, "num_tool_calls": 5},
    }


def test_valid_result_passes():
    assert validate_result(make_valid()) == []


def test_missing_field_reported():
    bad = make_valid()
    del bad["score"]
    assert any("score" in e for e in validate_result(bad))


def test_bad_category_reported():
    bad = make_valid()
    bad["checks"][0]["category"] = "vibes"
    assert any("category" in e for e in validate_result(bad))


def test_score_out_of_range():
    bad = make_valid()
    bad["score"] = 1.5
    assert any("score" in e for e in validate_result(bad))


def test_bool_not_accepted_as_int():
    bad = make_valid()
    bad["agent_exit_code"] = True
    assert any("agent_exit_code" in e for e in validate_result(bad))
