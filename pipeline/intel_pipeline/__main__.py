from __future__ import annotations

import argparse
import sys

from .collect import run_collect
from .weekly import run_weekly


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Physical AI market intel pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("collect", help="Fetch RSS, dedup, write source cards + daily logs")

    wp = sub.add_parser("weekly", help="Build weekly strategy report from recent DB rows")
    wp.add_argument("--days", type=int, default=7, help="Lookback window (default 7)")

    args = p.parse_args(argv)
    if args.cmd == "collect":
        return run_collect()
    if args.cmd == "weekly":
        return run_weekly(days=args.days)
    return 1


if __name__ == "__main__":
    sys.exit(main())
