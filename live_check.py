#!/usr/bin/env python3
"""live_check.py — automated post-deploy verification for PhishDefend AI.

Executes the 10-point post-deploy checklist from docs/deploy-instructions.md
(section 5) against the live site.

Usage:
    python live_check.py [BASE_URL]

Default BASE_URL is https://phishdefend-ai.vercel.app
Exit code: 0 = all checks pass, 1 = one or more checks fail.
Only the Python standard library is used.
"""
from __future__ import annotations

import json
import re
import sys
import urllib.error
import urllib.request

BASE = (sys.argv[1] if len(sys.argv) > 1 else "https://phishdefend-ai.vercel.app").rstrip("/")
UA = "live_check.py/1.0 (PhishDefend AI post-deploy checker)"
TIMEOUT = 30

# Canonical URL for each indexable page (must be self-referencing).
CANONICALS = {
    "/": BASE + "/",
    "/impressum": BASE + "/impressum",
    "/privacy": BASE + "/privacy",
    "/data-processing-agreement": BASE + "/data-processing-agreement",
}

# Expected JSON-LD @types per page (docs/deploy-instructions.md §5.4).
EXPECTED_JSONLD = {
    "/": {"Organization", "WebSite", "BreadcrumbList", "SoftwareApplication", "Service", "FAQPage"},
    "/impressum": {"Organization", "BreadcrumbList"},
    "/privacy": {"Organization", "BreadcrumbList"},
    "/data-processing-agreement": {"Organization", "BreadcrumbList"},
    "/404": {"Organization"},
}

FONTS = ["/fonts/inter-variable.woff2", "/fonts/jetbrains-mono-variable.woff2"]

# Marker text that identifies the styled 404 page (static/404.html).
NOT_FOUND_MARKER = "phishing test"

results: list[tuple[str, bool | None, str]] = []  # (check, pass/fail/warn, evidence)


def fetch(url: str, timeout: int = TIMEOUT) -> tuple[int, dict, str]:
    """GET url; returns (status, headers, body). Follows redirects. Raises on transport error."""
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode("utf-8", "replace")


def attr(tag: str, name: str) -> str | None:
    m = re.search(name + r'\s*=\s*["\']([^"\']+)["\']', tag, re.I)
    return m.group(1) if m else None


def tags(html: str, pattern: str) -> list[str]:
    return re.findall(pattern, html, re.I | re.S)


def report(label: str, ok: bool | None, evidence: str) -> None:
    results.append((label, ok, evidence))
    status = "PASS" if ok is True else ("FAIL" if ok is False else "WARN")
    print(f"[{status}] {label}\n      {evidence}")


# ---------------------------------------------------------------- checks

def c1_sitemap_urls() -> None:
    """1. HTTP 200 for all sitemap URLs."""
    status, _, body = fetch(BASE + "/sitemap.xml")
    locs = tags(body, r"<loc>\s*([^<]+?)\s*</loc>")
    if status != 200 or not locs:
        report("1. All sitemap URLs return HTTP 200", False, f"sitemap status={status}, loc entries={len(locs)}")
        return
    bad = []
    for loc in locs:
        s, _, _ = fetch(loc)
        if s != 200:
            bad.append(f"{loc} -> {s}")
    report("1. All sitemap URLs return HTTP 200", not bad, f"{len(locs)} URLs: " + (", ".join(bad) if bad else "all 200"))


def c2_privacy_email() -> None:
    """2. /privacy serves the DPO email, no placeholder."""
    status, _, body = fetch(BASE + "/privacy")
    has = "rorshopping@gmail.com" in body
    no_placeholder = "[dpo@email.com]" not in body and "[your@email.com]" not in body
    report("2. Privacy page serves DPO email (no placeholder)",
           status == 200 and has and no_placeholder,
           f"status={status}, rorshopping@gmail.com={'yes' if has else 'NO'}, "
           f"placeholder={'PRESENT' if not no_placeholder else 'absent'}")


def c3_canonicals() -> None:
    """3. Self-referencing canonical on each indexable page."""
    bad = []
    for path, expect in CANONICALS.items():
        status, _, body = fetch(BASE + path)
        links = tags(body, r"<link[^>]+>")
        hrefs = [attr(l, "href") for l in links if (attr(l, "rel") or "").lower() == "canonical"]
        if status != 200 or hrefs != [expect]:
            bad.append(f"{path}: status={status}, canonical={hrefs} (want [{expect}])")
    report("3. Self-referencing canonicals", not bad, "; ".join(bad) if bad else "all 4 pages exact-match")


def c4_no_google_fonts() -> None:
    """4. Zero fonts.googleapis.com / fonts.gstatic.com references."""
    bad = []
    for path in ("/", "/impressum", "/privacy", "/data-processing-agreement", "/404"):
        _, _, body = fetch(BASE + path)
        for needle in ("fonts.googleapis.com", "fonts.gstatic.com"):
            if needle in body:
                bad.append(f"{path} contains {needle}")
    report("4. Zero Google Fonts references", not bad, "; ".join(bad) if bad else "no googleapis/gstatic on 5 pages")


def c5_jsonld() -> None:
    """5. JSON-LD blocks intact and parseable, expected types present."""
    bad = []
    for path, expected in EXPECTED_JSONLD.items():
        status, _, body = fetch(BASE + path)
        blocks = tags(body, r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>', )
        if status != 200:
            bad.append(f"{path}: status={status}")
            continue
        types: set[str] = set()
        for i, raw in enumerate(blocks):
            try:
                data = json.loads(raw.strip())
            except json.JSONDecodeError as e:
                bad.append(f"{path} block {i}: invalid JSON ({e})")
                continue
            t = data.get("@type") if isinstance(data, dict) else None
            if isinstance(t, list):
                types.update(x for x in t if isinstance(x, str))
            elif isinstance(t, str):
                types.add(t)
        missing = sorted(expected - types)
        if missing:
            bad.append(f"{path}: {len(blocks)} blocks, missing {missing}")
    report("5. JSON-LD blocks intact (expected types present)", not bad,
           "; ".join(bad) if bad else "all pages parse, expected @types present")


def c6_og_twitter_images() -> None:
    """6. og:image and twitter:image resolve HTTP 200."""
    bad = []
    seen: set[str] = set()
    for path in ("/", "/impressum", "/privacy", "/data-processing-agreement"):
        _, _, body = fetch(BASE + path)
        metas = tags(body, r"<meta[^>]+>")
        for m in metas:
            prop = (attr(m, "property") or attr(m, "name") or "").lower()
            if prop in ("og:image", "twitter:image"):
                url = attr(m, "content")
                if url and url not in seen:
                    seen.add(url)
                    s, _, _ = fetch(url)
                    if s != 200:
                        bad.append(f"{url} -> {s}")
    report("6. og:image / twitter:image resolve 200", not bad,
           f"{len(seen)} unique image URL(s): " + (", ".join(bad) if bad else "all 200"))


def c7_cache_headers() -> None:
    """7. robots.txt and sitemap.xml served with max-age=3600."""
    bad = []
    for path, want in (("/robots.txt", "max-age=3600"), ("/sitemap.xml", "max-age=3600")):
        status, hdrs, body = fetch(BASE + path)
        cc = hdrs.get("Cache-Control", "")
        if status != 200 or want not in cc:
            bad.append(f"{path}: status={status}, Cache-Control={cc!r}")
        if path == "/robots.txt" and "Sitemap: " not in body:
            bad.append("/robots.txt missing Sitemap directive")
    report("7. robots.txt / sitemap.xml cache headers", not bad, "; ".join(bad) if bad else "both max-age=3600, robots has Sitemap")


def c8_fonts_immutable() -> None:
    """8. woff2 fonts served with immutable cache."""
    bad = []
    for path in FONTS:
        status, hdrs, _ = fetch(BASE + path)
        cc = hdrs.get("Cache-Control", "")
        if status != 200 or "immutable" not in cc:
            bad.append(f"{path}: status={status}, Cache-Control={cc!r}")
    report("8. woff2 fonts immutable cache", not bad, "; ".join(bad) if bad else "both fonts 200 + immutable")


def c9_404_page() -> None:
    """9. /404 serves the styled 404 page (200); nonexistent path -> 404 with styled page."""
    bad = []
    status, _, body = fetch(BASE + "/404")
    if status != 200 or NOT_FOUND_MARKER not in body:
        bad.append(f"/404: status={status}, styled-marker={'yes' if NOT_FOUND_MARKER in body else 'NO'}")
    status2, _, body2 = fetch(BASE + "/nonexistent-check-8f3a2c")
    if status2 != 404 or NOT_FOUND_MARKER not in body2:
        bad.append(f"/nonexistent: status={status2} (want 404), styled-marker={'yes' if NOT_FOUND_MARKER in body2 else 'NO'}")
    report("9. 404 page (styled, /404=200, unknown path=404)", not bad, "; ".join(bad) if bad else "/404=200 styled; unknown path=404 styled")


def c10_llms() -> None:
    """10. llms.txt and llms-full.txt return 200."""
    bad = []
    for path in ("/llms.txt", "/llms-full.txt"):
        status, _, _ = fetch(BASE + path)
        if status != 200:
            bad.append(f"{path} -> {status}")
    report("10. llms.txt / llms-full.txt return 200", not bad, "; ".join(bad) if bad else "both 200")


# ---------------------------------------------------------------- main

def main() -> int:
    print(f"Post-deploy check against {BASE}\n")
    c1_sitemap_urls()
    c2_privacy_email()
    c3_canonicals()
    c4_no_google_fonts()
    c5_jsonld()
    c6_og_twitter_images()
    c7_cache_headers()
    c8_fonts_immutable()
    c9_404_page()
    c10_llms()

    failed = [r for r in results if r[1] is False]
    warns = [r for r in results if r[1] is None]
    print(f"\nSummary: {len(results) - len(failed)}/{len(results)} pass"
          f"{f', {len(warns)} warn' if warns else ''}"
          f"{f', {len(failed)} FAIL' if failed else ''}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
