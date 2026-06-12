"""Visible tests. These encode part of the spec in the module docstrings
and must not be weakened — the full spec is also exercised elsewhere."""

from expand import expand
from loader import load_layers
from merge import deep_merge


def test_merge_recurses_into_dicts():
    base = {"db": {"host": "a", "port": 1}, "x": 1}
    over = {"db": {"host": "b"}}
    assert deep_merge(base, over) == {"db": {"host": "b", "port": 1}, "x": 1}


def test_merge_none_deletes_key():
    assert deep_merge({"a": 1, "b": 2}, {"b": None}) == {"a": 1}


def test_merge_does_not_mutate_inputs():
    base = {"db": {"host": "a"}}
    over = {"db": {"host": "b"}}
    deep_merge(base, over)
    assert base == {"db": {"host": "a"}}


def test_expand_basic_and_default():
    assert expand("${HOST}", {"HOST": "h"}) == "h"
    assert expand("${HOST:fallback}", {}) == "fallback"


def test_loader_later_layers_win():
    cfg = load_layers([{"a": 1}, {"a": 2}], {})
    assert cfg == {"a": 2}
