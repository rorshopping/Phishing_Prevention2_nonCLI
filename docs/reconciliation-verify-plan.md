# Post-Reconciliation Verification Plan

**Purpose:** run **after agent 6's implementation wave (subagents A–H) has fully finished** landing edits. Verifies the merged tree against the pre-reconciliation invariants so the next `vercel --prod` deploys a reconciled, regression-free state.
**Date created:** 2026-08-10
**Status:** PREPARED (not yet run — awaiting agent 6 reconciliation completion)
**Rule:** this file is read-only against the existing tree; execute the checks below against the live repo state at run time.

---

## Pre-flight

- [ ] Confirm no agent is mid-write: `git status --short` shows only expected files; optionally re-run once after a 60 s pause and compare.
- [ ] Record `git rev-parse HEAD` and `git diff --stat` so the run can be tied to a known tree.
- [ ] Note the full test expectation baseline (see §7) and the current deployed `index.html` bytes for later live-diff.

---

## 1. 18-file root ↔ `static/` byte parity

Source of truth: `static/`; Vercel serves the repo root (AGENTS.md §Root mirror files — 18 files).

**Files:** `index.html`, `privacy.html`, `impressum.html`, `data-processing-agreement.html`←`static/dpa.html`, `404.html`, `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `style.css`, `style.min.css`, `script.js`, `script.min.js`, `analytics.js`, `og-image.png`, `logo.svg`, `fonts/inter-variable.woff2`, `fonts/jetbrains-mono-variable.woff2`.

**Command:**
```powershell
python "$env:TEMP\opencode\verify_18.py"        # or: foreach pair -> Get-FileHash SHA-256, expect equal
python "$env:TEMP\opencode\sync_check.py"       # fallback byte-compare sweep
```

**Expect:** **ALL 18 MATCH** (SHA-256). Any `DIFF` = agent-6 wave left a file un-synced → re-copy that `static/` file to root **before** deploy.

---

## 2. robots.txt — AI-crawler allow blocks restored

**Command:**
```powershell
Select-String -Path static\robots.txt,robots.txt -Pattern '^User-agent:'
# expect ≥15 lines: User-agent: * + the 14 AI crawler blocks
foreach($ua in 'GPTBot','ClaudeBot','PerplexityBot'){ Select-String -Path static\robots.txt -Pattern "^User-agent: $ua`$" -Context 0,2 }
```

**Expect:**
- `User-agent: *` / `Allow: /` (permissive default — never blocks AI).
- **GPTBot, ClaudeBot, PerplexityBot** each present with an `Allow: /` line directly below.
- Secondary set intact: OAI-SearchBot, ChatGPT-User, anthropic-ai, Claude-Web, Google-Extended, Applebot-Extended, Meta-ExternalAgent, Amazonbot, cohere-ai, CCBot, Bytespider.
- `Sitemap: https://phishdefend-ai.vercel.app/sitemap.xml` present.
- Root copy byte-identical to `static/` (covered by §1).

---

## 3. Sitemap — canonical 4-URL set intact

**Command:**
```powershell
python "$env:TEMP\opencode\live_sitemap_verify.py"   # parses sitemap.xml, resolves every <loc> to a real file
[regex]::Matches((Get-Content sitemap.xml -Raw),'<loc>([^<]+)</loc>').Value
```

**Expect:**
- The **canonical HTML set is present and correct**: `/` (home, `lastmod` fresh), `/impressum`, `/privacy`, `/data-processing-agreement` — each with matching `xhtml:link` hreflang `de`/`x-default`.
- Total `<loc>` count is either **4** (canonical set only) or **6** (canonical set + `/llms.txt` + `/llms-full.txt`) — the 4 canonical HTML URLs must be present regardless; record the observed total.
- XML well-formed (parse via `xml.etree.ElementTree`), every `<loc>` maps to an existing root file.
- `lastmod` reflects the reconciliation date, not a stale pre-reconciliation date.

---

## 4. Schema validation (JSON-LD)

**Command:**
```powershell
python "$env:TEMP\opencode\validate_schema.py"        # static/ (source of truth)
python "$env:TEMP\opencode\validate_schema.py" root   # root copies (what Vercel serves)
python "$env:TEMP\opencode\crossref_validate.py"      # @id / url / item / og-image resolution
```

**Expect:**
- **13 JSON-LD blocks, all valid & schema-complete:** `index.html` 6 (Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage — 11 Q&A == 11 visible FAQ); each legal page 2 (Organization + BreadcrumbList); `404.html` 1 (Organization).
- FAQ parity **11:11** (JSON-LD questions == visible `<details>` microdata).
- Cross-reference PASS: every `@id` defined, `#organization`/`#logo` referenced resolvable, `og:image`/`twitter:image` → `og-image.png` on the 4 indexable pages.

---

## 5. Anchor audit

**Command:**
```powershell
python "$env:TEMP\opencode\anchor_check.py"          # index.html: dup ids + broken in-page anchors
python "$env:TEMP\opencode\link_integrity_verify.py" # all internal hrefs (files + anchors) resolve
```

**Expect:**
- No duplicate `id` attributes; every `href="#…"` resolves to an existing element (`#features`, `#how-it-works`, `#pricing`, `#gdpr`, `#nis2`, `#faq`, `#contact`).
- Every root-relative link (`/`, `/privacy`, `/impressum`, `/data-processing-agreement`) maps to an existing root file/route.
- Run against **both** root and `static/` copies.

---

## 6. src/main.py reads robots.txt / sitemap.xml from disk

**Command:**
```powershell
Select-String -Path src\main.py -Pattern 'robots.txt|sitemap.xml|llms_txt|get_robots|_read_static'
Select-String -Path src\llms_txt.py -Pattern 'read_text|static|robots'
```

**Expect:**
- `/robots.txt` route returns `get_robots_txt()` (from `src/llms_txt.py`, which reads **`static/robots.txt`** from disk — single source of truth).
- `/sitemap.xml` route returns `_read_static("sitemap.xml")` (reads **`static/sitemap.xml`** from disk; no hardcoded/embedded sitemap remains).
- No stale inline `lastmod`/URL strings in the route (routes must not duplicate file content).
- Optional live check: `python "$env:TEMP\opencode\live_http.py"` or uvicorn + `httpx` GET `/robots.txt`, `/sitemap.xml`, `/llms.txt`, `/llms-full.txt` → 200.

---

## 7. Extended pytest suite

**Command:**
```powershell
python -m pytest tests -q --ignore=tests/test_openrouter.py
```

**Expect:**
- **All pass, 0 fail** (baseline was **197 passed** pre-reconciliation; the suite now includes additional modules — `test_structured_data.py`, `test_placeholders.py`, `test_self_hosted_fonts.py`, `test_llms_txt.py` — so expect **≥ 197 passed**).
- Coverage to confirm green: llms presence/size/sitemap-disclosure/root↔static mirroring/served-vs-root identity (test_llms_txt), structured-data 13 blocks + FAQ parity (test_structured_data), placeholder scan (test_placeholders), font files + `@font-face` references (test_self_hosted_fonts), plus the general backend modules.
- `tests/test_openrouter.py` is a **known pre-existing live-network collection failure** (unset `LLM_API_KEY`) — excluded via `--ignore`; not a reconciliation regression.

---

## 8. Final live Lighthouse run

Local baseline (optional, for drift isolation):
```powershell
python -m http.server 8099 --directory static
npx --yes lighthouse "http://localhost:8099/" --chrome-path="C:\Program Files\Google\Chrome\Application\chrome.exe" --chrome-flags="--headless=new --no-sandbox" --only-categories=performance --output=json --output-path=perf.json
```

Production (the number that counts — run **after** the next `vercel --prod`):
```powershell
npx --yes lighthouse "https://phishdefend-ai.vercel.app/" --chrome-path="C:\Program Files\Google\Chrome\Application\chrome.exe" --chrome-flags="--headless=new --no-sandbox" --only-categories=performance --output=json --output-path=perf-live.json
```

**Expect (self-hosted-fonts era, live):**
- Performance score **≥ 0.90** (measured 0.96–1.00 after font self-hosting).
- **LCP ≤ 2.5 s** (measured ~1.3–1.7 s), **CLS ≤ 0.1** (measured 0), **TBT ≤ 200 ms** (measured 0).
- **0 third-party requests** (no Google Fonts; verify `fonts.googleapis.com`/`fonts.gstatic.com` absent from served HTML).
- Cache headers live: `/fonts/*.woff2` → `max-age=31536000, immutable`; assets → `max-age=86400`; `robots.txt`/`sitemap.xml` → `3600`.
- Optional live-diff: `python "$env:TEMP\opencode\compare_live.py"` → deployed `/` bytes == local root `index.html`.

---

## Wrap-up gates

- [ ] All 8 sections PASS; any failure blocks deploy until fixed + re-verified.
- [ ] After any fix edit: re-copy the affected `static/` file(s) to root (18-file rule) and re-run §1, then the specific failed check.
- [ ] Only then run `vercel --prod`, followed by §8 (live Lighthouse) + a live 200 sweep.
- [ ] Update `docs/seo-verification-report.md` (owner: agent 5) and `docs/seo-audit.md` §9 with the reconciliation results and observed sitemap URL count.
