"""Enforce the static/ -> repo-root mirror contract (see AGENTS.md sync list).

Vercel serves the repo root (verified live 2026-08-10: deployed bytes ==
root index.html), so after any static/ edit the affected file must be
copied to the root before `vercel --prod` (docs/seo-audit.md §Root-Duplicate
Fix). The mapping lives in src/root_mirror.py; this test fails loudly when
a mirror is missing or stale, or when the sync list itself drifts from
static/ contents.
"""
import pytest

from src.root_mirror import EXPECTED_SYNC_LIST, RENAMES, diff, mirror_map, static_files


def test_sync_list_matches_static_contents():
    """Every file in static/ must be in EXPECTED_SYNC_LIST, and vice versa.

    A new static/ file must be added to the list (and mirrored); a removed
    one must be dropped from the list and its root mirror deleted.
    """
    actual = set(static_files())
    assert actual == set(EXPECTED_SYNC_LIST), (
        f"static/ contents diverged from the sync list: "
        f"unlisted={sorted(actual - set(EXPECTED_SYNC_LIST))} "
        f"stale-entries={sorted(set(EXPECTED_SYNC_LIST) - actual)}"
    )


def test_renames_point_at_sync_list():
    assert set(RENAMES) <= set(EXPECTED_SYNC_LIST)


def test_dpa_rename():
    assert mirror_map()["dpa.html"] == "data-processing-agreement.html"


@pytest.mark.parametrize(
    "static_rel,root_rel,state", sorted(diff()), ids=lambda v: v
)
def test_root_mirror_is_byte_identical(static_rel, root_rel, state):
    assert state != "missing-src", (
        f"static/{static_rel} is in the sync list but does not exist"
    )
    assert state != "missing", (
        f"missing root mirror: {root_rel} — copy static/{static_rel} to root "
        "(python scripts/sync_mirror.py)"
    )
    assert state == "in-sync", (
        f"root/{root_rel} differs from static/{static_rel} — "
        "re-sync the mirror before vercel --prod (python scripts/sync_mirror.py)"
    )
