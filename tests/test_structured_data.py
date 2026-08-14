"""Regression tests for structured data (JSON-LD) and SEO meta constraints.

Verifies the per-page JSON-LD inventory and the title/meta-description length
caps documented in docs/seo-* (all pages: title <= 60 chars, meta description
<= 150 chars). Pages under test are the `static/` sources of truth (root
mirrors must stay byte-identical per AGENTS.md).
"""
import json
import re
from pathlib import Path

import pytest

STATIC_DIR = Path(__file__).resolve().parent.parent / "static"

ALL_PAGES = ["index.html", "privacy.html", "impressum.html", "dpa.html", "404.html"]

LEGAL_PAGES = ["privacy.html", "impressum.html", "dpa.html"]


def _read_page(name: str) -> str:
    path = STATIC_DIR / name
    assert path.exists(), f"Missing page: {name}"
    return path.read_text(encoding="utf-8")


def _jsonld_blocks(html: str) -> list[dict]:
    raw_blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    return [json.loads(b.strip()) for b in raw_blocks]


def _root_types(block: dict) -> list[str]:
    t = block.get("@type")
    return [t] if isinstance(t, str) else list(t)


def _title(html: str) -> str:
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    assert m, "missing <title>"
    return m.group(1).strip()


def _description(html: str) -> str:
    m = re.search(r'name="description" content="(.*?)"', html, re.S)
    assert m, 'missing <meta name="description">'
    return m.group(1)


# ---------- JSON-LD inventory ----------


@pytest.mark.parametrize("page", LEGAL_PAGES)
def test_legal_pages_have_exactly_two_jsonld_blocks(page):
    blocks = _jsonld_blocks(_read_page(page))
    assert len(blocks) == 2, f"{page}: expected 2 JSON-LD blocks, got {len(blocks)}"
    assert {t for b in blocks for t in _root_types(b)} == {"Organization", "BreadcrumbList"}


@pytest.mark.parametrize("page", LEGAL_PAGES)
def test_legal_pages_have_organization_block(page):
    blocks = _jsonld_blocks(_read_page(page))
    org = next(b for b in blocks if "Organization" in _root_types(b))
    assert org.get("name") == "PhishDefend AI"
    assert org.get("url") == "https://phishdefend-ai.vercel.app/"


@pytest.mark.parametrize("page", LEGAL_PAGES)
def test_legal_pages_have_breadcrumblist_block(page):
    blocks = _jsonld_blocks(_read_page(page))
    bc = next(b for b in blocks if "BreadcrumbList" in _root_types(b))
    items = bc.get("itemListElement", [])
    assert len(items) == 2
    assert [i.get("position") for i in items] == [1, 2]
    assert isinstance(items[0].get("name"), str) and items[0]["name"]
    assert items[0].get("item", "").startswith("https://phishdefend-ai.vercel.app/")


def test_404_has_single_organization_jsonld():
    blocks = _jsonld_blocks(_read_page("404.html"))
    assert len(blocks) == 1, f"404.html: expected 1 JSON-LD block, got {len(blocks)}"
    assert _root_types(blocks[0]) == ["Organization"]


# ---------- SEO meta caps (all 5 pages) ----------


@pytest.mark.parametrize("page", ALL_PAGES)
def test_title_max_60_chars(page):
    assert len(_title(_read_page(page))) <= 60


@pytest.mark.parametrize("page", ALL_PAGES)
def test_meta_description_max_150_chars(page):
    assert len(_description(_read_page(page))) <= 150
