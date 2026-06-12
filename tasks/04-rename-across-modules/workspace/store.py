"""In-memory record store."""

_DB = {
    "users": [{"id": 1, "name": "ada"}, {"id": 2, "name": "grace"}],
    "orders": [{"id": 10, "user_id": 1, "total": 25.0}],
}


def fetch_records(table):
    """fetch_records returns a copy of all rows in `table`."""
    if table not in _DB:
        raise KeyError(f"unknown table: {table}")
    return [dict(row) for row in _DB[table]]
