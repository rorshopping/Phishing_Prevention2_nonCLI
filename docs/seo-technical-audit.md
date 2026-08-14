# SEO Technical Audit — Broken Links & Missing Assets

**Audit date:** 2026-08-10 (refreshed run)
**Scope:** All served HTML (Vercel **root** + `static/` FastAPI copies), plus `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `analytics.js`
**Result:** **0 broken links · 0 missing assets** · orphan `twiml_test.xml` relocated

---

## Deployment context

- **Vercel serves the repo root** (verified live 2026-08-10): `/` → `index.html`,
  `/impressum`, `/privacy`, `/data-processing-agreement`, `/robots.txt`,
  `/sitemap.xml`, `/llms.txt`, `/llms-full.txt`.
- `static/` is the FastAPI-served mirror for local development (`src/main.py`
  mounts it at `/` and serves robots/sitemap/llms from routes). The
  robots/sitemap routes and `src/llms_txt.py` (`get_llms_txt`,
  `get_llms_full_txt`, `get_robots_txt`) all read from `static/` files, so the
  FastAPI routes and Vercel's root serving expose byte-identical content.
- Root and `static/` copies were byte-verified in sync (index.html 1027 lines in both; all **16 mirror files** incl. `llms.txt`/`llms-full.txt` match).

---

## Summary

| Check | Root (Vercel) | static/ (FastAPI) |
|---|---|---|
| `href`/`src` references resolved | ✅ 94 refs, 0 broken | ✅ 94 refs, 0 broken |
| In-page anchors vs `id` attributes | ✅ all resolve | ✅ all resolve |
| `style.min.css` / `script.min.js` | ✅ present | ✅ present |
| `analytics.js` | ✅ present | ✅ present |
| `logo.svg` (JSON-LD Organization logo, 512×512) | ✅ present | ✅ present |
| `og-image.png` (og:image / twitter:image, 1200×630) | ✅ present | ✅ present |
| Favicon | ✅ inline SVG data-URI (self-contained) | ✅ inline SVG data-URI |

---

## Link & asset detail

### Pages (both root and static/ are identical content)
- **index.html** — new sections added since last audit (Phishing-Test, E-Mail-Sicherheit,
  Benchmarks & ROI) all anchor correctly; footer links `/privacy`, `/data-processing-agreement`,
  `/impressum`, anchors `#features #how-it-works #pricing #gdpr #nis2 #faq #contact` resolve.
  Loads `analytics.js` + `script.min.js` (both `defer`) — files present.
- **impressum.html / privacy.html / data-processing-agreement.html** — load `style.min.css`;
  link `/`, `/#features`, `/#pricing`, `/#contact`, and all legal routes. All resolve.
- **404.html** — single link `/`; inline styles only.

### Assets
| Asset | Valid | Used by |
|---|---|---|
| `og-image.png` | ✅ PNG 1200×630 (matches `og:image:width/height`) | og:image + twitter:image on all 4 pages |
| `logo.svg` | ✅ SVG 512×512 (matches JSON-LD width/height) | JSON-LD `Organization.logo` |
| `style.min.css` | ✅ | All 4 content pages |
| `script.min.js` | ✅ (contains nav/cookie/contact-form/consent logic) | index.html |
| `analytics.js` | ✅ consent-gated GA4 loader | index.html |
| `style.css`, `script.js` | ✅ unminified sources | not referenced (sources only) |

---

## robots.txt / sitemap.xml / llms.txt

- **robots.txt**: base rule + 15 AI/LLM crawler allows, `Sitemap:` directive present. OK.
- **sitemap.xml**: 6 `<loc>` URLs — **all verified to map to real files**:

  | URL | File | Status |
  |---|---|---|
  | `/` | `index.html` | ✅ |
  | `/impressum` | `impressum.html` | ✅ |
  | `/privacy` | `privacy.html` | ✅ |
  | `/data-processing-agreement` | `data-processing-agreement.html` | ✅ |
  | `/llms.txt` | `llms.txt` | ✅ |
  | `/llms-full.txt` | `llms-full.txt` | ✅ |

- **llms.txt**: all internal links (homepage, llms-full.txt, privacy, DPA, impressum)
  resolve to existing files. OK.

---

## Placeholder token re-verification

1. **Bing `msvalidate.01`** — ✅ no longer live. Token `REPLACE_WITH_BING_VERIFICATION_TOKEN`
   is commented out (`index.html:10`), same treatment as the GA block.
2. **GA4 `G-XXXXXXXXXX`** — ✅ no longer shipped as an inline script tag. `analytics.js`
   contains `MEASUREMENT_ID = 'G-XXXXXXXXXX'` but **self-guards**: it returns before loading
   gtag.js while the ID is the placeholder, so no tracking requests fire. It only activates
   after (a) a real Measurement ID is set and (b) `gdpr_cookie_consent == 'accepted'`
   (GDPR/ePrivacy consent-gated). Documented, intentional.
3. **⚠️ Legal content placeholders remain visible** on the legal pages (not SEO tags):
   - `impressum.html`: `[Your Company Name]`, `[Street & Number]`, `[your@email.com]`,
     `[+49 XXX XXX XXX]`, `[Amtsgericht City]`, `[HRB XXXXX]`, `[DE XXX XXX XXX]`,
     `[Name of Managing Director]`
   - `privacy.html`: `[Your Company Name]`, `[Street & Number]`, `[your@email.com]`, `[dpo@email.com]`
   - `data-processing-agreement.html`: `[Provider Address]`
   **Action:** these are legally required data — fill in before production launch.
   Not removable without the operator's real company data.

---

## Findings & actions taken

1. **`twiml_test.xml` orphan — RESOLVED.** The unreferenced TwiML test artifact was
   relocated from `static/twiml_test.xml` → `tests/fixtures/twiml_test.xml`. Nothing in
   `src/` references it (grep confirmed), so it can no longer be served publicly at
   `/twiml_test.xml`.
2. **Git tracking gap — RESOLVED (committed).** The previously-untracked deploy-critical
   files are now `git add`ed. **Root cause:** they were never `git add`ed after the
   initial commit (not ignored by `.gitignore` — verified via `git check-ignore`).
   Deployment currently succeeds despite this because the site is published with
   `vercel --prod` CLI, which uploads the local working directory (not just committed
   files) — that is why all assets return 200 live even while untracked.
   **Committed:** `analytics.js`, `llms.txt`, `llms-full.txt`, `logo.svg`, `og-image.png`,
   `style.min.css`, `script.min.js`, `src/llms_txt.py`, `src/services/live_voice.py`,
   `src/utils/g711.py`, `tests/test_llms_txt.py`, `tests/fixtures/twiml_test.xml`, plus
   the `static/` mirrors, and `.vercelignore`.
   **Commit:** `4eb15be` — "fix: track SEO/AI-SEO deploy-critical files - llms.txt,
   llms-full.txt, analytics.js, og-image.png, logo.svg, style.min.css, script.min.js,
   src/llms_txt.py, src/services/live_voice.py, src/utils/g711.py, tests/test_llms_txt.py,
   tests/fixtures/twiml_test.xml, static mirrors, .vercelignore" (18 files, +890).
   **Post-commit verification:** staging index is empty (`git status --porcelain` shows no
   `A/M/R/C` entries); all files confirmed tracked via `git ls-files`. `HEAD = 4eb15be`.
3. **`architecture_visualization.html` — RESOLVED (consistent).** It is tracked in git
   (`git ls-files` confirms) and excluded from the Vercel upload via `.vercelignore:30`.
   Live check: `/architecture_visualization` returns 404, confirming the exclusion is in
   effect. No further action needed.
4. **Deploy/working-tree drift — RESOLVED.** A redeploy (with the fixed `vercel.json`
   cache headers) from the performance agent has brought the live site in sync with the
   working tree. Re-probed on 2026-08-10: **live `index.html` (87,927 bytes) == local
   `index.html` (87,927 bytes)**, sha256 `AF45D640239FD4CD4BE25357519E6FDB7955C0DACEF803FA470E6FED64188E55` on both. No drift remains.
   Cache-header re-verification (live): `style.min.css` & `og-image.png` →
   `Cache-Control: public, max-age=86400`; `robots.txt` & `sitemap.xml` →
   `Cache-Control: public, max-age=3600` — confirming the fixed `vercel.json` is live.
   All deploy-critical assets (`analytics.js`, `llms.txt`, `llms-full.txt`, `logo.svg`,
   `script.min.js`) return 200.
5. **External URLs** (fonts.googleapis.com, fonts.gstatic.com, ec.europa.eu,
   formspree.io) are well-formed official endpoints; reachability not verifiable offline.

---

## Verification method

- Regex scan of every `href`/`src` in every `*.html` in both root and `static/`, resolved
  against on-disk files + registered FastAPI routes → 0 broken.
- Anchor scan: every `href="#…"` matched against `id="…"` in the same document → 0 missing.
- Sitemap/llms link resolution against real files → all OK.
- Binary check: `og-image.png` (PNG, 1200×630), `logo.svg` (SVG, 512×512).
- Placeholder scan across all served `*.html`/`*.js` with comment-awareness.
