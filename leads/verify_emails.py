import csv
import dns.resolver
import os
import re
import sys
from collections import Counter
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "leads.csv"

GENERIC_ROLES = {
    "info", "contact", "support", "sales", "help", "admin", "office",
    "hello", "webmaster", "postmaster", "noreply", "no-reply", "abuse",
    "careers", "jobs", "hr", "billing", "accounts", "team", "service",
    "enquiries", "enquiry", "marketing", "privacy", "press",
}

REQUIRED_COLUMNS = ["company", "website", "contact_role", "email", "source_url", "status"]

SYNTAX_RE = re.compile(r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$")


def ensure_dir() -> None:
    BASE_DIR.mkdir(parents=True, exist_ok=True)


def read_rows() -> list[dict]:
    if not CSV_PATH.exists() or CSV_PATH.stat().st_size == 0:
        print(f"[info] {CSV_PATH.name} missing or empty - nothing to verify.")
        return []
    with open(CSV_PATH, "r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def local_part(email: str) -> str:
    return email.split("@", 1)[0].lower()


def has_mx(domain: str) -> bool:
    try:
        dns.resolver.resolve(domain, "MX")
        return True
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer, dns.resolver.NoNameservers, dns.exception.Timeout):
        return False


def main() -> None:
    ensure_dir()
    rows = read_rows()
    if not rows:
        print("REPORT: no rows verified.")
        return

    for col in REQUIRED_COLUMNS:
        if col not in rows[0]:
            print(f"[error] CSV missing required column: {col}")
            sys.exit(1)

    emails = [str(r.get("email") or "").strip() for r in rows]
    seen: dict[str, list[int]] = {}
    dup_lines: set[int] = set()
    for i, e in enumerate(emails, start=2):
        key = e.lower()
        seen.setdefault(key, []).append(i)
        if len(seen[key]) > 1:
            dup_lines.update(seen[key])

    syntax_bad: list[str] = []
    mx_bad: list[tuple[str, str]] = []
    generic: list[tuple[int, str]] = []

    domains = {e.split("@", 1)[1] for e in emails if "@" in e}
    mx_ok: dict[str, bool] = {}
    for d in domains:
        mx_ok[d] = has_mx(d)

    for i, e in enumerate(emails, start=2):
        if not e:
            continue
        if not SYNTAX_RE.match(e):
            syntax_bad.append(e)
            continue
        domain = e.split("@", 1)[1]
        if not mx_ok.get(domain, False):
            mx_bad.append((domain, e))
        if local_part(e) in GENERIC_ROLES:
            generic.append((i, e))

    print(f"rows parsed: {len(rows)}")
    print(f"unique emails: {len(seen)}")
    print(f"duplicate lines: {len(dup_lines)}")
    print(f"invalid syntax: {len(syntax_bad)}")
    print(f"no/invalid MX: {len(mx_bad)}")
    print(f"generic-role: {len(generic)}")

    if dup_lines:
        print("\nduplicate occurrences (csv line: email):")
        for line in sorted(dup_lines):
            print(f"  {line}: {emails[line - 2]}")

    if syntax_bad:
        print("\ninvalid syntax:")
        for e in syntax_bad:
            print(f"  {e}")

    if mx_bad:
        print("\nno/invalid MX:")
        for domain, e in mx_bad:
            print(f"  {domain}  ({e})")

    if generic:
        print("\ngeneric-role addresses:")
        for line, e in generic:
            print(f"  {line}: {e}")

    if not (dup_lines or syntax_bad or mx_bad or generic):
        print("\nREPORT: all emails PASS - no issues found.")


if __name__ == "__main__":
    main()
