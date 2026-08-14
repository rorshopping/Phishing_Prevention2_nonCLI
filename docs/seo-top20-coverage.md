# SEO Top-20 Coverage — Consolidated Meta-Audit

**Meta-audit date:** 2026-08-10
**Scope:** the four top-20 checklists in `docs/` — `seo-onpage-checklist.md`, `seo-performance-checklist.md`, `seo-schema-checklist.md`, `seo-ai-checklist.md` (4 × 20 = 80 claims)
**Method:** re-read each checklist, spot-verified load-bearing claims against the actual served files (`static/` + root mirrors, live site), SHA-256 root↔static parity, and cross-checked doc-to-doc consistency.

---

## Roll-up

| Checklist | Items | Implemented | N/A / inherited | Open | Evidence quality | Gaps found |
|---|---|---|---|---|---|---|
| **On-Page** | 20 | **20** | 0 | 0 | ✅ strong (files + verification logs) | 2 doc-staleness |
| **Performance** | 20 | **15** | 5 (2 N/A, 2 inherited, 1 evaluated) | 0 | ✅ strong (Lighthouse before/after + live cache headers) | none (deviations justified) |
| **Schema** | 20 | **17** | 3 (Ready: Bing, GA4; Evaluated: hreflang) | 0 | ✅ strong (validators + live check) | 4 doc-staleness |
| **AI-SEO** | 20 | **19** | 0 | **1 (item 18)** | ✅ strong (files + regression tests) | 1 real gap + 1 checkbox-markup gap |
| **TOTAL** | **80** | **71** | **8** | **1** | ✅ | 1 real, 7 documentation |

**Verdict:** no checklist reaches a literal *"all 20/20 implemented"* claim for performance (5 items legitimately N/A/inherited/evaluated) and AI-SEO (item 18 open). Schema/on-page claim 20/20 but carry stale details. All implemented items have concrete, re-verifiable evidence.

---

## Per-checklist detail

### 1. On-Page (20/20 ✅)
Verified fresh (2026-08-10): titles 45–60 ch unique per page; meta descriptions 78–148 ch (all ≤160); exactly 1 `<h1>` on all 5 pages; canonical + `hreflang` (de/x-default) on the 4 indexable pages; `og:image`/`twitter:image` on the 4 indexable pages (none on 404); JSON-LD present; sitemap + robots.txt in place.
**Evidence gaps (documentation staleness, not implementation):**
- Row 9 says sitemap "lists `/`, `/impressum`, `/privacy`, `/data-processing-agreement`" → sitemap now has **6 URLs** (added `llms.txt`, `llms-full.txt`).
- §Additional notes says "All 14 SEO files verified in sync" → mirror set is now **16 files** (verification log itself correctly says 16).

### 2. Performance (15 implemented, 5 justified deviations ⚠️)
Verified fresh: `style.min.css`/`script.min.js` minified + deferred; fonts non-blocking (`preload` + `onload` + `noscript`, `display=optional` + metric fallbacks); live `Cache-Control` headers confirmed (`max-age=86400` assets / `3600` robots/sitemap); Lighthouse evidence 0.99 local, 0.86 live, CLS 0, TBT 0 ms.
**The 5 non-"done" rows are legitimate, not gaps:**
- #10 lazy-load → **N/A** (page contains 0 `<img>` tags)
- #15 compression, #17 HTTP/2+TLS → **inherited** from Vercel CDN
- #16 image optimisation → **N/A** (no raster images besides social-only `og-image.png`)
- #19 critical-CSS inline → **evaluated, deliberately not applied** (maintainability + byte-identical sync); documented decision with re-evaluation trigger

### 3. Schema (17 done, 3 ready/evaluated ✅)
Verified fresh: `static/index.html` = 6 JSON-LD blocks (Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage 11 Q&A == 11 visible FAQ); legal pages now carry **2 blocks each** (Organization + BreadcrumbList); `og-image.png` 1200×630 valid; `logo.svg` referenced from Organization.logo.
**Documentation staleness:**
- Item 18: sitemap "4 URLs" → now **6**.
- §Validation Evidence log: legal pages "1 block: Organization" → now **2 blocks** (Organization + BreadcrumbList with `@id` `…/impressum#breadcrumb`, `/privacy#breadcrumb`, `/data-processing-agreement#breadcrumb`).
- Item 13: Bing `msvalidate.01` "meta present" → the meta is now **commented out** (disabled), not present-and-live.
- Item 14: GA4 described as "commented-out snippet in `<head>`" → mechanism is now the consent-gated **`analytics.js`** (deferred, ID-guarded, `anonymize_ip`); the inline commented snippet no longer exists.

### 4. AI-SEO (19 done, 1 open ⚠️)
Verified fresh: `llms.txt` = 2,037 B (≤2 KB spec), `llms-full.txt` = 9,966 B, both placeholder-free; `llms.txt` links to `llms-full.txt`; `robots.txt` = 15 `User-agent` rules (base `*` + 14 AI crawlers); sitemap discloses both llms URLs; `tests/test_llms_txt.py` asserts file existence, `src/main.py` route wiring, sitemap disclosure, root↔static mirroring, and simulates an LLM prompt.
**Gaps:**
- **Real gap — item 18 (partially resolved):** `llms.txt`/`llms-full.txt` are placeholder-free,
  and the `[your@email.com]` placeholders in `impressum.html` + `privacy.html` have been filled
  with the repo-verified operator contact `rorshopping@gmail.com`. Remaining open: legal entity
  data (company name, address, phone, register/HRB, VAT ID, director, DPO) — see the exact
  placeholder table under §Flagged gaps. This is the **sole go-live blocker**.
- **Checkbox-markup gap:** the top-20 checklist items 1–20 are all still written `[ ]` even though the "Current status" section documents 19 as done — the table itself does not reflect the implementation state.

---

## Flagged gaps (summary)

### Implementation gaps — 1 (sole go-live blocker: legal entity data)

**Investigation (2026-08-10):** searched the repo (footer/contact, `src/config.py`,
`.env.example`, `src/api/contact.py`, `script.js`, README, tests, `vercel.json`) for
genuine operator data.

- **Found (genuine, repo-verified):** operator contact email **`rorshopping@gmail.com`** —
  it is the recipient of the contact form (`src/api/contact.py` → `msg["To"]`), the
  Formspree target (`script.js:44`), and the site's public error-message fallback. This
  email has now been **filled into the `[your@email.com]` placeholders** in
  `impressum.html` (Kontakt) and `privacy.html` (Data Controller) — both `static/` and
  root mirrors updated, SHA-256 MATCH.
- **Not found:** any legal company name (only `YOUR_COMPANY_NAME_HERE` tag exists; no
  GmbH/address/register data anywhere — prior audits rejected fabricating an entity),
  street address, postal code/city, phone, register court, HRB number, VAT ID, managing
  director, or appointed DPO. `privacy@phishguard.ai` (in `src/utils/gdpr.py` boilerplate)
  is a code-domain for an unowned/unverified domain (site lives on `*.vercel.app`), so it
  is **not** operator data.

**Remaining placeholders — the sole go-live blocker** (operator must supply real entity
data; cannot be filled from repo evidence):

| File | Line | Field |
|---|---|---|
| `impressum.html` (static + root) | 96 | Company name (`YOUR_COMPANY_NAME_HERE`) |
| `impressum.html` | 94–95 | Street & Number; Postal Code, City, Germany |
| `impressum.html` | 101 | Phone (`[+49 XXX XXX XXX]`) |
| `impressum.html` | 106 | Register court (`[Amtsgericht City]`) |
| `impressum.html` | 107 | Handelsregisternummer (`[HRB XXXXX]`) |
| `impressum.html` | 113 | VAT ID (`[DE XXX XXX XXX]`) |
| `impressum.html` | 118 | Managing director (`[Name of Managing Director]`) |
| `impressum.html` | 123 | Responsible for content (`[Name, Address as above]`) |
| `privacy.html` | 95 | Company name / Street & Number / Postal Code, City (same block as filled email) |
| `privacy.html` | 98 | DPO email (`[dpo@email.com]`) — only if an officer is appointed |
| `data-processing-agreement.html` | 99 | `[Client Company Name, Address]` — **by design** (Controller = each customer) |
| `data-processing-agreement.html` | 100 | Processor address (`[Provider Address]`) |

Same blocker already recorded in `seo-onpage-checklist.md` §Follow-up #1 and
`seo-schema-checklist.md` §Go-Live Values #4.

### Configuration placeholders — 2 (not implementation gaps; await real keys)
- Bing `REPLACE_WITH_BING_VERIFICATION_TOKEN` (commented out; uncomment + set token).
- GA4 `G-XXXXXXXXXX` in `analytics.js` (self-guarding no-op until a real Measurement ID is set — no tracking fires).

### Documentation staleness — 7 (checklists must be refreshed to match the tree)
1. On-Page row 9: sitemap 4 → 6 URLs.
2. On-Page §notes: mirror set 14 → 16 files.
3. Schema item 18: sitemap 4 → 6 URLs.
4. Schema validation log: legal pages 1 → 2 JSON-LD blocks (Organization + BreadcrumbList).
5. Schema item 13: Bing meta wording ("present" → "commented out").
6. Schema item 14: GA4 wording (inline commented snippet → consent-gated `analytics.js`).
7. AI-SEO top-20 checkboxes all `[ ]` despite status narrative showing 19/20 done.

---

## Cross-cutting verification (fresh, 2026-08-10)

- **Root↔static parity:** all **16** mirrored files SHA-256 **MATCH** (incl. `data-processing-agreement.html`↔`static/dpa.html`).
- **Live site:** all assets return 200; cache headers live; JSON-LD served matches root copies; live `index.html` bytes == root `index.html`.
- **Commit:** deploy-critical files committed at `4eb15be`; staging index clean.
- **Sitemap (6 URLs) → real files:** `/`→`index.html`, `/impressum`, `/privacy`, `/data-processing-agreement`, `/llms.txt`, `/llms-full.txt` — all present.
- **LLM surface:** `robots.txt` permissive `*` + 14 AI crawlers allowed; `llms.txt`/`llms-full.txt` served on canonical domain over HTTPS; FAQ digest 11 items matches visible FAQ.

---

## Recommended actions

1. **Before go-live:** fill the remaining legal-entity placeholders listed in §Flagged gaps
   (the sole blocker — contact email already filled with `rorshopping@gmail.com`) and set the
   Bing/GA4 keys.
2. **Docs hygiene (non-blocking):** apply the 7 staleness fixes above to the four checklists so each table matches the current tree (6 sitemap URLs, 16-file mirror set, 2 legal JSON-LD blocks, commented Bing meta, `analytics.js` mechanism, checked AI boxes).
3. Re-run `tests/test_llms_txt.py`, `validate_schema.py`, `crossref_validate.py`, and the anchor/cache-header checks on any future `static/` edit before `vercel --prod`.
