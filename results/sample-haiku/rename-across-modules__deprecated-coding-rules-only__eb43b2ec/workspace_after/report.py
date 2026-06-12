"""Revenue report built directly on the store (legacy path)."""

import store


def revenue_total():
    orders = store.load_records("orders")
    return sum(o["total"] for o in orders)
