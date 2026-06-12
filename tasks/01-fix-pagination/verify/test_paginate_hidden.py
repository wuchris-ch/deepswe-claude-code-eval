"""Hidden verification tests — never shown to the agent."""
import pytest

from paginate import paginate, total_pages


def test_exact_multiple():
    assert paginate(list(range(9)), page=3, page_size=3) == [6, 7, 8]


def test_page_size_one():
    assert paginate(["a", "b", "c"], page=2, page_size=1) == ["b"]


def test_page_beyond_end_is_empty():
    assert paginate(list(range(4)), page=3, page_size=3) == []


def test_large_page_size():
    assert paginate(list(range(5)), page=1, page_size=100) == list(range(5))


def test_total_pages_exact():
    assert total_pages(9, 3) == 3


def test_rejects_bad_page_size():
    with pytest.raises(ValueError):
        paginate([1], page=1, page_size=0)
