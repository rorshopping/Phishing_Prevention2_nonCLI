"""static/ -> repo-root mirror sync (Vercel serves the repo root).

`static/` is the source of truth; the repo root is what Vercel deploys, so
every public file in static/ must be mirrored byte-for-byte before
`vercel --prod` (AGENTS.md sync list, docs/seo-audit.md §Root-Duplicate Fix).

Single source of truth for the mapping — consumed by
tests/test_root_mirror.py and scripts/sync_mirror.py.
"""
import shutil
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "static"

# The AGENTS.md sync list: every public file in static/. Keep in sync with
# that table — the contract test fails when a file is added or removed here
# without updating the list (and vice versa).
EXPECTED_SYNC_LIST = {
    "404.html",
    "analytics.js",
    "console.css",
    "console.html",
    "console.js",
    "dpa.html",
    "fonts/inter-variable.woff2",
    "fonts/jetbrains-mono-variable.woff2",
    "impressum.html",
    "index.html",
    "llms-full.txt",
    "llms.txt",
    "logo.svg",
    "og-image.png",
    "privacy.html",
    "robots.txt",
    "script.js",
    "script.min.js",
    "sitemap.xml",
    "style.css",
    "style.min.css",
}

# Only renames need listing; every other static/ file mirrors 1:1 by name.
RENAMES = {
    "dpa.html": "data-processing-agreement.html",
}


def static_files() -> dict[str, Path]:
    """Every file currently in static/, as {relative posix path: Path}."""
    return {
        p.relative_to(STATIC_DIR).as_posix(): p
        for p in sorted(STATIC_DIR.rglob("*"))
        if p.is_file()
    }


def mirror_map() -> dict[str, str]:
    """static/ relative path -> repo-root relative path, for the sync list."""
    return {rel: RENAMES.get(rel, rel) for rel in sorted(EXPECTED_SYNC_LIST)}


def diff() -> list[tuple[str, str, str]]:
    """Return (static_rel, root_rel, state) for every mirror in the sync list.

    state is "in-sync", "stale", "missing" (root copy absent), or
    "missing-src" (static/ source absent — the sync list needs updating).
    """
    out = []
    for static_rel, root_rel in mirror_map().items():
        src = STATIC_DIR / static_rel
        dst = REPO_ROOT / root_rel
        if not src.exists():
            state = "missing-src"
        elif not dst.exists():
            state = "missing"
        elif dst.read_bytes() != src.read_bytes():
            state = "stale"
        else:
            state = "in-sync"
        out.append((static_rel, root_rel, state))
    return out


def sync(check_only: bool = False) -> tuple[list[str], list[str]]:
    """Copy stale/missing mirrors. Returns (copied, not_synced).

    With check_only=True nothing is written and every out-of-sync file is
    returned in not_synced (as "path (state)").
    """
    copied: list[str] = []
    not_synced: list[str] = []
    for static_rel, root_rel, state in diff():
        if state == "in-sync":
            continue
        if check_only:
            not_synced.append(f"{root_rel} ({state})")
            continue
        if state == "missing-src":
            not_synced.append(f"{root_rel} ({state})")
            continue
        dst = REPO_ROOT / root_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(STATIC_DIR / static_rel, dst)
        copied.append(root_rel)
    return copied, not_synced
