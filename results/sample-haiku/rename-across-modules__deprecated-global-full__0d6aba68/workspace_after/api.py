"""Thin API layer over the store."""

from store import load_records


def list_users():
    return load_records("users")


def list_orders():
    return load_records("orders")
