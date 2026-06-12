"""Pagination helpers for list-backed APIs."""


def paginate(items, page, page_size):
    """Return the items for a 1-indexed page.

    Raises ValueError for page < 1 or page_size < 1.
    """
    if page < 1 or page_size < 1:
        raise ValueError("page and page_size must be >= 1")
    start = (page - 1) * page_size
    end = start + page_size
    return items[start:end]


def total_pages(n_items, page_size):
    if page_size < 1:
        raise ValueError("page_size must be >= 1")
    return (n_items + page_size - 1) // page_size
