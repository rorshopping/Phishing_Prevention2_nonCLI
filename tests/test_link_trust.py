"""Automated internal-link / trust regression test.

Crawls every served HTML page — both the `static/` sources and the root
mirrors that Vercel deploys (see AGENTS.md "Root mirror files") — and asserts:

  1. every `href` / `src` resolves to an existing file in the same tree,
  2. every fragment link (`#name`) has a matching `id` on the page it points to
     (same-page for `#name`, target page for `/path#name`),
  3. every internal link returns HTTP 200 against a local server that mimics
     Vercel's `cleanUrls` behaviour (when serving is available).

External links (other hosts, `mailto:`, `data:`) are intentionally excluded.
"""
import re
import threading
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
STATIC_DIR = REPO_ROOT / "static"

BASE_HOST = "phishdefend-ai.vercel.app"

# page name in static -> root mirror filename (Vercel serves repo root)
PAGES = [
    ("index.html", "index.html"),
    ("privacy.html", "privacy.html"),
    ("impressum.html", "impressum.html"),
    ("dpa.html", "data-processing-agreement.html"),
    ("404.html", "404.html"),
]

_ATTR_RE = re.compile(r'\s(?:href|src)="([^"]*)"')


def _iter_pages():
    """Yield (tree, page_name, path, html) for static + root trees."""
    for tree, base in (("static", STATIC_DIR), ("root", REPO_ROOT)):
        for static_name, root_name in PAGES:
            name = static_name if tree == "static" else root_name
            path = base / name
            yield tree, name, path, path.read_text(encoding="utf-8")


def _links(html):
    return _ATTR_RE.findall(html)


def _clean_map(tree):
    """Vercel cleanUrls: served URL path -> file name in the given tree."""
    return {
        "/": "index.html",
        "/privacy": "privacy.html",
        "/impressum": "impressum.html",
        "/data-processing-agreement": (
            "dpa.html" if tree == "static" else "data-processing-agreement.html"
        ),
        "/llms.txt": "llms.txt",
        "/llms-full.txt": "llms-full.txt",
        "/robots.txt": "robots.txt",
        "/sitemap.xml": "sitemap.xml",
    }


def _tree_dir(tree):
    return STATIC_DIR if tree == "static" else REPO_ROOT


def _split_url(url):
    """Return (served_path|None, fragment|None, kind) where kind in
    {'internal','external','skip'}."""
    url = url.strip()
    if not url:
        return None, None, "skip"
    if url.startswith("#"):
        return None, url[1:], "internal"
    if url.startswith(("mailto:", "tel:", "data:")):
        return None, None, "skip"
    if "://" in url:
        parsed = urlsplit(url)
        if parsed.netloc == BASE_HOST:
            return (parsed.path or "/"), parsed.fragment, "internal"
        return None, None, "external"
    path, _, frag = url.partition("#")
    if not path:
        return "/", frag, "internal"
    if path.startswith("/"):
        return path, frag, "internal"
    return "/" + path, frag, "internal"


def _resolve_file(tree, path):
    """Map a served URL path to the concrete file path in the tree."""
    if path in _clean_map(tree):
        return _tree_dir(tree) / _clean_map(tree)[path]
    return _tree_dir(tree) / path.lstrip("/")


def _id_targets(html):
    return set(re.findall(r'\bid="([^"]+)"', html))


# ---------- 1. every href/src resolves to an existing file ----------


@pytest.mark.parametrize("tree", ["static", "root"])
def test_all_internal_href_src_resolve_to_existing_file(tree):
    failures = []
    for _tree, _name, _path, html in _iter_pages():
        if _tree != tree:
            continue
        for url in _links(html):
            served, _frag, kind = _split_url(url)
            if kind != "internal" or served is None:
                continue
            target = _resolve_file(tree, served)
            if not target.exists():
                failures.append(f"{tree}/{_name}: {url!r} -> missing file {target}")
    assert not failures, "\n".join(failures)


# ---------- 2. fragment targets exist ----------


@pytest.mark.parametrize("tree", ["static", "root"])
def test_all_fragment_targets_exist(tree):
    failures = []
    for _tree, _name, _path, html in _iter_pages():
        if _tree != tree:
            continue
        page_ids = _id_targets(html)
        for url in _links(html):
            served, frag, kind = _split_url(url)
            if kind != "internal" or not frag:
                continue
            if served is None:
                target_ids = page_ids
                target_label = f"{tree}/{_name} (same page)"
            else:
                target = _resolve_file(tree, served)
                if not target.exists():
                    failures.append(f"{tree}/{_name}: {url!r} -> target file missing")
                    continue
                target_ids = _id_targets(target.read_text(encoding="utf-8"))
                target_label = f"{tree}/{_name}:{served} -> {target.name}"
            if frag not in target_ids:
                failures.append(f"{tree}/{_name}: fragment '#{frag}' ({url!r}) not found in {target_label}")
    assert not failures, "\n".join(failures)


# ---------- 3. internal links return HTTP 200 (local cleanUrls server) ----------


class _CleanUrlsHandler(SimpleHTTPRequestHandler):
    def _serve(self, raw_path: str):
        path = unquote(urlsplit(raw_path).path)
        if path.endswith("/"):
            path += "index.html"
        elif not Path(path).suffix and Path(self.directory + path + ".html").exists():
            path += ".html"
        self.path = path
        super().do_GET()

    def do_GET(self):
        self._serve(self.path)

    def do_HEAD(self):
        self._serve(self.path)

    def log_message(self, *args):
        pass


@pytest.fixture(scope="module")
def cleanurl_server():
    handler = partial(_CleanUrlsHandler, directory=str(REPO_ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_address[1]}"
    yield base
    server.shutdown()
    thread.join(timeout=5)


def _http_status(base_url, path):
    import urllib.request

    try:
        with urllib.request.urlopen(base_url + path, timeout=5) as resp:
            return resp.status
    except Exception:
        return 0


@pytest.mark.parametrize("tree", ["static", "root"])
def test_internal_links_return_200(tree, cleanurl_server):
    failures = []
    for _tree, _name, _path, html in _iter_pages():
        if _tree != tree:
            continue
        for url in _links(html):
            served, _frag, kind = _split_url(url)
            if kind != "internal" or served is None:
                continue
            status = _http_status(cleanurl_server, served)
            if status != 200:
                failures.append(f"{tree}/{_name}: {url!r} ({served}) -> HTTP {status}")
    assert not failures, "\n".join(failures)


# ---------- trust invariants ----------


def test_homepage_reachable_from_every_page():
    for _tree, _name, _path, html in _iter_pages():
        assert "/" in _links(html), f"{_tree}/{_name}: no link to homepage"
        # 404.html is a recovery page (noindex) — home link only is correct
        if _name == "404.html":
            continue
        assert "/privacy" in _links(html), f"{_tree}/{_name}: no link to /privacy"
        assert "/impressum" in _links(html), f"{_tree}/{_name}: no link to /impressum"
        assert "/data-processing-agreement" in _links(html), (
            f"{_tree}/{_name}: no link to /data-processing-agreement"
        )
