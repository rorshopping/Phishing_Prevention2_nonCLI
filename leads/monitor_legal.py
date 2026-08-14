#!/usr/bin/env python3
"""Monitor leads/contacts-v1.md for agent 0's Legal email-collection section.

Waits until a '#'/'##' heading matching legal keywords (legal/law/kanzlei/
anwalt/rechts) appears with '### ' company blocks underneath, then prints the
section header and company blocks and exits 0.
"""

from __future__ import annotations

import re
import sys
import time
from pathlib import Path

MD = Path("leads/contacts-v1.md")
POLL_SECONDS = 15

LEGAL_RE = re.compile(r"\b(legal|law|anwalt|kanzlei|rechts)\b", re.IGNORECASE)
COMPANY_RE = re.compile(r"^### ")
BLOCK_HEAD_RE = re.compile(r"^#{1,2} ")


def find_legal_section(text: str):
    """Return (header_line, [company_lines]) for the first legal section, else None."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if not (line.startswith("# ") or line.startswith("## ")):
            continue
        if not LEGAL_RE.search(line):
            continue
        blocks = []
        for j in range(i + 1, len(lines)):
            l = lines[j]
            if l.startswith("# ") or l.startswith("## "):
                break
            if l.startswith("### "):
                blocks.append(l)
        return line, blocks
    return None


def main() -> int:
    start = time.time()
    while True:
        try:
            text = MD.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            text = ""
            print(f"[monitor] read error: {exc}", flush=True)
        found = find_legal_section(text)
        if found is not None and found[1]:
            header, blocks = found
            print(f"LEGAL SECTION FOUND: {header}", flush=True)
            print(f"company blocks: {len(blocks)}", flush=True)
            for b in blocks:
                print(f"  {b}", flush=True)
            return 0
        elapsed = int(time.time() - start)
        if elapsed % 60 < POLL_SECONDS:
            print(f"[monitor] {elapsed}s: no legal section yet", flush=True)
        time.sleep(POLL_SECONDS)


if __name__ == "__main__":
    sys.exit(main())
