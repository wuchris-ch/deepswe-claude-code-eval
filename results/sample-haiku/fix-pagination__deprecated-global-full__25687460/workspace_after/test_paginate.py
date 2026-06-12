import pytest

from paginate import paginate, total_pages


def test_full_page():
    assert paginate(list(range(10)), page=1, page_size=3) == [0, 1, 2]


def test_second_page():
    assert paginate(list(range(10)), page=2, page_size=3) == [3, 4, 5]


def test_last_partial_page():
    assert paginate(list(range(10)), page=4, page_size=3) == [9]


def test_total_pages():
    assert total_pages(10, 3) == 4


def test_rejects_bad_page():
    with pytest.raises(ValueError):
        paginate([1, 2], page=0, page_size=2)
