"""Tiny CLI app entry point."""

from messy import format_name


def greeting(name):
    return f"Welcom, {format_name(name)}!"


if __name__ == "__main__":
    import sys
    print(greeting(sys.argv[1] if len(sys.argv) > 1 else "friend"))
