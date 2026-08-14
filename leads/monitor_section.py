#!/usr/bin/env python3
"""Monitor leads/contacts-v1.md for a specific email-collection section.

Waits until a '#'/'##' heading matching --section-regex appears with '### '
company blocks underneath, AND all --domains are present in that section, then
prints the section header + company blocks and exits 0.

Usage:
    python leads/monitor_section.py --section-regex "(benelux|netherlands|belgium)" \
        --domains kembit.nl,itility.nl,appsys.be
"""

from __future__ import annotations

import argparse
import re
import sys
import time
from pathlib import Path


def find_section(text: str, sect_re: re.Pattern):
    """Return (header, [company_lines], section_text) for the first matching
    '# ' / '## ' section, or (None, [], '')."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not (line.startswith("# ") or line.startswith("## ")):
            continue
        if not sect_re.search(line):
            continue
        blocks: list[str] = []
        for j in range(i + 1, len(lines)):
            l = lines[j]
            if l.startswith("# ") or l.startswith("## "):
                break
            if l.startswith("### "):
                blocks.append(l)
        return line, blocks, "\n".join(lines[i:])
    return None, [], ""


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--file", default="leads/contacts-v1.md")
    p.add_argument("--section-regex", required=True)
    p.add_argument("--domains", required=True, help="comma-separated expected domains")
    p.add_argument("--poll", type=int, default=15)
    args = p.parse_args()

    expected = {d.strip().lower().lstrip("www.") for d in args.domains.split(",") if d.strip()}
    sect_re = re.compile(args.section_regex, re.IGNORECASE)
    md = Path(args.file)
    start = time.time()

    while True:
        try:
            text = md.read_text(encoding="utf-8", errors="replace")
        except OSError:
            text = ""
        header, blocks, section_text = find_section(text, sect_re)
        if header:
            present = {d for d in expected if d in section_text}
            print(
                f"[monitor] {int(time.time() - start)}s: section='{header}' "
                f"blocks={len(blocks)} expected-present={len(present)}/{len(expected)}",
                flush=True,
            )
            if present == expected and blocks:
                print("SECTION COMPLETE", flush=True)
                for b in blocks:
                    print(f"  {b}", flush=True)
                return 0
        else:
            if int(time.time() - start) % 60 < args.poll:
                print(f"[monitor] {int(time.time() - start)}s: section not found yet", flush=True)
        time.sleep(args.poll)


if __name__ == "__main__":
    sys.exit(main())
