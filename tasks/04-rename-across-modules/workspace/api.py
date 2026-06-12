"""Thin API layer over the store."""

from store import fetch_records


def list_users():
    return fetch_records("users")


def list_orders():
    return fetch_records("orders")
