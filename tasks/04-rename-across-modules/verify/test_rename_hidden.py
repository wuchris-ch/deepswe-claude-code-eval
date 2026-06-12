"""Hidden verification tests — never shown to the agent."""
import pytest


def test_new_name_exists_and_works():
    from store import load_records
    assert [u["name"] for u in load_records("users")] == ["ada", "grace"]


def test_old_name_fully_removed():
    import store
    assert not hasattr(store, "fetch_records")


def test_returns_copies_not_references():
    from store import load_records
    rows = load_records("users")
    rows[0]["name"] = "mutated"
    assert load_records("users")[0]["name"] == "ada"


def test_unknown_table_still_raises():
    from store import load_records
    with pytest.raises(KeyError):
        load_records("nope")
