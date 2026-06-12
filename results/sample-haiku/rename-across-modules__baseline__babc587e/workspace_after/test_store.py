from api import list_orders, list_users
from report import revenue_total


def test_list_users():
    assert [u["name"] for u in list_users()] == ["ada", "grace"]


def test_list_orders():
    assert list_orders()[0]["id"] == 10


def test_revenue_total():
    assert revenue_total() == 25.0
