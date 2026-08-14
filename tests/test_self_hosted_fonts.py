"""Regression tests for self-hosted fonts.

Asserts that no Google Fonts (fonts.googleapis.com / fonts.gstatic.com)
references remain in any served HTML page, and that index.html preloads both
self-hosted variable fonts (/fonts/inter-variable.woff2,
/fonts/jetbrains-mono-variable.woff2) used by style.css @font-face rules.
"""
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = REPO_ROOT / "static"

ALL_PAGES = ["index.html", "privacy.html", "impressum.html", "dpa.html", "404.html"]

FONT_PRELOADS = [
    "/fonts/inter-variable.woff2",
    "/fonts/jetbrains-mono-variable.woff2",
]

EXTERNAL_FONT_PATTERNS = ["fonts.googleapis.com", "fonts.gstatic.com"]


def _read(name: str) -> str:
    path = STATIC_DIR / name
    assert path.exists(), f"Missing page: {name}"
    return path.read_text(encoding="utf-8")


@pytest.mark.parametrize("page", ALL_PAGES)
def test_no_external_google_fonts_reference(page):
    html = _read(page)
    for pattern in EXTERNAL_FONT_PATTERNS:
        assert pattern not in html, f"{page}: external font reference '{pattern}' present"


@pytest.mark.parametrize("font", FONT_PRELOADS)
def test_index_preloads_self_hosted_font(font):
    html = _read("index.html")
    preload = re.search(r'<link rel="preload"[^>]*href="%s"[^>]*>' % re.escape(font), html)
    assert preload, f"index.html: missing preload for {font}"


def test_font_files_exist_and_mirrored():
    for font in FONT_PRELOADS:
        rel = font.lstrip("/")
        static_font = STATIC_DIR / rel
        root_font = REPO_ROOT / rel
        assert static_font.exists(), f"missing static font: {rel}"
        assert root_font.exists(), f"missing root font mirror: {rel}"
        assert static_font.read_bytes() == root_font.read_bytes(), f"root/static font differ: {rel}"
