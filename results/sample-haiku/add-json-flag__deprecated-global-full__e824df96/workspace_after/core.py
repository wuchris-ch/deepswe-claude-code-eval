"""Numeric summary statistics. Shared with other internal tools."""


def summarize(values):
    if not values:
        raise ValueError("no values given")
    return {
        "count": len(values),
        "mean": sum(values) / len(values),
        "min": min(values),
        "max": max(values),
    }
