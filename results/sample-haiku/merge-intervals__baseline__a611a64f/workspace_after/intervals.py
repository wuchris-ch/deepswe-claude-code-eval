"""Closed-interval utilities used by the scheduling service."""


def merge(intervals):
    """Merge overlapping or touching closed intervals.

    [(1, 3), (3, 5)] merges to [(1, 5)] because closed intervals that share
    an endpoint touch.
    """
    if not intervals:
        return []
    ordered = sorted(intervals)
    merged = [ordered[0]]
    for start, end in ordered[1:]:
        last_start, last_end = merged[-1]
        if start <= last_end:
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged
