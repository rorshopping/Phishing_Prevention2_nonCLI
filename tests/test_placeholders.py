"""Regression tests for the contact-placeholder fix.

Asserts that the real contact email is present (and the old placeholder is
gone) in `impressum.html` and `privacy.html` — in both the `static/` sources
and the root mirrors served by Vercel — while the DPA intentionally keeps its
generic `[Client Company Name, Address]` placeholder for per-client fill-in.
"""
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = REPO_ROOT / "static"

CONTACT_EMAIL = "rorshopping@gmail.com"
OLD_PLACEHOLDER = "[your@email.com]"
DPA_PLACEHOLDER = "[Client Company Name, Address]"
DPO_PLACEHOLDER = "[dpo@email.com]"

# page label -> (root file, static file)
PAGES_WITH_CONTACT = {
    "impressum": ("impressum.html", "impressum.html"),
    "privacy": ("privacy.html", "privacy.html"),
}

# DPA root file maps to static/dpa.html (name differs)
DPA_PAGES = {
    "dpa": ("data-processing-agreement.html", "dpa.html"),
}


def _read(path: Path) -> str:
    assert path.exists(), f"Missing file: {path}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("label", list(PAGES_WITH_CONTACT))
@pytest.mark.parametrize("location", ["root", "static"])
def test_contact_email_present(label, location):
    root_file, static_file = PAGES_WITH_CONTACT[label]
    path = REPO_ROOT / root_file if location == "root" else STATIC_DIR / static_file
    assert CONTACT_EMAIL in _read(path)


@pytest.mark.parametrize("label", list(PAGES_WITH_CONTACT))
@pytest.mark.parametrize("location", ["root", "static"])
def test_old_placeholder_removed(label, location):
    root_file, static_file = PAGES_WITH_CONTACT[label]
    path = REPO_ROOT / root_file if location == "root" else STATIC_DIR / static_file
    assert OLD_PLACEHOLDER not in _read(path)


@pytest.mark.parametrize("label", list(DPA_PAGES))
@pytest.mark.parametrize("location", ["root", "static"])
def test_dpa_keeps_client_placeholder(label, location):
    root_file, static_file = DPA_PAGES[label]
    path = REPO_ROOT / root_file if location == "root" else STATIC_DIR / static_file
    assert DPA_PLACEHOLDER in _read(path)
    assert CONTACT_EMAIL not in _read(path)


@pytest.mark.parametrize("label", list(PAGES_WITH_CONTACT))
def test_root_mirrors_static_contact_pages(label):
    root_file, static_file = PAGES_WITH_CONTACT[label]
    assert _read(REPO_ROOT / root_file) == _read(STATIC_DIR / static_file)


# ---------- DPO-email fix (privacy pages, both copies) ----------


@pytest.mark.parametrize("location", ["root", "static"])
def test_privacy_dpo_placeholder_removed(location):
    path = REPO_ROOT / "privacy.html" if location == "root" else STATIC_DIR / "privacy.html"
    assert DPO_PLACEHOLDER not in _read(path)


@pytest.mark.parametrize("location", ["root", "static"])
def test_privacy_contact_email_present(location):
    path = REPO_ROOT / "privacy.html" if location == "root" else STATIC_DIR / "privacy.html"
    assert CONTACT_EMAIL in _read(path)


def test_privacy_root_mirrors_static():
    assert _read(REPO_ROOT / "privacy.html") == _read(STATIC_DIR / "privacy.html")
