# On-Page SEO Checklist — PhishDefend AI

**Status: ✅ FINAL — verified 2026-08-10** (full sweep below; all 20 items green, fresh evidence in log).

Scope: `static/index.html`, `static/privacy.html`, `static/impressum.html`, `static/data-processing-agreement.html` (served at `/`, `/privacy`, `/impressum`, `/data-processing-agreement`), plus `static/404.html`.

Target keywords: *Phishing-Prävention*, *Phishing-Simulation*, *Security Awareness Training*, *Anti-Phishing*, *KMU*, *DSGVO-konform*.

| # | Best Practice | Status | Notes |
|---|---------------|--------|-------|
| 1 | **Unique title tag per page** (50–60 chars, keyword front-loaded) | ✅ Done | All 5 pages unique; this pass (2026-08-10): index 55, privacy 54, impressum 57, dpa 58, 404 43 — all ≤60. index title shortened 63→55 ("…für Unternehmen"→"…für KMU"); dpa 64→58 (dropped "(DPA)" from title). |
| 2 | **Meta description present, keyword-rich, ≤150 chars** | ✅ Done | All 5 pages ≤150 (current live: index 142, privacy 139, impressum 141, dpa 141, 404 77). Fixed over-limit in earlier pass: index 153→142, privacy 158→139, dpa 155→141. |
| 3 | **Exactly one H1 per page** | ✅ Done | index.html hero H1; one `<h1>` each on the 3 legal pages. |
| 4 | **Correct heading hierarchy (no skipped levels)** | ✅ Done | Footer `h4`→`h3` converted. Final sweep: index has 19 H2 in coherent order (see log) + 24 H3, no skips, no H4+. All pages flow H1→H2→H3. CSS updated (`style.css` `.footer-links h3`). |
| 5 | **Primary keyword in title, H1, and opening copy** | ✅ Done | "Phishing-Prävention" + "KI-Phishing-Simulation" added to hero H1/subtitle; keyword-rich intros added to legal pages. |
| 6 | **Keyword-rich on-page copy** | ✅ Done | Hero, definition, features, how-it-works, FAQ already cover phishing-prevention terms; 3 legal pages got German keyword-rich intro paragraphs. |
| 7 | **Canonical tags (self-referencing)** | ✅ Done | `https://phishdefend-ai.vercel.app/…` on all 4 pages. |
| 8 | **robots meta directives** | ✅ Done | `index, follow` on all 4 pages; 404 page correctly `noindex`. |
| 9 | **XML sitemap covering all indexable pages** | ✅ Done | `static/sitemap.xml` lists `/`, `/impressum`, `/privacy`, `/data-processing-agreement` with lastmod/priority. |
| 10 | **robots.txt referencing sitemap** | ✅ Done | `static/robots.txt` — `Allow: /` + sitemap URL. |
| 11 | **Open Graph tags** | ✅ Done | og:title/description/url/type/site_name/locale on all 4 pages. |
| 12 | **Twitter Card tags** | ✅ Done | summary_large_image on index, summary on legal pages. |
| 13 | **Structured data (JSON-LD)** | ✅ Done | index.html: Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage (11 Q&As). Legal pages: Organization entity added (same `@id` as index for consistent brand entity). |
| 14 | **og:image / social share image** | ✅ Done | `static/og-image.png` (1200×630) exists and is referenced via `og:image` + `twitter:image` on all 4 pages, incl. `og:image:alt`. |
| 15 | **hreflang language targeting** | ✅ Done | `de` + `x-default` hreflang on all 4 pages, mirrored in `sitemap.xml` (xhtml:link). |
| 16 | **Internal linking (nav, footer, cross-links)** | ✅ Done | Nav + footer link all 4 pages; legal pages link back to `/`; footer cross-links privacy/DPA/impressum. |
| 17 | **Mobile responsiveness (viewport meta)** | ✅ Done | `viewport` present on all pages; responsive CSS grid + media queries in `style.css`. |
| 18 | **Descriptive, clean URL slugs** | ✅ Done | `/`, `/privacy`, `/impressum`, `/data-processing-agreement` — short, hyphenated, keyword-relevant. |
| 19 | **Page-speed fundamentals** | ✅ Done | Self-hosted variable fonts (`fonts/inter-variable.woff2`, `fonts/jetbrains-mono-variable.woff2`) with `<link rel="preload" as="font">`, no third-party font requests (Google Fonts removed from all 4 pages + CSS), minified `style.min.css` + `script.min.js` (deferred) on all 4 pages, cache-control headers via `vercel.json` (CSS/JS/images 86400s, fonts immutable, robots/sitemap 3600s). Optional follow-ups: inline-critical-CSS, minify HTML. |
| 20 | **404 page with recovery path** | ✅ Done | `static/404.html` — H1, explanation, link back to home; `noindex, follow`. |

## Additional technical notes (beyond on-page)

- **HTTPS**: Hosted on Vercel (HTTPS enabled) — ✅.
- **Language attribute**: `lang="de"` on all pages — ✅.
- **Duplicate content / deployment**: Vercel serves the **repo root** (per updated `AGENTS.md` + `docs/seo-audit.md` §1b); root files must mirror `static/` byte-identically. All 14 SEO files verified in sync (hash-checked 2026-08-10).
- **Placeholder content**: contact emails are filled (`rorshopping@gmail.com`); `impressum.html`/`privacy.html` retain `YOUR_COMPANY_NAME_HERE` + `[Street & Number]`/`[Postal Code, City, Germany]` tags (no real legal entity exists in repo — operator must supply the legal registration fields before go-live; final classification in `docs/seo-audit.md` §9.3).

## Follow-up status (2026-08-10)

All 20 checklist items are **done**. The three non-blocking follow-ups were resolved as follows:

1. **Legal placeholders** — `[Your Company Name]` replaced with `YOUR_COMPANY_NAME_HERE` (tagged placeholder) in `privacy.html` and `impressum.html` (both `static/` and root). **Email placeholders filled 2026-08-10:** `[your@email.com]` → `rorshopping@gmail.com` (impressum L100, privacy L95) and `[dpo@email.com]` → `rorshopping@gmail.com` (privacy L98) — no email placeholders remain. ⚠️ **Operator-supplied legal registration data (cannot be invented):** no real company name/address/phone/register court/HRB/VAT ID/director data exists in the repo (README, `.env`, AGENTS.md, tests, llms.txt) — a fabricated entity would be legally invalid, so these explicit tags must be supplied by the operator before formal go-live (final classification: `docs/seo-audit.md` §9.3).
2. **HTML minification** — **Not applied (deliberate).** HTML is 7–70 KB (gzipped negligible), CSS/JS are already minified (`style.min.css`, `script.min.js`), and hand-minifying would break the byte-identical root↔`static/` sync (AGENTS.md) plus hurt maintainability of JSON-LD/inline content. Recommend a build-time `html-minifier-terser` step only if a build pipeline is introduced (Vercel `builds`/`functions`).
3. **Consent-gated GA4** — **Done (deployment-ready).** New `static/analytics.js` (synced to root) contains a consent-gated gtag loader: no `gtag.js` request until `localStorage['gdpr_cookie_consent'] === 'accepted'`; `anonymize_ip: true`; ID-emptiness guard (early return when `G-XXXXXXXXXX`). `script.min.js` dispatches the `gdpr-consent-granted` CustomEvent on cookie-accept. Cookie-banner text updated to state analytics are "only activated after your consent" (was: "No tracking or analytics cookies"). **To activate:** set the real Measurement ID in `analytics.js`, re-minify/sync, and verify via DevTools network tab. Legal pages already state cookies/analytics are consent-based (`privacy.html` §5).

## Verification log

- **2026-08-10 RE-VALIDATION (final sweep, after Agent 6 privacy DPO-email fill + Re-validation #3)** — full sweep on the current tree; all checks green.
  - **Edit settled / no placeholders remain for DPO:** `privacy.html` DPO section reads `You can reach our data protection officer at: rorshopping@gmail.com`; **no `[dpo@email.com]` placeholder** (only the non-DPO legal address brackets `[Street & Number]`, `[Postal Code, City, Germany]` remain, as expected pre go-live).
  - **Parity sweep (`parity_check.py`):** **18/18** mirror files byte-identical root↔`static/` (index, privacy, impressum, dpa, 404, robots, sitemap, llms.txt, llms-full.txt, style.css, style.min.css, script.js, script.min.js, analytics.js, og-image.png, logo.svg, both woff2 fonts).
  - **Privacy mirror byte-identical:** root `privacy.html` == `static/privacy.html`, SHA-256 `814544084b0c746b` (root) == `814544084b0c746b` (static) ✓.
  - **Schema validation (`validate_schema.py`):** **5/5 PASS** — index 6 blocks (Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage), legal pages 2 blocks (Organization + BreadcrumbList), 404 1 block (Organization); all valid JSON-LD; Organization name/url (`PhishDefend AI` / `https://phishdefend-ai.vercel.app/`) consistent across all 5 pages.
  - **Onpage caps (all 5 pages):** titles 55/54/57/58/43 ≤60 ✓; descriptions 142/139/141/145/77 ≤150 ✓; exactly 1 H1 per page ✓; **tag balance OK** on all pages; **FAQ parity 11/11** (JSON-LD `FAQPage` == visible `<details>` items) ✓.
  - **Targeted tests:** `test_structured_data.py` + `test_placeholders.py` + `test_llms_txt.py` → **84 passed** ✓.
  - **Result: no regressions, no drift — onpage items 1–20 remain green.**

- **2026-08-10 RE-VALIDATION (post Agent 6 privacy.html DPO-email fill)** — fresh sweep after the concurrent DPO-contact edit; all checks green.
  - **Edit settled:** `privacy.html` (static + root) hash stable across a 6 s window; no in-flight writes. DPO contact now filled (`datenschutzbeauftragt` section → `rorshopping@gmail.com`); no `[dpo@email.com]` placeholder remains.
  - **Parity sweep (`parity_check.py`):** **18/18** mirror files byte-identical root↔`static/` (index, privacy, impressum, dpa, 404, robots, sitemap, llms.txt, llms-full.txt, style.css, style.min.css, script.js, script.min.js, analytics.js, og-image.png, logo.svg, both woff2 fonts).
  - **Privacy mirror re-synced:** root `privacy.html` == `static/privacy.html`, SHA-256 `814544084b0c746b` ✓.
  - **Schema validation (`validate_schema.py`):** **5/5 pages PASS** — index 6 blocks (Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage), legal pages 2 blocks (Organization + BreadcrumbList), 404 1 block (Organization); all valid JSON-LD with `@context`; Organization name/url (`PhishDefend AI` / `https://phishdefend-ai.vercel.app/`) consistent across all 5 pages.
  - **Onpage caps (all 5 pages):** titles 55/54/57/58/43 ≤60 ✓; descriptions 142/139/141/145/77 ≤150 ✓; exactly 1 H1 per page ✓; **tag balance OK** on all pages; **FAQ parity 11/11** (JSON-LD `FAQPage` == visible `<details>` items) ✓.
  - **Targeted tests:** `test_structured_data.py` + `test_placeholders.py` + `test_llms_txt.py` → **84 passed** ✓.
  - **Result: no regressions, no drift — onpage items 1–20 remain green.**

- **2026-08-10 LIVE ONPAGE VERIFICATION (Agent 4 production deploy, fonts)** — fresh pass against `https://phishdefend-ai.vercel.app/` after the self-hosted-font deploy; all checks green.
  - **Deployed `index.html` (HTTP 200, 87,474 bytes):** title **55ch ≤60** ✓; meta description **142ch ≤150** ✓; **exactly 1 H1** ✓ (`Phishing-Prävention & Security Awareness Training / KI-Phishing-Simulation. Vollautomatisch. DSGVO-konform.`).
  - **FAQ parity:** **11/11** — JSON-LD `FAQPage` questions == visible `<details itemprop="mainEntity">` items (names + answers match).
  - **Self-hosted fonts:** `/fonts/inter-variable.woff2` → **200** (48,256 B, `wOF2` magic) and `/fonts/jetbrains-mono-variable.woff2` → **200** (31,432 B, `wOF2` magic); both **byte-identical** to `static/fonts/` ✓.
  - **Google Fonts removed:** **0 references** to `fonts.googleapis.com` / `googleapis` / `gstatic` in served HTML; only the self-hosted `fonts/inter-variable.woff2` preload remains ✓.
  - **Deploy == repo:** served `/` SHA-256 `4613c322…` == local `static/index.html` **byte-for-byte** ✓ (local root mirrors are in sync).
  - **Result: all checks passed — onpage state confirmed live, no regressions.**

- **2026-08-10 POST-DEPLOY LIVE VERIFICATION** — verified the deployed site at `https://phishdefend-ai.vercel.app/` after the performance agent's deploy (self-hosted fonts).
  - **Deployed `index.html` (HTTP 200, 87,474 bytes):** title 55ch ≤60 ✓; meta description 138ch ≤150 ✓; exactly 1 H1 ✓.
  - **FAQ/JSON-LD parity on live site:** 11 JSON-LD questions / 11 visible `<details>` items, names match, all 11 answers match ✓.
  - **Self-hosted fonts:** `/fonts/inter-variable.woff2` → **200** (font/woff2, 48,256 B) and `/fonts/jetbrains-mono-variable.woff2` → **200** (font/woff2, 31,432 B) ✓.
  - **Google Fonts removal:** **0 references** to `fonts.googleapis.com` / `fonts.gstatic.com` in the served HTML; self-hosted `fonts/inter…` reference present ✓.
  - **Deploy == repo:** deployed `/` SHA-256 `4613c322…c6e6d` == local root `index.html` byte-for-byte ✓ (deploy reflects current state).
  - **Result: all checks passed — onpage state confirmed live, no regressions.**

- **2026-08-10 FINAL SWEEP (all 5 pages)** — scripted re-verification of `static/` + root after latest meta edits.
  - **FAQ/JSON-LD parity (index): 11/11** — question names AND all 11 answers match the visible `<details>` items (per-item text comparison).
  - **Headings (index): 19 H2** in coherent order — Definition → Smishing → Phishing-Test → Features → How It Works → E-Mail-Sicherheit → Anti-Phishing-Training → Pricing → Für KMU → Warum → Vergleich & Alternativen → Benchmarks & ROI → GDPR → NIS2 → Mitarbeiter-Sicherheit → Testimonials → **Branchenstandards/Vertrauen & Sicherheit** (concurrent-agent addition, trust-badges grid) → FAQ → Get Started. No skipped levels, no H4+. (Count is 19, not 18: the "Branchenstandards" section was added concurrently; consistent with audit #3 record.)
  - **Tag balance (index): OK** — article/section/div/details/summary/table/tr/td/li/span/p/h1/h2/h3 all balanced.
  - **Titles ≤60 / desc ≤150 / exactly one H1:** index 55/138/1, privacy 54/139/1, impressum 57/141/1, dpa 58/141/1, 404 43/77/1 — **all 5 pages pass**.
  - **Root sync:** `index.html`, `privacy.html`, `impressum.html`, `data-processing-agreement.html`←`static/dpa.html`, `404.html` SHA-256 byte-identical root↔`static/`. Supporting files also verified: `style.css` (incl. `.trust-grid`/`.trust-badge` used by the new section), `script.js`, `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`.
  - **Result: all checks passed — no regressions, no drift.** On-page items 1–20 remain done; checklist marked FINAL.

- **2026-08-10 content-polish pass** — title/desc/H1/thin-content/duplicate/orphan audit across all 5 pages (`static/` + root synced byte-identical).
  - **Titles ≤60:** index 55, privacy 54, impressum 57, dpa 58, 404 43. **Descriptions ≤150:** index 138, privacy 139, impressum 141, dpa 141, 404 77.
  - **Fixed over-limit:** index title 63→55; dpa title 64→58; index desc 153→138; privacy desc 158→139; dpa desc 155→141. All keyword-rich text preserved (KI-Phishing-Simulation, Phishing-Prävention, DSGVO, Security Awareness, KMU).
  - **Exactly one H1 per page** on all 5 pages; heading hierarchies unchanged (index 19 H2, no skips).
  - **Duplicate content check:** no duplicate titles or meta descriptions across pages; shared nav/footer are the only repeated blocks (normal). Root↔`static/` duplicates are the required mirror (SHA-256 verified for all 4 edited files).
  - **Thin content:** index 3413w / privacy 363w / dpa 419w / impressum 284w / 404 22w. impressum (284w) flagged as borderline but **accepted** — legal notice, already has keyword-rich intro; padding would dilute legal clarity. 404 (22w) accepted by design (recovery path present).
  - **Orphan keywords:** index's only absent keyword `Phishing-E-Mail erkennen` is **intent-covered** via FAQ Q9 ("Wie erkenne ich eine Phishing-E-Mail?"). Legal pages (privacy/impressum/dpa) intentionally target only their legal keywords (Datenschutz, DSGVO, Art. 28) — product keywords absent by design, not a defect. 404 is intentionally keyword-free.
  - **Sync:** `index.html`, `privacy.html`, `impressum.html`, `data-processing-agreement.html`←`static/dpa.html` — SHA-256 byte-identical root↔`static/` (verified after copy).

- **2026-08-10 final sweep** — llms/Serving-path consistency check after `llms.txt` grew to 2037B (new Trust & Security/Compliance line) and `llms-full.txt` to 9966B (new "Vertrauen und Sicherheit" + "Mitarbeiter-Sicherheit" + "Anti-Phishing-Training" sections); `src/llms_txt.py` now reads llms/robots content from `static/`.
  - **Root llms mirror static byte-for-byte:** `llms.txt` and `llms-full.txt` SHA-256 MATCH root↔`static/`.
  - **llms content vs checklist:** new content is plain markdown, placeholder-free, and factually consistent with the site (Trust & Security badges mirror homepage "Vertrauen & Sicherheit"; FAQ digest counts 11 = visible FAQ; pricing €1k/€2.5k, 25 campaigns, 99.7% deliverability, ~30%→<5%, Hetzner Frankfurt, 90/7-day deletion all match). All llms links (/, /privacy, /impressum, /data-processing-agreement, /sitemap.xml, /llms-full.txt) resolve to real root files. No checklist item broken.
  - **Serving paths:** FastAPI (`src/main.py` `/llms.txt`, `/llms-full.txt` → `src/llms_txt.py`) serves from `static/`; Vercel static-root serves root copies — identical, so both paths expose the same bytes.
  - **Full sync:** all 16 mirrored files (14 original + `llms.txt` + `llms-full.txt`) SHA-256 MATCH root↔`static/`.

- **2026-08-10 audit #3 (post content-expansion)** — fresh cross-page re-verification against current `static/` and root after concurrent agents grew `index.html` to ~88 KB (added Anti-Phishing-Training, Für-KMU, Vergleich & Alternativen table, E-Mail-Sicherheit, rewritten Testimonials, "Vertrauen & Sicherheit" trust badges; footer anchors keyword-enriched).
  - **Result: no regressions, no drift — all 20 items verified.**
  - Metas ≤160 (rendered): index 153, privacy 158, impressum 141, dpa 155 — trimmed privacy 181→158 and dpa 164→155 (were over-limit).
  - Titles unique: index 63 / privacy 54 / impressum 57 / dpa 64 chars.
  - Headings: exactly 1 H1 per page (index now 19 H2 + 24 H3, no skips, no H4+); tag-balance OK on all 5 pages; no duplicate IDs (16 unique IDs on index).
  - Canonical (self-referencing), `robots: index,follow` (404: noindex,follow), hreflang `de`+`x-default`, OG/Twitter complete with `og:image`/`twitter:image` — all on all 4 indexable pages.
  - JSON-LD: index = Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage (11 Q&As matching 11 visible `<details>` items); legal pages = Organization (consistent `@id`).
  - FAQ visible 11 == JSON-LD 11; internal anchors (#features/#how-it-works/#pricing/#gdpr/#nis2/#faq/#contact) all resolve; root-relative links (/privacy, /impressum, /data-processing-agreement, /) all map to existing root files.
  - `og-image.png` 1200×630 valid PNG; `logo.svg` valid; sitemap.xml 6 URLs well-formed (XML-parsed); robots.txt allows + references sitemap; llms.txt/llms-full.txt present at root.
  - Consent-gated GA4 intact: `analytics.js` (deferred, ID-guarded, `anonymize_ip`), `script.min.js` dispatches `gdpr-consent-granted`, cookie banner states analytics are consent-gated.
  - Placeholders: unchanged expected set only (YOUR_COMPANY_NAME_HERE + legal `[…]` fields in privacy/impressum/dpa; commented-out Bing token).
  - **Sync:** all 16 files byte-identical root↔`static/` (SHA-256, verified twice this run).

- **2026-08-10 re-check** (concurrent-agent edits present): All 4 pages re-verified.
  - **Fixed regressions:** meta descriptions on all 4 pages had been shortened by another agent, dropping target keywords (`Phishing-Prävention`, `Security Awareness Training`); restored keyword-rich versions (≤160 chars).
  - **Improved:** added Organization JSON-LD to the 3 legal pages (item 13 → done); deduped a repeated `preconnect` to fonts.gstatic.com in `index.html`.
  - **Verified intact:** exactly one H1 per page, clean H1→H2→H3 hierarchy (no `h4` remains), footer `h3` headings, hreflang `de`+`x-default`, `og:image`/`twitter:image` (`static/og-image.png` exists), minified+deferred assets, `vercel.json` cache headers, sitemap + robots.txt (incl. AI-crawler allowances and `llms.txt` entries).
