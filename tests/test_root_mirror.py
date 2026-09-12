"""Enforce the static/ -> repo-root mirror contract (see AGENTS.md sync list).

Vercel serves the repo root (verified live 2026-08-10: deployed bytes ==
root index.html), so after any static/ edit the affected file must be
copied to the root before `vercel --prod` (docs/seo-audit.md §Root-Duplicate
Fix). This test fails loudly when a mirror is missing or stale.
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
STATIC_DIR = REPO_ROOT / "static"

# Only renames need listing; everything else mirrors 1:1 by name.
RENAMES = {
    "dpa.html": "data-processing-agreement.html",
}


def _mirror_map() -> dict[str, str]:
    static_files = {
        p.relative_to(STATIC_DIR).as_posix()
        for p in STATIC_DIR.rglob("*")
        if p.is_file()
    }
    return {rel: RENAMES.get(rel, rel) for rel in static_files}


def test_mirror_map_is_complete():
    """Every public file in static/ must be covered by the sync list.

    If this fails, a new file was added to static/ without deciding its
    root-mirror name — extend RENAMES or copy it to the root 1:1.
    """
    static_files = {
        p.relative_to(STATIC_DIR).as_posix()
        for p in STATIC_DIR.rglob("*")
        if p.is_file()
    }
    unmapped = static_files - set(RENAMES) - set(_mirror_map().keys())
    assert not unmapped, (
        f"new static/ file(s) without a root mirror decision: {sorted(unmapped)}"
    )


@pytest.mark.parametrize(
    "static_rel,root_rel", sorted(_mirror_map().items()), ids=lambda v: v
)
def test_root_mirror_is_byte_identical(static_rel, root_rel):
    src = STATIC_DIR / static_rel
    dst = REPO_ROOT / root_rel
    assert dst.exists(), (
        f"missing root mirror: {root_rel} — copy static/{static_rel} to root"
    )
    assert dst.read_bytes() == src.read_bytes(), (
        f"root/{root_rel} differs from static/{static_rel} — "
        "re-sync the mirror before vercel --prod"
    )
