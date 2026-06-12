"""Hidden verification tests — never shown to the agent."""
from intervals import merge


def test_chain_of_touching():
    assert merge([(1, 2), (2, 3), (3, 4)]) == [(1, 4)]


def test_contained_interval():
    assert merge([(1, 10), (3, 4)]) == [(1, 10)]


def test_identical_intervals():
    assert merge([(2, 5), (2, 5)]) == [(2, 5)]


def test_overlap_still_merges():
    assert merge([(0, 5), (4, 9)]) == [(0, 9)]


def test_disjoint_preserved():
    assert merge([(0, 1), (5, 6), (10, 11)]) == [(0, 1), (5, 6), (10, 11)]
