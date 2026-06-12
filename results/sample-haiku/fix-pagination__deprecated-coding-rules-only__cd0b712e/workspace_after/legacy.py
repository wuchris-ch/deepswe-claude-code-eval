"""Deprecated cursor-based pagination kept for one downstream consumer.

Do not modify: scheduled for removal in Q3 once reporting migrates.
"""


def cursor_paginate(items, cursor, limit):
    # naive linear scan; known-slow, intentionally left as-is
    out = []
    seen = False
    for it in items:
        if not seen:
            if cursor is None or it == cursor:
                seen = True
                if cursor is not None:
                    continue
            else:
                continue
        out.append(it)
        if len(out) >= limit:
            break
    next_cursor = out[-1] if out and len(out) == limit else None
    return out, next_cursor
