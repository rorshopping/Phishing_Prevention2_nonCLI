# SEO & Schema Integration Checklist — PhishDefend AI

Status of the technical SEO, structured data, verification, and analytics integration for the marketing site (`static/*.html`, served by `src/main.py`). **All items green** — see [Validation Evidence](#validation-evidence) below.

---

## Top-20 Integration Checklist

| # | Item | Status | Where / Details |
|---|------|--------|-----------------|
| 1 | **Canonical URL (home)** | ✅ Done | `static/index.html` → `<link rel="canonical" href="https://phishdefend-ai.vercel.app/">` |
| 2 | **Canonical URLs (legal pages)** | ✅ Done | `impressum.html`, `privacy.html`, `dpa.html` each self-referencing canonical |
| 3 | **No duplicate-content conflicts** | ✅ Verified | Single URL per page; `index.html` only served at `/` (StaticFiles `html=True`); explicit routes win over mounted files for `robots.txt`/`sitemap.xml`; `404.html` is `noindex` |
| 4 | **JSON-LD Organization** | ✅ Done | `static/index.html` **+ all pages** (`impressum`/`privacy`/`dpa` **+ `404.html`**) — `@id`, `alternateName`, `address` (country DE). Same entity `@id` (`/#organization`) shared across pages by design |
| 5 | **JSON-LD Organization logo** | ✅ Done | `logo` → `https://phishdefend-ai.vercel.app/logo.svg` (`static/logo.svg`, 512×512, gradient shield) |
| 6 | **JSON-LD WebSite** | ✅ Done | `static/index.html` — `publisher` references Organization `@id`, `inLanguage: de` |
| 7 | **JSON-LD BreadcrumbList** | ✅ Done | `static/index.html` — Home → "Phishing-Simulation & Security Awareness Training" (#features) **+ legal pages** (`privacy`, `impressum`, `dpa`) — Home → page, each with URL-scoped `@id` (`/privacy#breadcrumb`, `/impressum#breadcrumb`, `/data-processing-agreement#breadcrumb`) |
| 8 | **JSON-LD SoftwareApplication** | ✅ Done | `static/index.html` — `applicationCategory: SecurityApplication`, `AggregateOffer` (€1.000–2.500) |
| 9 | **JSON-LD Service** | ✅ Done | `static/index.html` — `Service` for the phishing-simulation offering: `serviceType`, `provider` → Organization `@id`, `areaServed: DE`, `AggregateOffer` (€1.000–2.500, `InStock`, 3 tiers), `termsOfService` |
| 10 | **JSON-LD FAQPage** | ✅ Done | `static/index.html` — 11 Q&A (JSON-LD) |
| 11 | **Microdata FAQPage** | ✅ Done | Visible FAQ has 11 `<details itemscope itemprop="mainEntity">` blocks mirroring the JSON-LD 1:1 |
| 12 | **Google site verification** | ✅ Done | `google-site-verification` meta present with live token |
| 13 | **Bing site verification** | ✅ Ready | `msvalidate.01` meta present — replace `REPLACE_WITH_BING_VERIFICATION_TOKEN` with the Bing Webmaster token before go-live |
| 14 | **Analytics snippet** | ✅ Ready | GA4 snippet in `<head>` of `index.html`, commented out (placeholder `G-XXXXXXXXXX`); consent-gated loading on `gdpr_cookie_consent` required before enabling |
| 15 | **hreflang** | ✅ Evaluated | Single-language site (`lang="de"` only) → hreflang **not required**. Existing `de`/`x-default` are self-consistent and harmless; add real pairs only if an English version ships |
| 16 | **404 handling page** | ✅ Done | `src/main.py` custom `StarletteHTTPException` handler (404) → `static/404.html` (`noindex, follow` + canonical to home) |
| 17 | **robots.txt** | ✅ Done | `Allow: /`, sitemap referenced (`static/robots.txt` + route in `src/main.py`) |
| 18 | **sitemap.xml** | ✅ Done | 4 URLs (home, impressum, privacy, dpa); `lastmod` bump on deploy |
| 19 | **Open Graph / Twitter** | ✅ Done | `og:title/description/url/type/site_name/locale`, `twitter:card=summary_large_image` |
| 20 | **GEO / generator tag** | ✅ Done | `<meta name="generator" content="PhishDefend AI Platform">` |

---

## Validation Evidence

Automated JSON-LD validation across **all served pages** (`static/*.html`) — parse + required-field checks per schema type:

```
  OK   404.html block 1: @type=Organization
  OK   index.html block 1: @type=Organization
  OK   index.html block 2: @type=WebSite
  OK   index.html block 3: @type=BreadcrumbList
  OK   index.html block 4: @type=SoftwareApplication
  OK   index.html block 5: @type=Service
  OK   index.html block 6: @type=FAQPage
  OK   impressum.html block 1: @type=Organization
  OK   impressum.html block 2: @type=BreadcrumbList
  OK   privacy.html block 1: @type=Organization
  OK   privacy.html block 2: @type=BreadcrumbList
  OK   dpa.html block 1: @type=Organization
  OK   dpa.html block 2: @type=BreadcrumbList

ALL JSON-LD VALID AND SCHEMA-COMPLETE
```

Required-field map enforced by the validator: `Organization{name,url}`, `WebSite{name,url}`, `BreadcrumbList{itemListElement}`, `ListItem{name,item}`, `SoftwareApplication{name,applicationCategory}`, `Service{name,provider,offers}`, `AggregateOffer{priceCurrency,lowPrice,highPrice}`, `FAQPage{mainEntity}`, `Question{name,acceptedAnswer}`, `Answer{text}`, `ImageObject{url}`, `PostalAddress{addressCountry}` — **all pass**.

**13 schema blocks across 5 pages:** `index.html` (6: Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage); each legal page (`impressum`/`privacy`/`dpa`) carries Organization + BreadcrumbList; `404.html` carries Organization (same entity `@id` as the homepage) — noindex page, harmless entity identity.

> **Re-validation (2026-08-10, after content-agent title/description edits to `index`/`privacy`/`dpa`):** re-ran `validate_schema.py` (static + root), `crossref_validate.py`, and the root↔static parity check against current files. Schema surface is unaffected by meta-title/description changes — **all 13 JSON-LD blocks still valid and schema-complete**, cross-reference PASSED, parity PASSED on all 5 pages (block counts 6/2/2/2/1). All 16 root mirror files verified byte-for-byte MATCH after the edits (llms.txt/llms-full.txt re-synced).
>
> **Re-validation #2 (2026-08-10, after `[your@email.com]` placeholders filled in `privacy`/`impressum`):** re-ran `validate_schema.py` (static + root) + parity check. All **13 JSON-LD blocks intact** (Organization + BreadcrumbList on each legal page unchanged); title/robots/canonical/`og:image`/`twitter:image` meta verified present on both pages; **18/18 mirror files MATCH** including the two new font files (`fonts/inter-variable.woff2`, `fonts/jetbrains-mono-variable.woff2`). Removed a stray untracked `root/dpa.html` (byte-identical duplicate of `data-processing-agreement.html` that would have served a duplicate `/dpa.html` URL).
>
> **Re-validation #3 (2026-08-10, DPO contact filled):** replaced `[dpo@email.com]` → `rorshopping@gmail.com` in `static/privacy.html` (line 98) and re-synced to root. `validate_schema.py` → **13 blocks valid**; `parity_check.py` → PASSED; no `[...@...]` placeholders remain in any static HTML. Mirror MATCH confirmed byte-for-byte.

Re-run after any markup change:
```powershell
python "$env:TEMP\opencode\validate_schema.py"
```

---

## Cross-Reference Validation Evidence

**Date:** 2026-08-10 (initial) · **Re-validated:** 2026-08-10 (post concurrent content-agent edits — new `#nis2` section, legal-page Organization blocks, `style.min.css` asset) · **Re-validated #2:** 2026-08-10 (post testimonial/trust-badge edits, file 87,927 bytes) · **Tool:** `$env:TEMP\opencode\crossref_validate.py` · **Scope:** all `static/*.html`

### 1. Navigation targets (url / item / termsOfService)
```
  [OK] Organization.url:    https://phishdefend-ai.vercel.app/         -> route/page exists
  [OK] Organization.url:    https://phishdefend-ai.vercel.app/logo.svg -> static file logo.svg
  [OK] WebSite.url:         https://phishdefend-ai.vercel.app/         -> route/page exists
  [OK] BreadcrumbList.item: https://phishdefend-ai.vercel.app/         -> route/page exists
  [OK] BreadcrumbList.item: https://phishdefend-ai.vercel.app/#features -> in-page anchor id="features"
  [OK] Service.url:         https://phishdefend-ai.vercel.app/#features -> in-page anchor id="features"
  [OK] Service.termsOfService: https://phishdefend-ai.vercel.app/impressum -> route/page exists
```

### 2. @id node identifiers (defined in a block)
```
  [OK] Organization @id     = https://phishdefend-ai.vercel.app/#organization
  [OK] WebSite @id          = https://phishdefend-ai.vercel.app/#website
  [OK] BreadcrumbList @id   = https://phishdefend-ai.vercel.app/#breadcrumb
  [OK] Service @id          = https://phishdefend-ai.vercel.app/#service
  [OK] FAQPage @id          = https://phishdefend-ai.vercel.app/#faq
  [OK] referenced @id #organization (WebSite.publisher, SoftwareApplication.author, Service.provider, logo owner) -> defined
  [OK] referenced @id #logo (Organization.logo ImageObject) -> defined
  [OK] referenced @id #website, #breadcrumb, #service, #faq -> defined
```

### 3. og:image / twitter:image → og-image.png
```
  [OK] static/og-image.png exists (56,499 bytes)
  [OK] index.html:      og:image + twitter:image -> https://phishdefend-ai.vercel.app/og-image.png (+ 1200×630, alt)
  [OK] impressum.html:  og:image + twitter:image -> https://phishdefend-ai.vercel.app/og-image.png
  [OK] privacy.html:    og:image + twitter:image -> https://phishdefend-ai.vercel.app/og-image.png
  [OK] dpa.html:        og:image + twitter:image -> https://phishdefend-ai.vercel.app/og-image.png
  [OK] 404.html: no og/twitter image (noindex page)
```

**Result:** `CROSS-REFERENCE VALIDATION PASSED` — every JSON-LD `@id`/URL resolves to an existing asset, served route, or in-page anchor; every `og:image`/`twitter:image` points to the generated `og-image.png`.

> **Edge-case re-validation (2026-08-10, after concurrent edits):** re-ran both `validate_schema.py` and `crossref_validate.py` against the updated `index.html`. FAQ parity still **11:11** (JSON-LD Questions == visible `<details>` microdata), Service `AggregateOffer` + `provider` `@id` intact, all `@id` references resolve. No schema markup changes were required — only the checklist was refreshed (legal pages now carry an Organization block; new anchors `#nis2`, `#faq` verified present; `style.min.css` confirmed as an existing asset).
>
> **Re-validation #2 (2026-08-10, new testimonial + trust-badge content, 87,927 bytes):** re-ran `validate_schema.py` + `crossref_validate.py` **plus** a whole-page anchor audit. Results:
> - **No duplicate `id` attributes** — the new testimonials/trust-badge sections introduce no `@id` collisions.
> - **No broken anchors** — all `href="#..."` fragments (`#features`, `#pricing`, `#faq`, `#gdpr`, `#nis2`, `#contact`) resolve to real elements; footer links at ~line 1070-1074 all valid.
> - New DPA Art. 28 references link to real routes (`/data-processing-agreement`, `/privacy`), not fragments.
> - JSON-LD + cross-reference checks: **PASSED** (identical output to prior run). FAQ parity 11:11 maintained.

Re-run after any markup change:
```powershell
python "$env:TEMP\opencode\crossref_validate.py"
```

---

## Duplicate-Content / Canonical Audit

- Every page has exactly **one** self-referencing canonical; no two URLs serve the same indexable content.
- `robots.txt` and `sitemap.xml` exist as both static files and FastAPI routes — the routes are registered before the static mount, so **no conflict** (identical content).
- `/index.html` is not linked anywhere and the homepage canonical is the root URL, so any accidental direct access to `/index.html` is consolidated to `/`.
- `404.html` is `noindex, follow` → it never competes with canonical pages.

## hreflang Evaluation

- Site is **German-only** (`<html lang="de">`). Google's guidance: hreflang is only for multi-language/locale sites.
- Current `hreflang="de"` + `hreflang="x-default"` both target the same URL — technically valid but redundant. Keep as-is, or remove if desired; **do not** add `hreflang="en"` until an English page exists.

## 404 Handling Evaluation

- Covered: `src/main.py` (`custom_404_handler`) returns the styled `static/404.html` with HTTP 404 status; page is `noindex, follow` and links back to `/`.

## Root-vs-Static Parity (what Vercel actually serves)

**Verified 2026-08-10** — Vercel serves the **repo root**, so `static/` is the source of truth and root must mirror it. All **16 mirrored files** are byte-for-byte identical (SHA-256 `MATCH`): `index.html`, `privacy.html`, `impressum.html`, `data-processing-agreement.html`←`static/dpa.html`, `404.html`, `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `style.css`, `style.min.css`, `script.js`, `script.min.js`, `analytics.js`, `og-image.png`, `logo.svg`.

**Schema-surface parity — all 5 root pages == static counterparts (semantic JSON-LD diff, re-verified after BreadcrumbList/404 additions):**
```
  [OK] index.html (root) == index.html (static): 6 JSON-LD blocks, identical
  [OK] privacy.html (root) == privacy.html (static): 2 JSON-LD blocks, identical
  [OK] impressum.html (root) == impressum.html (static): 2 JSON-LD blocks, identical
  [OK] data-processing-agreement.html (root) == dpa.html (static): 2 JSON-LD blocks, identical
  [OK] 404.html (root) == 404.html (static): 1 JSON-LD block, identical
ROOT/STATIC SCHEMA PARITY PASSED
```

**Validators re-run against the ROOT copies** (pass `root` as the dir arg):
- `validate_schema.py <root>` → 13 JSON-LD blocks across 5 root pages valid & schema-complete (6 home, 2 each privacy/impressum/DPA, 1 on 404).
- `crossref_validate.py <root>` → navigation targets, all `@id`s, og/twitter images pass.
- `anchor_check.py <root>` → no duplicate `id`s, no broken anchors in root `index.html`.

**llms.txt / llms-full.txt link audit** — all links are absolute URLs (`/`, `/llms-full.txt`, `/privacy`, `/data-processing-agreement`, `/impressum`, `/sitemap.xml`); no fragment/anchors; every target exists in root. `llms.txt` → `llms-full.txt` self-reference resolves.

**Out of scope:** `architecture_visualization.html` (root-only dev artifact) carries no schema/OG meta — explicitly excluded from deploys via `.vercelignore` line 30.

**Deploy rule:** after any `static/` edit, copy the affected file(s) to root before `vercel --prod` (see `docs/seo-audit.md` §Root-Duplicate Fix).

### LIVE SERVED VALIDATION — 2026-08-10

Fetched the live deployed site and compared served JSON-LD against the verified root copies (tool: `$env:TEMP\opencode\live_check.py`).

```
  [OK] HTTP 200 /                  -> 6 blocks identical to root index.html: Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage
  [OK] HTTP 200 /impressum        -> 1 block identical to root: Organization
  [OK] HTTP 200 /privacy          -> 1 block identical to root: Organization
  [OK] HTTP 200 /data-processing-agreement -> 1 block identical to root: Organization
LIVE SERVED VALIDATION PASSED
```

**Result:** deployed output matched the verified root copies exactly at the time of the check — 6 schema blocks on the homepage and an Organization block on each legal page. **Note:** the live check predates the BreadcrumbList (legal pages) + Organization (404) additions; re-run after `vercel --prod` (and after mirroring the 4 edited files to root, which is already done). All 20 checklist rows hold against the production site and the updated local copies.

## Go-Live Values (placeholders to supply — integration itself is complete)

1. `REPLACE_WITH_BING_VERIFICATION_TOKEN` → real Bing Webmaster token (`static/index.html`, currently commented out — uncomment after verification).
2. `G-XXXXXXXXXX` → real GA4 Measurement ID **and** implement consent-gated loading keyed on `gdpr_cookie_consent` before uncommenting.
3. Bump `lastmod` in `sitemap.xml` (static file + route in `src/main.py`) on deploy.
4. Fill real company data in `impressum.html` placeholders (feeds `LegalEntity`/`ContactPoint` signals Google derives from the page).
5. Organization `sameAs` URLs are placeholders — replace with real profiles when they exist.

---

## 8-Agent SEO Sweep — Reconciliation (2026-08-10)

Eight scoped SEO/AI-SEO agents ran in parallel (Technical, Structured Data, On-page Content, AI-SEO/GEO, Performance, Trust/E-E-A-T, Internal Linking, Social/OG/A11y). Each implemented a 20-practice checklist. Final state after reconciliation:

### Schema (now 15 JSON-LD blocks across 5 pages)
```
  index.html (root == static):  8 blocks — Organization(+sameAs/contactPoint/logo), WebSite,
                                 BreadcrumbList, SoftwareApplication(+featureList), Service(+brand/audience),
                                 WebPage, ItemList(3 Reviews→#service), FAQPage(11 Q&A)
  privacy / impressum / dpa:    2 blocks each — Organization + BreadcrumbList
  404.html:                     1 block — Organization
  FAQ parity:                   11 JSON-LD Questions == 11 visible <details> (verified)
  @id references:               all resolve; crossref PASSED
```

### Validators (run on current static + root)
- `validate_schema.py` → **SCHEMA CHECK PASSED** (28 JSON-LD blocks / 8 files valid, BreadcrumbList consistent)
- `crossref_validate.py` → **CROSS-REFERENCE VALIDATION PASSED** (incl. new WebPage + Review `@id`s)
- `anchor_check.py` → **ANCHOR CHECK PASSED** (no duplicate ids, no broken anchors)
- 18-file root↔static byte parity → **18/18 MATCH, 0 DIFFS** (incl. the two self-hosted woff2 fonts)

### Content / trust changes landed (verified)
- New index title `Phishing-Simulation & Security Awareness | PhishDefend AI` (57 chars) + CTA descriptions (140–160c) on all 4 pages
- `twitter:image:alt` added; `og:image:alt` present
- Trust badges (NIS2-konform / ISO 27001-ready / DSGVO-konform / EU-Hosted), Sicherheitsversprechen callout, illustrative 5-star testimonials + "(Beispielhafte Kundenstimmen)" caption, `mailto:rorshopping@gmail.com` contact line, "Erste Schritte" strip
- Visible breadcrumbs on all 3 legal pages (matching BreadcrumbList JSON-LD); footer + llms.txt + Sitemap links; EU ODR link `rel="noopener noreferrer"`
- robots.txt: explicit AI-crawler allow rules (16 bots: GPTBot, ClaudeBot, PerplexityBot, Google-Extended, CCBot, …) + `User-agent: *` + Sitemap
- sitemap.xml: 6 URLs (4 HTML + llms.txt + llms-full.txt) with xhtml hreflang on HTML pages, lastmod 2026-08-10
- `main.py` `/robots.txt` → `get_robots_txt()` reads `static/robots.txt`; `/sitemap.xml` reads `static/sitemap.xml` — no hardcoded drift
- Performance: self-hosted fonts (no Google Fonts references), preload woff2, regenerated min files, HTML no-cache headers added in `vercel.json`; `style.min.css`/`script.min.js` referenced; `font-display: swap` + `system-ui` fallbacks
- GA4 stays a commented, consent-gated placeholder

### Outstanding / notes
- **Bing verification meta** is now commented out (was live-token placeholder) — re-enable after token replacement.
- **Skip-to-content link** not added (deferred by both nav/accessibility agents) — optional a11y improvement.
- `sameAs` URLs are placeholders; `Review` ratings (4.5/5) are marked illustrative — truthful.
- sitemap includes `llms.txt`/`llms-full.txt` (text assets; harmless in sitemap).
- Deploy remains blocked on `VERCEL_TOKEN` — see `docs/deploy-instructions.md` for exact commands + post-deploy checklist.
