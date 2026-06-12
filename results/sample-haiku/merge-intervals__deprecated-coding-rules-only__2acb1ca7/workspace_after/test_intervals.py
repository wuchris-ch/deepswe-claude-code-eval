from intervals import merge


def test_empty():
    assert merge([]) == []


def test_disjoint_kept():
    assert merge([(1, 2), (4, 5)]) == [(1, 2), (4, 5)]


def test_overlap_merged():
    assert merge([(1, 4), (2, 6)]) == [(1, 6)]


def test_touching_endpoints_merge():
    # closed intervals sharing an endpoint must merge
    assert merge([(1, 3), (3, 5)]) == [(1, 5)]


def test_unsorted_input():
    assert merge([(5, 7), (1, 3), (2, 4)]) == [(1, 4), (5, 7)]
