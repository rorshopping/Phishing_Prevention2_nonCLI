# SEO Performance Checklist — PhishDefend AI (Core Web Vitals)

> Scope: landing page + legal pages (`static/index.html`, `static/privacy.html`, `static/impressum.html`, `static/dpa.html`, `static/404.html`), `static/style.css`, `static/script.js`, serving config (`src/main.py`, `vercel.json`).
> Measurement: **Lighthouse 13.4.1**, mobile, simulated throttling, Chrome headless, local `http://localhost:8099/`.
> Date: 2026-08-10

## Before / After (Core Web Vitals)

| Metric | Before | After (final) | Delta | Target |
|---|---|---|---|---|
| Performance score | 0.89 | **0.99** | +0.10 | ≥ 0.9 |
| First Contentful Paint (FCP) | 3,011 ms | **1,727 ms** | **−1,284 ms (−43%)** | ≤ 1.8 s |
| Largest Contentful Paint (LCP) | 3,011 ms | **1,727 ms** | **−1,284 ms (−43%)** | ≤ 2.5 s |
| Total Blocking Time (TBT) | 0 ms | 0 ms | 0 | ≤ 200 ms |
| Cumulative Layout Shift (CLS) | 0 | 0 | 0 | ≤ 0.1 |
| Speed Index | 3,111 ms | **1,727 ms** | **−1,384 ms (−44%)** | ≤ 3.4 s |
| Time to Interactive | 3,011 ms | **1,727 ms** | −1,284 ms | ≤ 3.8 s |

*Final verified 2026-08-10 (Lighthouse 13.4.1, mobile, simulated throttling) **after** the concurrent NIS2/Smishing/pricing + legal-JSON-LD edits stabilized. Two consecutive runs: FCP/LCP 1,727 ms and 1,771 ms (score 0.99 both) — stable. Earlier post-change runs scored 1.00 at ~1.1–1.2 s while `index.html` was ~9 KB smaller; the growth moved FCP/LCP to ~1.75 s, still well inside green. **These are localhost-baseline numbers.** For the real production path (CDN + throttled network), see §Live production re-check: score 0.86, FCP/LCP ~3.3 s — **then improved to 0.96–1.00 / FCP ~1.3 s / LCP ~1.6 s by self-hosting fonts (§Self-hosted variable fonts).**

The dominant before-cost was the **render-blocking Google Fonts stylesheet** (3 s until first paint). Making it non-blocking plus `font-display: optional` moved FCP/LCP under 1.2 s with CLS still at 0.

## Asset weight (served files)

| Asset | Before (bytes) | After (bytes) | Saving |
|---|---|---|---|
| `style.css` → `style.min.css` | 14,075 | 11,702 | **−2,373 (−17%)** |
| `script.js` → `script.min.js` | 3,760 | 2,370 | **−1,390 (−37%)** |
| Google Fonts CSS | render-blocking request | **removed** (self-hosted) | 0 blocking requests, 0 third-party |
| Fonts (Inter 400–900, JetBrains Mono) | Google CDN CSS + multi-slice fetch (~316 KB transfer) | **2 variable woff2, 79,688 B total** (`inter-variable.woff2` 48,256 B + `jetbrains-mono-variable.woff2` 31,432 B), cached `immutable` | fewer bytes, own CDN, preloaded LCP font |

`index.html` also grew ~20 KB across the session from **concurrent** SEO/content work (Bing meta, JSON-LD, NIS2/Smishing/pricing sections) — unrelated to the performance changes. Verify total page bytes again once that work is fully merged.

## Top-20 Performance Checklist

| # | Item | Status | Impact | Evidence |
|---|---|---|---|---|
| 1 | Eliminate render-blocking Google Fonts stylesheet | ✅ Done (superseded) | FCP −1.9 s | All Google Fonts links removed — fonts are now self-hosted variable woff2 declared in `style.min.css` (§Self-hosted variable fonts) |
| 2 | Self-host fonts + `preload` LCP font | ✅ Done | LCP −1.7 s live | `fonts/inter-variable.woff2` (48 KB, covers 400–900) + `jetbrains-mono-variable.woff2` (31 KB) + `<link rel="preload" as="font">`; zero third-party requests |
| 3 | `font-display: swap` + metric fallbacks | ✅ Done | No FOIT, minimal swap CLS | Local `@font-face` with `font-display: swap`; `Inter Fallback`/`JetBrains Mono Fallback` size-adjust rules keep CLS 0 |
| 4 | Metric-matched fallback fonts (`size-adjust`, `ascent/descent-override`) | ✅ Done | Fallback ≈ web font → no layout jump | `@font-face` "Inter Fallback" (Arial) & "JetBrains Mono Fallback" (Courier New) in `style.css` |
| 5 | Minify CSS | ✅ Done | −2.4 KB, faster parse | `npx clean-css-cli` → `style.min.css` (115 rule blocks preserved) |
| 6 | Minify JS | ✅ Done | −1.4 KB, faster parse | `npx terser -c -m` → `script.min.js` (syntax-checked) |
| 7 | Load JS non-blocking (`defer`) | ✅ Done | No parser-blocking | `<script src="script.min.js" defer>` |
| 8 | Cache-Control for static assets (FastAPI) | ✅ Done | Reuse cache, fewer bytes over network | Middleware in `src/main.py`: css/js/svg/img `max-age=86400`, fonts `immutable`, txt/xml `3600`; verified via Starlette harness |
| 9 | Cache-Control on Vercel edge | ✅ Done (live) | Same policy on production CDN | `vercel.json` `headers` config — **verified live 2026-08-10**: `style.min.css`/`script.min.js`/images → `max-age=86400`, fonts → immutable, `robots.txt`/`sitemap.xml` → `3600`. See §Production deploy |
| 10 | `loading="lazy"` on images | ✅ N/A (verified) | — | **0 `<img>` tags on every served page** (grep 2026-08-10: `404/dpa/impressum/index/privacy` all `img=0`; index has exactly 1 inline `<svg>`); trust badges are emoji. Nothing to lazy-load. Rule enforced going forward: any future `<img>` gets `loading="lazy"` + `decoding="async"` + width/height |
| 11 | LCP element prioritised | ✅ Done | Hero `<h1>` paints with Inter 900 on first frame | LCP font (`inter-variable.woff2`) is `preload`ed; `style.min.css` is the only render-blocking resource. Live LCP 3,280 → **~1.6 s** |
| 12 | CLS: no offscreen shifts | ✅ Done | CLS stays 0 | Cookie banner & toast start `translateY(100%/120px)` offscreen; fixed nav; `fade-in` uses opacity/transform (no layout) |
| 13 | Zero unused CSS / unused JS | ✅ Done | Smaller effective parse | Lighthouse `unused-css-rules` and `unused-javascript` pass (score 1) |
| 14 | Favicon as inline SVG data URI | ✅ Done | No extra request | `<link rel="icon" ... data:image/svg+xml>` |
| 15 | Text compression | ✅ Inherited (verified) | — | **Live `Content-Encoding: br` (Brotli) verified 2026-08-10** on `/`, `style.min.css`, `script.min.js`, `llms.txt`. Vercel edge auto-compresses text; enable gzip/brotli in any self-host proxy |
| 16 | Image optimisation | ✅ N/A (verified) | — | No raster images on the render path (all graphics inline SVG/emoji). `og-image.png` (56 KB, 1200×630) is **social-meta only** (`og:image`/`twitter:image`); not fetched during page render, and social platforms require PNG/JPG (WebP/AVIF not applicable). Rule for future: serve WebP/AVIF with proper width/height on any render `<img>` |
| 17 | HTTP/2 + TLS | ✅ Inherited (verified) | — | **Live verified 2026-08-10:** Lighthouse network trace shows `protocol: h2` for all requests; response carries `Strict-Transport-Security: max-age=63072000; includeSubDomains; preload`; TLS 1.3 on Vercel CDN. uvicorn dev server is HTTP/1.1 (fine locally) |
| 18 | Cache legal/SEO text assets | ✅ Done | 1 h cache | `robots.txt`, `sitemap.xml` via middleware + vercel.json |
| 19 | Critical CSS inline | ✅ Rationale (verified) | — | Kept external `style.min.css` — it is the **only** render-blocking resource (`render-blocking-insight`: 3,698 B transferred), served with Brotli + `max-age=86400`; inlining would duplicate CSS across 4 pages for negligible gain. Live LCP is green (~1.5–1.8 s). Revisit only if a 3G budget < 1 s is adopted |
| 20 | Continuous monitoring | ✅ Set up | Guards regressions | Re-run this Lighthouse command after each deploy / on PageSpeed Insights for `https://phishdefend-ai.vercel.app/` |

## Concurrent-edit re-scan (final, 2026-08-10)

Re-scanned **all served pages** after other agents added NIS2/Smishing/pricing sections and legal-page JSON-LD:

- **No new render-blocking resources.** The GA4 gtag block added to `index.html` is **commented out** (`<!-- ... -->`) — nothing is fetched; it stays disabled because the cookie banner promises "no tracking or analytics cookies" (re-enable only with consent-gated loading, GDPR Art. 6(1)(a) + ePrivacy).
- **New legal-page JSON-LD** is `type="application/ld+json"` — inert, never fetched, no paint impact.
- **`og-image.png` (56 KB)** added to `static/` is referenced **only** in `og:image`/`twitter:image` meta tags — social-crawlers only, **not fetched on page render**, so it does not affect CWV. Served via `StaticFiles` and cached by the middleware (`.png` → `max-age=86400`), so it is covered by the cache policy.
- **New NIS2/Smishing/pricing sections** reuse existing `style.min.css` classes + inline styles — no new requests.
- `robots.txt` / `sitemap.xml` grew via concurrent edits; both still cached 1 h.

**Every served page** still references only minified assets:

| Page | CSS | JS | Fonts |
|---|---|---|---|
| `index.html` | `style.min.css` ✅ | `script.min.js defer` ✅ | non-blocking `preload` + `optional` ✅ |
| `privacy.html` | `style.min.css` ✅ | (no JS — none needed) | non-blocking `preload` + `optional` ✅ |
| `impressum.html` | `style.min.css` ✅ | (no JS) | non-blocking `preload` + `optional` ✅ |
| `dpa.html` | `style.min.css` ✅ | (no JS) | non-blocking `preload` + `optional` ✅ |
| `404.html` | inline `<style>` (no external) | (no JS) | system fonts only ✅ |

**Cache-Control coverage** — verified via Starlette harness (same middleware pattern as `src/main.py`) against every asset type any page references:

| Path | Cache-Control |
|---|---|
| `/style.min.css` | `public, max-age=86400` ✅ |
| `/script.min.js` | `public, max-age=86400` ✅ |
| `/logo.svg`, `/og-image.png` | `public, max-age=86400` ✅ |
| `/robots.txt`, `/sitemap.xml` | `public, max-age=3600` ✅ |
| `/404.html`, `/impressum.html`, `/privacy.html`, `/dpa.html`, `/` | no cache header (HTML revalidates) ✅ |
| Google Fonts (external) | Google CDN-managed (immutable woff2) ✅ |

All site-wide assets are CSS, JS, two images (SVG logo + social `og-image.png`), inline data-URI favicon, and external fonts — 100 % covered. Same policy mirrored in `vercel.json` for production.

**Re-measurement** (after concurrent-edit stabilization): performance **0.99**, FCP **1,727 ms**, LCP **1,727 ms**, SI **1,727 ms**, TBT 0 ms, CLS 0 (confirming run: FCP/LCP 1,771 ms).

## Production deploy (2026-08-10)

Deployed to production via `vercel --prod` and verified against `https://phishdefend-ai.vercel.app/`:

| Asset | Status | Cache-Control (live) |
|---|---|---|
| `style.min.css`, `script.min.js`, `style.css`, `script.js`, `analytics.js` | 200 | `public, max-age=86400` ✅ |
| `og-image.png`, `logo.svg` | 200 | `public, max-age=86400` ✅ |
| `robots.txt`, `sitemap.xml` | 200 | `public, max-age=3600` ✅ |
| `/` (HTML) | 200 | `public, max-age=0, must-revalidate` (revalidates) ✅ |

**Bug found & fixed during deploy:** the original `vercel.json` `headers` `source` patterns used `$` anchors, but Vercel's `source` is **path-to-regexp** (full-match is implied; `$`/`^` are treated literally). So the regex rules never matched and all assets served Vercel's default `max-age=0`. Verified with a throwaway `X-Perf-Diag*` header: exact-path rule matched, anchored regex did not. **Removed the `$` anchors** → caching headers now apply in production (verified above). Diagnostic rules removed.

**Deploy hygiene:** added `.vercelignore` excluding `src/`, `tests/`, `*.py`, `gophish/`, `gophish.zip` (33 MB), env/secrets, DBs — upload shrank to ~508 KB; deploy ~5 s. Root mirrors `static/` (16 files incl. `llms.txt`/`llms-full.txt`, byte-for-byte); no HTML/assets were changed during deploy, so root was already in sync.

Note the FastAPI `Cache-Control` middleware in `src/main.py` remains the fallback for anyone running the Python server (e.g. local/render); Vercel serves the repo-root static output and honors `vercel.json` instead, which is what production uses.

## Live production re-check (post-content-growth, 2026-08-10)

`index.html` grew to **87,927 B** on production (trust badges, rewritten testimonials, 4 new content sections). Re-ran Lighthouse 13.4.1 (mobile, simulated throttling) against **the live site** `https://phishdefend-ai.vercel.app/` — two runs, stable:

| Metric | Live run 1 | Live run 2 | vs localhost after (1,727 ms) |
|---|---|---|---|
| Performance score | 0.86 | 0.86 | — |
| First Contentful Paint (FCP) | 3,280 ms | 3,292 ms | +~1.6 s |
| Largest Contentful Paint (LCP) | 3,280 ms | 3,292 ms | +~1.6 s |
| Total Blocking Time (TBT) | 0 ms | 0 ms | 0 |
| Cumulative Layout Shift (CLS) | 0 | 0 | 0 |
| Speed Index | 3,280 ms | 3,292 ms | — |

**Why live differs from localhost:** the live run measures the real path — CDN + TLS + Google Fonts over a throttled mobile network (simulated 4G). Lighthouse's `lcp-breakdown-insight` shows LCP is gated by the `font-display: optional` race: TTFB 51 ms + **element render delay 232 ms** — the hero `<h1>` (Inter 900) waits for the webfont before painting. Under simulated throttling that 232 ms scales to ~3.3 s. CLS stays 0 (metric-matched fallbacks). TBT stays 0.

**Cache headers re-verified on the latest content — all hold:**

| Asset | Live Cache-Control |
|---|---|
| `style.min.css`, `script.min.js`, `style.css`, `script.js`, `analytics.js` | `public, max-age=86400` ✅ |
| `og-image.png`, `logo.svg` | `public, max-age=86400` ✅ |
| `robots.txt`, `sitemap.xml` | `public, max-age=3600` ✅ |
| `/` (HTML) | `public, max-age=0, must-revalidate` ✅ |

**Render-blocking audit of the added content (trust badges etc.):** no new render-blocking resources.
- Trust badges are **emoji** (`&#x1F4C4;`); the whole page contains **0 `<img>` tags and exactly 1 inline `<svg>`** (the hero scroll indicator).
- Scripts: 6 inert `application/ld+json` blocks + `script.min.js defer` + `analytics.js defer`. `analytics.js` (1.1 KB) is a **guarded no-op** — its `MEASUREMENT_ID = 'G-XXXXXXXXXX'` placeholder returns immediately, so it fetches nothing and loads no third-party code.
- Only render-blocking request: `style.min.css` itself (`render-blocking-insight` flags it at 3,526 B transferred — cached, intended).
- No `@import`, no new external stylesheets/fonts, no `loading=`-able images.

**Headline:** performance **0.86 on live production** after content growth — CLS 0, TBT 0 ms (both green); FCP/LCP ~3.3 s (LCP just outside the 2.5 s "good" band under simulated 4G, driven by the optional-font race, not page weight). **Next step was executed — see §Self-hosted variable fonts below.**

## Self-hosted variable fonts (final, 2026-08-10)

The flagged LCP optimization is **implemented and deployed**:

**What changed**
- Downloaded **2 variable-font woff2 files** (Latin slice) locally → `static/fonts/` + root `fonts/`:
  - `inter-variable.woff2` (48,256 B, `wght` axis 100–900 → covers used 400–900)
  - `jetbrains-mono-variable.woff2` (31,432 B, `wght` 400–800 → covers used 400–500)
  - Verified as true variable fonts via `fontTools` (`fvar`/`gvar` present).
- `style.css` now declares the local `@font-face`s (`font-display: swap`, latin `unicode-range`); the metric-matched `Inter Fallback`/`JetBrains Mono Fallback` rules are kept to hold CLS at 0 during any swap. Rebuilt `style.min.css` (12,922 B).
- **Removed all Google Fonts `<link>`s** (preconnect, preload-as-style, noscript) from `index.html` + all 3 legal pages — replaced with a same-origin **preload of the LCP font**: `<link rel="preload" as="font" type="font/woff2" href="/fonts/inter-variable.woff2" crossorigin>`.
- **`style.min.css` is now the only render-blocking resource** — no third-party requests at all.
- Fonts cached **`public, max-age=31536000, immutable`** (verified live).

**Live Lighthouse 13.4.1 (mobile) — self-hosted vs Google Fonts**

| Metric | Google Fonts (live) | Self-hosted run 1 | Self-hosted run 2 |
|---|---|---|---|
| Performance score | 0.86 | **1.00** | **0.96** |
| FCP | 3,280 ms | **1,267 ms** | **1,420 ms** |
| LCP | 3,280 ms | **1,567 ms** | **1,720 ms** |
| TBT | 0 ms | 0 ms | 157 ms (style/layout noise, 569 ms total main-thread) |
| CLS | 0 | 0 | 0 |
| Speed Index | 3,280 ms | **1,267 ms** | **1,420 ms** |
| Third-party requests | Google Fonts (~316 KB) | **0** | **0** |

Network trace (run 1): HTML 0→188 ms; `inter-variable.woff2` **preloaded, starts 194 ms in parallel with CSS**, done 215 ms; `style.min.css` 195→216 ms (only render-blocking); `jetbrains-mono-variable.woff2` lazy via CSS at 307→321 ms. Total requests on the critical path: HTML + CSS + 1 font.

**Result:** LCP **3,280 → ~1.6 s** (−52%), FCP 3,280 → ~1.3 s, performance 0.86 → **0.96–1.00**, CLS still 0, zero third-party requests. All targets green (LCP ≤ 2.5 s, CLS ≤ 0.1, TBT ≤ 200 ms).

## What was changed

- `static/index.html`, `static/privacy.html`, `static/impressum.html`, `static/dpa.html` — Google Fonts now non-blocking (`preload` + `onload` + `<noscript>`), `display=optional`, added `preconnect` to `fonts.gstatic.com`, switched to `style.min.css`.
- `static/index.html` — `script.min.js` loaded with `defer`.
- `static/style.css` — added `@font-face` metric fallbacks for Inter and JetBrains Mono; font stacks now include them.
- `static/style.min.css`, `static/script.min.js` — **new** minified assets (originals kept as source of truth).
- `src/main.py` — `Cache-Control` header middleware for static asset suffixes (HTML left uncached).
- `vercel.json` — production CDN caching headers (fonts `immutable`).
- **Self-hosted fonts (2026-08-10):** `static/fonts/inter-variable.woff2` + `static/fonts/jetbrains-mono-variable.woff2` (+ root `fonts/` mirrors); local `@font-face` in `style.css`/`style.min.css`; removed all Google Fonts links from the 4 HTML pages and replaced with same-origin `preload` of `inter-variable.woff2`; `style.min.css` is now the only render-blocking resource. AGENTS.md mirror list updated (18 files).

## Re-measure command

Local (development baseline):
```powershell
python -m http.server 8099 --directory static
npx --yes lighthouse "http://localhost:8099/" `
  --chrome-path="C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --chrome-flags="--headless=new --no-sandbox" `
  --only-categories=performance --output=json --output-path=perf.json
```

Production (real CDN/network — the number that counts):
```powershell
npx --yes lighthouse "https://phishdefend-ai.vercel.app/" `
  --chrome-path="C:\Program Files\Google\Chrome\Application\chrome.exe" `
  --chrome-flags="--headless=new --no-sandbox" `
  --only-categories=performance --output=json --output-path=perf-live.json
```

## Caveats

- Full FastAPI app currently cannot boot in this environment due to a **pre-existing** `fastapi`/`starlette` version mismatch (`Router.__init__() got an unexpected keyword argument 'on_startup'`) — unrelated to this task. The cache-header middleware was therefore verified with an identical Starlette harness; `python -m py_compile src/main.py` passes.
- `git diff` shows concurrent in-flight SEO content edits to `static/index.html` (meta/JSON-LD) — left untouched.

## Final performance panel (2026-08-10, live)

Closure pass: all 20 checklist rows are now **Done, N/A, or Inherited — each with verified evidence** (grep for `<img>`, live Brotli headers, HTTP/2 + HSTS, `render-blocking-insight` byte count). Re-ran Lighthouse 13.4.1 (mobile, simulated throttling) against production `https://phishdefend-ai.vercel.app/`:

| Metric | Final run 1 | Final run 2 | Target | Verdict |
|---|---|---|---|---|
| Performance score | 0.96 | **1.00** | ≥ 0.9 | ✅ Green |
| First Contentful Paint (FCP) | 1,461 ms | **1,204 ms** | ≤ 1.8 s | ✅ Green |
| Largest Contentful Paint (LCP) | 1,761 ms | **1,504 ms** | ≤ 2.5 s | ✅ Green |
| Total Blocking Time (TBT) | 196 ms | **0 ms** | ≤ 200 ms | ✅ Green (run-1 196 ms is style/layout simulator noise from the large DOM; run 2 = 0) |
| Cumulative Layout Shift (CLS) | 0 | 0 | ≤ 0.1 | ✅ Green |
| Speed Index | 2,477 ms | **1,204 ms** | ≤ 3.4 s | ✅ Green |
| Third-party requests | 0 | 0 | — | ✅ None |
| Render-blocking resources | `style.min.css` only (3,698 B) | same | — | ✅ Intended |

**Journey recap (live, same Lighthouse config):**

| Stage | Score | FCP | LCP | CLS |
|---|---|---|---|---|
| Google Fonts (post-content-growth) | 0.86 | 3,280 ms | 3,280 ms | 0 |
| **Self-hosted variable fonts + preload** | **0.96–1.00** | **~1.2–1.5 s** | **~1.5–1.8 s** | **0** |

**Status:** 20/20 practices closed. The only render-blocking resource is the minified, Brotli-compressed, CDN-cached `style.min.css`; fonts are 2 self-hosted variable woff2 (preloaded LCP font, immutable cache); zero third-party requests; CLS and TBT at/under threshold. Remaining items are inherited platform capabilities (compression, HTTP/2, TLS) or verified N/A (no render images). No further on-page performance work is pending.

## Final polish verification (2026-08-10)

Script loading audit — **no non-deferred/blocking script tags exist; no fixes required**:

| Page | External scripts | Loading | Verdict |
|---|---|---|---|
| `index.html` | `analytics.js`, `script.min.js` | `defer` / `defer` | ✅ non-blocking |
| `privacy.html` | — | (2 inert `application/ld+json`) | ✅ no JS |
| `impressum.html` | — | (2 inert JSON-LD) | ✅ no JS |
| `dpa.html` | — | (2 inert JSON-LD) | ✅ no JS |
| `404.html` | — | (1 inert JSON-LD) | ✅ no JS |

Font preload audit — **all fonts used by a page are preloaded**:

| Page | Preloads | Rationale |
|---|---|---|
| `index.html` | `inter-variable.woff2` + `jetbrains-mono-variable.woff2` (both, `crossorigin`) | Uses both fonts (hero/body + `.stat-number`/`.step-number` mono) |
| `privacy.html`, `impressum.html`, `dpa.html` | `inter-variable.woff2` (Inter only) | JetBrains Mono is **unused** on legal pages — verified 0 references to `JetBrains`/`stat-number`/`step-number` in all 3 files; preloading it would waste 31 KB on the critical path |
| `404.html` | none | Self-contained (system fonts + inline CSS) — no font to preload |

Zero external requests (live, 2 Lighthouse traces): `third-parties-insight` = **[]**; the only request host is `phishdefend-ai.vercel.app` (6 requests: HTML, `style.min.css`, `analytics.js`, `script.min.js`, 2 × `/fonts/*.woff2`). No `googleapis`/`gstatic`/`googletagmanager` in any served HTML.

Root mirrors: all 5 HTML files byte-identical to `static/` (incl. `data-processing-agreement.html` ↔ `static/dpa.html`).

Note: the **live** `index.html` currently shows only the Inter preload because the deployed snapshot predates the source's 2nd (`jetbrains-mono`) preload — source/root are in sync; the next `vercel --prod` picks up both. Result: **0 fixes applied, 100% conformant.**

## Automated post-deploy check — live_check.py (baseline 2026-08-10)

Added **`live_check.py`** at repo root: stdlib-only, automates the 10-point post-deploy checklist from `docs/deploy-instructions.md` §5. Usage `python live_check.py [BASE_URL]` (default `https://phishdefend-ai.vercel.app`); exit code 0 = all pass, 1 = any fail.

Baseline run against the current live site — **9/10 PASS, 1 FAIL**:

| # | Check | Result | Evidence |
|---|---|---|---|
| 1 | All sitemap URLs return HTTP 200 | ✅ PASS | 6 URLs, all 200 |
| 2 | Privacy serves DPO email, no placeholder | ❌ **FAIL** | live `/privacy` has `rorshopping@gmail.com` **and** still contains `[dpo@email.com]` |
| 3 | Self-referencing canonicals | ✅ PASS | all 4 pages exact-match |
| 4 | Zero Google Fonts references | ✅ PASS | no googleapis/gstatic on 5 pages |
| 5 | JSON-LD blocks intact | ✅ PASS | all pages parse; expected @types present (Org/WebSite/Breadcrumb/SoftwareApp/Service/FAQPage on `/`; Org+Breadcrumb on legal; Org on 404) |
| 6 | og:image / twitter:image resolve 200 | ✅ PASS | `og-image.png` → 200 |
| 7 | robots.txt / sitemap.xml cache headers | ✅ PASS | both `max-age=3600`, robots has `Sitemap:` |
| 8 | woff2 fonts immutable cache | ✅ PASS | both fonts 200 + `immutable` |
| 9 | 404 page | ✅ PASS | `/404` → 200 styled; unknown path → 404 styled (`noindex`) |
| 10 | llms.txt / llms-full.txt | ✅ PASS | both 200 |

**Check 2 FAIL = deploy staleness, not a code defect** (matches `deploy-instructions.md` §8): source `static/privacy.html` and root `privacy.html` are correct — `rorshopping@gmail.com` present, `[dpo@email.com]` absent, mirror IN SYNC. The **live deployment predates the DPO-email fix**; the next `vercel --prod` ships it and check 2 will pass. Re-run: `python live_check.py`.
