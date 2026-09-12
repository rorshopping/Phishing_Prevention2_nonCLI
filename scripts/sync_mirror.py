#!/usr/bin/env python3
"""Sync static/ -> repo-root mirrors (Vercel serves the repo root).

Usage:
    python scripts/sync_mirror.py            # copy stale/missing mirrors
    python scripts/sync_mirror.py --check    # verify only; exit 1 on drift

Run `--check` before `vercel --prod`; the same contract is enforced by
tests/test_root_mirror.py.
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.root_mirror import sync  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sync static/ mirrors to the repo root."
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify only, do not write (exit 1 when out of sync)",
    )
    args = parser.parse_args()

    copied, not_synced = sync(check_only=args.check)

    if args.check:
        if not_synced:
            print("OUT OF SYNC:")
            for rel in not_synced:
                print(f"  {rel}")
            return 1
        print("All mirrors in sync.")
        return 0

    for rel in copied:
        print(f"copied: {rel}")
    if not_synced:
        print("NOT SYNCED (fix the sync list in src/root_mirror.py):")
        for rel in not_synced:
            print(f"  {rel}")
        return 1
    if not copied:
        print("All mirrors in sync, nothing to do.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
