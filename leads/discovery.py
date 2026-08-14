#!/usr/bin/env python3
"""Discovery: crawl prospect contact/impressum pages and extract public business emails.

Input : leads/leads.csv website column (fallback: leads/contacts-v1.md company sections)
Output: appends rows to leads/raw-contacts.csv (deduplicated) - the ONLY output file

Columns:
    domain,company,page_type,page_url,email,found_at

Usage:
    python leads/discovery.py
    python leads/discovery.py --md leads/leads.csv --csv leads/raw-contacts.csv
"""

from __future__ import annotations

import argparse
import csv
import html
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36"
)
TIMEOUT = 15
MAX_PAGE_BYTES = 2_000_000
MAX_PAGES_PER_DOMAIN = 8
MAX_EMAILS_PER_PAGE = 25

COMMON_PATHS = [
    "/impressum", "/impressum/",
    "/imprint", "/imprint/",
    "/legal-notice", "/legal-notice/",
    "/legal", "/legal/",
    "/kontakt", "/kontakt/",
    "/contact", "/contact/",
    "/contact-us", "/contact-us/",
    "/de/impressum", "/de/kontakt",
    "/en/impressum", "/en/contact",
    "/about/contact",
]

# href / text keywords that identify a contact or impressum page.
PAGE_KEYWORDS = re.compile(
    r"impressum|imprint|legal[-_]?notice|\blegal\b|kontakt|contact|contact[-_]?us",
    re.IGNORECASE,
)

EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")

# Obfuscated forms used by many German sites: info [at] domain . de, info[at]domain.de
AT_RE = re.compile(r"\s*\[\s*at\s*\]\s*|\s*\(\s*at\s*\)\s*|\s+at\s+", re.IGNORECASE)
DOT_RE = re.compile(r"\s*\[\s*dot\s*\]\s*|\s*\(\s*dot\s*\)\s*|\s+dot\s+", re.IGNORECASE)

JUNK_EMAIL_PATTERNS = [
    re.compile(r"\.(png|jpe?g|gif|webp|svg|ico|css|js|woff2?)$", re.IGNORECASE),
    re.compile(r"(example|yourdomain|sentry|sentry\.io|wixpress|godaddy|w3\.org|schema\.org|domain\.tld|email\.com|your-email|placeholder|someone@|noreply@no|@undefined|test@)", re.IGNORECASE),
    re.compile(r"@(example|localhost|test)\.", re.IGNORECASE),
    re.compile(r"^\d+@"),          # pure-numeric local parts are almost never business emails
    re.compile(r"[^@\s]+@\d"),      # TLD starting with a digit
    re.compile(r"^\.|\.$|\.\.|@\.|\.@"),  # malformed
]

JUNK_LOCAL = re.compile(r"^(team@example|email@|your@|user@|name@)", re.IGNORECASE)

# Placeholder / obviously-not-a-person patterns seen in contact-form demos.
PLACEHOLDER_PATTERNS = [
    re.compile(r"(mustermann|muster|beispiel|example|platzhalter|placeholder|yourname|your-email|someone|nobody|dummy)", re.IGNORECASE),
    re.compile(r"^(user|email|name|test|demo)@", re.IGNORECASE),
]

# Real page-type hint (best-effort, for reporting).
TYPE_IMPRESSUM = re.compile(r"impressum|imprint|legal", re.IGNORECASE)
TYPE_CONTACT = re.compile(r"kontakt|contact", re.IGNORECASE)


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def log(msg: str) -> None:
    print(msg, flush=True)


DOMAIN_RE = re.compile(r"^[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?(?:\.[a-z0-9-]{2,24})*\.[a-z]{2,24}$")

# File-extension-like TLDs that are not registered domains.
JUNK_TLD = re.compile(r"\.(?:py|pyw|md|csv|txt|json|ya?ml|xml|html?|css|js|ts|pdf|docx?|xlsx?|zip|png|jpg|svg)$", re.IGNORECASE)

EMAIL_IN_TEXT = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
URL_IN_TEXT = re.compile(r"https?://([^\s\"'<>|]+)", re.IGNORECASE)
COMPANY_SITE_PATH = re.compile(
    r"kontakt|contact|impressum|imprint|ueber|unternehmen|karriere|firmenportrait|info",
    re.IGNORECASE,
)
# Third-party registry / social hosts that are never the company's own domain.
THIRD_PARTY_HOSTS = {
    "linkedin.com", "xing.com", "moneyhouse.ch", "online-handelsregister.de",
    "bibb.de", "evi.gv.at", "asscompact.at", "shab.ch", "registercheck.de",
    "reutlingen.ihk.de", "wer-zu-wem.de", "viaductus.de", "firmen.wko.at",
    "firmenbuch.ai", "teletrust.de", "news-blast.com", "wko.at",
    "handelskammer-d-ch.ch", "thebrokernews.ch", "intercom.io", "hubspot.com",
    "zendesk.com", "google.com", "facebook.com",
}


def _host_of(url: str) -> str:
    host = (urlparse(url).netloc or "").lower().split(":")[0]
    return host.removeprefix("www.").rstrip(".")


def parse_domains_from_contacts_v1(text: str) -> list[str]:
    """Extract one primary prospect domain per company section.

    Contacts-v1 groups companies under '### ' headers inside '## ' sections
    (the enrichment tables use '## ' with table rows only - those are skipped).
    Each company block's emails and source URLs are scanned; the company's own
    contact/impressum site wins, otherwise the most frequent email domain.
    """
    domains: list[str] = []
    for section in re.split(r"(?m)^## ", text)[1:]:
        if "### " not in section:
            continue
        for block in re.split(r"(?m)^### ", section)[1:]:
            emails = [m.group(0).lower() for m in EMAIL_IN_TEXT.finditer(block)]
            urls = [m.group(0).lower() for m in URL_IN_TEXT.finditer(block)]

            site_domains: list[str] = []
            for u in urls:
                host = _host_of(u)
                if host in THIRD_PARTY_HOSTS:
                    continue
                path = urlparse(u).path.lower()
                if COMPANY_SITE_PATH.search(path) and host not in site_domains:
                    site_domains.append(host)

            primary: str | None = None
            if site_domains:
                primary = site_domains[0]
            else:
                counts = Counter(e.rsplit("@", 1)[-1] for e in emails)
                if counts:
                    primary = counts.most_common(1)[0][0]

            if primary and DOMAIN_RE.match(primary) and not JUNK_TLD.search(primary):
                domains.append(primary)

    seen: set[str] = set()
    unique: list[str] = []
    for d in domains:
        if d not in seen:
            seen.add(d)
            unique.append(d)
    return unique


def parse_domains_from_csv(path: Path) -> list[str]:
    """Read the website column from leads.csv (or any csv with website/url)."""
    domains: list[str] = []
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            return domains
        for rec in reader:
            raw = (rec.get("website") or rec.get("url") or rec.get("domain") or "").strip()
            if not raw:
                continue
            if "://" not in raw:
                raw = "https://" + raw
            host = _host_of(raw)
            if host and DOMAIN_RE.match(host) and not JUNK_TLD.search(host) and host not in domains:
                domains.append(host)
    return domains


def parse_domains(md_path: Path) -> list[str]:
    """Extract prospect domains from the source file.

    * .csv          -> website column of leads.csv
    * .md           -> per-company '### ' sections of contacts-v1.md
    """
    text = md_path.read_text(encoding="utf-8", errors="replace")
    return parse_domains_from_csv(md_path) if md_path.suffix.lower() == ".csv" else parse_domains_from_contacts_v1(text)


def fetch(session: requests.Session, url: str) -> tuple[str, str] | None:
    """GET a URL, return (body_text, final_url) or None on failure."""
    try:
        resp = session.get(
            url,
            headers={"User-Agent": UA, "Accept-Language": "de-DE,de;q=0.9,en;q=0.8"},
            timeout=TIMEOUT,
            allow_redirects=True,
        )
        resp.raise_for_status()
        if len(resp.content) > MAX_PAGE_BYTES:
            return None
        ct = (resp.headers.get("Content-Type") or "").lower()
        if "html" not in ct and "text" not in ct:
            return None
        return resp.text, resp.url
    except Exception as exc:  # noqa: BLE001 - crawl failures are per-URL, not fatal
        log(f"    ! fetch failed {url}: {type(exc).__name__}: {exc}")
        return None


def is_same_host(url: str, host_key: str) -> bool:
    host = (urlparse(url).netloc or "").lower().split(":")[0]
    host = host.removeprefix("www.")
    return host == host_key or host.endswith("." + host_key)


def discover_page_urls(home_html: str, homepage_url: str, host_key: str) -> list[tuple[str, str]]:
    """Return (url, page_type) candidates for contact/impressum pages.

    ``host_key`` is the final (post-redirect) host of the homepage, used both
    to validate links and to build the common-path fallbacks.
    """
    found: list[tuple[str, str]] = []

    for href in re.findall(r'href\s*=\s*["\']([^"\']+)["\']', home_html, re.IGNORECASE):
        if href.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        path = urlparse(href).path.lower()
        if PAGE_KEYWORDS.search(path):
            url = urljoin(homepage_url, href)
            if is_same_host(url, host_key) and url not in [u for u, _ in found]:
                found.append((url, classify_type(url)))

    # Common paths as fallback if the homepage gave nothing useful.
    for path in COMMON_PATHS:
        url = f"https://{host_key}{path}"
        if url not in [u for u, _ in found]:
            found.append((url, classify_type(url)))

    return found[:MAX_PAGES_PER_DOMAIN]


def classify_type(url: str) -> str:
    path = urlparse(url).path.lower()
    if TYPE_IMPRESSUM.search(path):
        return "impressum"
    if TYPE_CONTACT.search(path):
        return "contact"
    return "other"


def deobfuscate(text: str) -> str:
    text = AT_RE.sub("@", text)
    text = DOT_RE.sub(".", text)
    return text


def extract_emails(text: str) -> list[str]:
    """Extract and clean publicly listed emails from raw HTML text."""
    decoded = html.unescape(text)
    # Strip obvious noise: scripts/styles contain junk emails.
    decoded = re.sub(r"<script\b.*?</script>", " ", decoded, flags=re.DOTALL | re.IGNORECASE)
    decoded = re.sub(r"<style\b.*?</style>", " ", decoded, flags=re.DOTALL | re.IGNORECASE)
    decoded = re.sub(r"<!--.*?-->", " ", decoded, flags=re.DOTALL)

    # Anti-spam trick: emails split by empty tags, e.g.
    #   vienna<span class="d-none"></span>@bindergroesswang<span ...></span>.at
    # Remove empty tag pairs first (no whitespace), then a space-substituted copy
    # of the rest so tag boundaries never merge two adjacent addresses.
    decoded = re.sub(
        r"<(?:[a-z][a-z0-9]*)[^>]*>\s*</(?:[a-z][a-z0-9]*)>", "", decoded,
        flags=re.IGNORECASE,
    )
    no_tags = re.sub(r"<[^>]+>", " ", decoded)

    candidates: list[str] = []
    for chunk in (decoded, no_tags):
        for m in EMAIL_RE.finditer(deobfuscate(chunk)):
            candidates.append(m.group(0))
    # Obfuscated variants where the regex above could not match (spaces inside).
    for m in re.finditer(
        r"([A-Za-z0-9._%+\-]+)\s*(?:\[at\]|\(at\)|\sat\s)\s*([A-Za-z0-9.\-]+\.[A-Za-z]{2,})",
        decoded,
        re.IGNORECASE,
    ):
        candidates.append(f"{m.group(1)}@{m.group(2).replace(' ', '').lower()}")

    cleaned: list[str] = []
    for email in candidates:
        email = email.strip(" .")
        low = email.lower()
        if any(p.search(low) for p in JUNK_EMAIL_PATTERNS):
            continue
        if JUNK_LOCAL.search(low):
            continue
        if len(email) > 254:
            continue
        if not email.isascii():
            continue
        if email not in cleaned:
            cleaned.append(email)

    # Drop placeholder addresses and any whose domain is a www. prefix.
    filtered: list[str] = []
    for email in cleaned:
        low = email.lower()
        if "@www." in low:
            continue
        if any(p.search(low) for p in PLACEHOLDER_PATTERNS):
            continue
        filtered.append(email)

    # Tag-merge junk (e.g. koeln@cbh.de + "Web") creates entries that have a
    # shorter candidate as a prefix - keep only the shortest variant.
    kept: list[str] = []
    for email in filtered:
        low = email.lower()
        if any(c.lower() != low and low.startswith(c.lower()) for c in filtered):
            continue
        kept.append(email)
    return kept[:MAX_EMAILS_PER_PAGE]


def collect_for_domain(session: requests.Session, domain: str) -> list[dict]:
    rows: list[dict] = []
    home = fetch(session, f"https://{domain}")
    if home is None and not domain.startswith("www."):
        # Some sites serve only on the www subdomain (or have an expired
        # apex certificate) - retry there before giving up.
        home = fetch(session, f"https://www.{domain}")
    if home is None:
        log(f"  [{domain}] homepage unreachable - skipped")
        return rows
    home_html, home_final = home
    host_key = (urlparse(home_final).netloc or domain).lower().split(":")[0].removeprefix("www.")

    # Homepage footers often carry a public business email (e.g. asson.de) even
    # when the contact/impressum pages are forms-only - always scan the homepage.
    seen_emails: set[str] = set()
    for email in extract_emails(home_html):
        seen_emails.add(email.lower())
        rows.append({
            "domain": domain,
            "company": "",
            "page_type": "home",
            "page_url": home_final,
            "email": email,
            "found_at": now_utc(),
        })
    if rows:
        log(f"  [{domain}] home      {home_final} -> {len(rows)} email(s)")

    pages: list[tuple[str, str]] = discover_page_urls(home_html, home_final, host_key)
    for page_url, page_type in pages:
        page = fetch(session, page_url)
        if page is None:
            continue
        emails = [e for e in extract_emails(page[0]) if e.lower() not in seen_emails]
        for email in emails:
            seen_emails.add(email.lower())
            rows.append({
                "domain": domain,
                "company": "",
                "page_type": page_type,
                "page_url": page_url,
                "email": email,
                "found_at": now_utc(),
            })
        if emails:
            log(f"  [{domain}] {page_type:9s} {page_url} -> {len(emails)} email(s)")
    return rows


def append_rows(csv_path: Path, rows: list[dict]) -> int:
    """Append rows, skipping any (domain, email) already present. Returns count added."""
    fields = ["domain", "company", "page_type", "page_url", "email", "found_at"]
    existing: set[tuple[str, str]] = set()
    if csv_path.exists():
        with csv_path.open("r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames:
                for rec in reader:
                    if rec.get("domain") and rec.get("email"):
                        existing.add((rec["domain"].lower(), rec["email"].lower()))

    new_rows = [r for r in rows if (r["domain"].lower(), r["email"].lower()) not in existing]
    if not new_rows:
        return 0

    file_is_new = not csv_path.exists()
    with csv_path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        if file_is_new:
            writer.writeheader()
        writer.writerows(new_rows)
    return len(new_rows)


def coverage_check(args) -> int:
    """Report source domains that lack rows in raw-contacts.csv. No crawling."""
    domains = parse_domains(args.md)
    rows = list(csv.DictReader(open(args.csv, encoding="utf-8", newline="")))
    from collections import Counter as _Counter
    cnt = _Counter(r.get("domain") or "" for r in rows if r.get("domain"))
    missing = [d for d in domains if cnt.get(d, 0) == 0]

    log(f"Coverage check — source: {args.md}")
    log(f"  Source domains parsed : {len(domains)}")
    log(f"  raw-contacts.csv rows : {len(rows)}")
    log(f"  raw-contacts domains  : {len(cnt)}")
    log(f"  Domains with 0 rows   : {len(missing)}")
    for d in missing:
        log(f"    - {d}")
    log("")
    for d in missing:
        if d == "wekal.de":
            log(f"  {d}: present in source but never crawled -> run discovery.py --only {d}")
        if d in {"orbit.de", "asson.de"}:
            log(f"  {d}: present in source; prior crawl returned 0 (masked/form-only) - expected")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--md", type=Path, default=Path("leads/leads.csv"))
    parser.add_argument("--csv", type=Path, default=Path("leads/raw-contacts.csv"))
    parser.add_argument("--only", type=str, default="",
                        help="comma-separated domain filter, e.g. --only netcup.de,swu.de")
    parser.add_argument("--coverage", action="store_true",
                        help="only report domains missing from the CSV, do not crawl")
    args = parser.parse_args()

    if not args.md.exists():
        log(f"ERROR: input file not found: {args.md}")
        return 1

    if args.coverage:
        return coverage_check(args)

    domains = parse_domains(args.md)
    if not domains:
        log(f"ERROR: no domains parsed from {args.md}")
        return 1
    if args.only:
        only = {d.strip().lower().removeprefix("www.") for d in args.only.split(",") if d.strip()}
        domains = [d for d in domains if d in only]
        if not domains:
            log("ERROR: --only matched no known domains")
            return 1
    log(f"Domains to crawl ({len(domains)}): {', '.join(domains)}\n")

    session = requests.Session()
    session.headers["User-Agent"] = UA
    per_domain: dict[str, int] = {}
    total_appended = 0

    for domain in domains:
        rows = collect_for_domain(session, domain)
        added = append_rows(args.csv, rows)
        per_domain[domain] = added
        total_appended += added
        if rows:
            log(f"  [{domain}] appended {added}/{len(rows)} new email row(s)")

    log("\n--- Summary ---")
    for domain, count in per_domain.items():
        log(f"  {domain:16s} {count} new row(s) appended")
    log(f"\nTotal rows appended to {args.csv}: {total_appended}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
