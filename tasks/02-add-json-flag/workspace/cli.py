"""stats: print summary statistics for numbers given on the command line."""

import argparse

from core import summarize


def build_parser():
    parser = argparse.ArgumentParser(prog="stats")
    parser.add_argument("values", nargs="+", type=float)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    stats = summarize(args.values)
    print(f"count: {stats['count']}")
    print(f"mean: {stats['mean']:.4g}")
    print(f"min: {stats['min']:.4g}")
    print(f"max: {stats['max']:.4g}")


if __name__ == "__main__":
    main()
