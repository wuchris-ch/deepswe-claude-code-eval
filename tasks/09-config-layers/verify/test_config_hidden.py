"""Hidden verification for the config-layers spec (module docstrings)."""

import copy

import pytest

from expand import expand
from loader import load_layers
from merge import deep_merge


# --- deep_merge -------------------------------------------------------------

def test_lists_replace_never_concatenate():
    assert deep_merge({"a": [1, 2]}, {"a": [3]}) == {"a": [3]}


def test_none_deletes_nested_key():
    base = {"db": {"host": "a", "password": "secret"}}
    assert deep_merge(base, {"db": {"password": None}}) == {"db": {"host": "a"}}


def test_none_delete_of_missing_key_is_noop():
    assert deep_merge({"a": 1}, {"b": None}) == {"a": 1}


def test_merge_never_mutates_at_any_depth():
    base = {"db": {"opts": {"x": 1}, "tags": [1, 2]}}
    over = {"db": {"opts": {"y": 2}, "tags": [9]}}
    base_copy = copy.deepcopy(base)
    over_copy = copy.deepcopy(over)
    result = deep_merge(base, over)
    assert base == base_copy and over == over_copy
    result["db"]["opts"]["x"] = 99
    result["db"]["tags"].append(99)
    assert base == base_copy and over == over_copy


def test_merge_dict_replaces_scalar_and_vice_versa():
    assert deep_merge({"a": 1}, {"a": {"b": 2}}) == {"a": {"b": 2}}
    assert deep_merge({"a": {"b": 2}}, {"a": 1}) == {"a": 1}


# --- expand -----------------------------------------------------------------

def test_default_may_contain_colons():
    assert expand("${HOST:http://localhost:8080}", {}) == "http://localhost:8080"
    assert expand("${HOST:http://localhost:8080}", {"HOST": "prod"}) == "prod"


def test_dollar_dollar_escapes():
    assert expand("$$", {}) == "$"
    assert expand("$${X}", {"X": "v"}) == "${X}"
    assert expand("cost: $$5 for ${ITEM}", {"ITEM": "tea"}) == "cost: $5 for tea"


def test_missing_var_without_default_raises_keyerror():
    with pytest.raises(KeyError):
        expand("${MISSING}", {})


def test_lists_are_expanded_recursively():
    value = {"servers": ["${A}", {"url": "${B:fallback}"}], "n": 3}
    assert expand(value, {"A": "a"}) == {"servers": ["a", {"url": "fallback"}], "n": 3}


def test_expand_returns_new_containers():
    inner = ["${A}"]
    value = {"list": inner}
    out = expand(value, {"A": "x"})
    out["list"].append("extra")
    assert inner == ["${A}"]


def test_multiple_refs_in_one_string():
    assert expand("${A}-${B}", {"A": "1", "B": "2"}) == "1-2"


# --- load_layers ------------------------------------------------------------

def test_loader_merges_then_expands():
    layers = [
        {"db": {"url": "${DB_URL:sqlite://}", "pool": 5}, "debug": True},
        {"db": {"url": "${PROD_DB}"}, "debug": None},
    ]
    cfg = load_layers(layers, {"PROD_DB": "postgres://prod"})
    assert cfg == {"db": {"url": "postgres://prod", "pool": 5}}


def test_loader_empty_and_no_mutation():
    assert load_layers([], {}) == {}
    layers = [{"a": "${X:1}"}, {"b": [1]}]
    snapshot = copy.deepcopy(layers)
    load_layers(layers, {})
    assert layers == snapshot


def test_loader_three_layer_precedence():
    layers = [{"a": 1, "b": 1, "c": 1}, {"b": 2, "c": 2}, {"c": 3}]
    assert load_layers(layers, {}) == {"a": 1, "b": 2, "c": 3}
