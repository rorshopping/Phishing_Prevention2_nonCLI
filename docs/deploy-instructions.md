# Deployment Instructions — PhishDefend AI (Vercel)

How to deploy `phishdefend-ai` to production, keep the root/static mirror in sync, and verify the live site afterward.

---

## 1. Prerequisites

- Node.js + Vercel CLI (`vercel --version` → 58.x). Upgrade with `npm install -g vercel@latest`.
- A Vercel auth token with access to project `phishdefend-ai` (`prj_89ZWzuOuBgHmXGu7sqt3CoGlox4Z`, org `team_yS61zVlm5pSlXVCZNcmAc1Ge`).
- **Known blocker (2026-08-10):** this workspace has no `VERCEL_TOKEN` and no saved login. `vercel --prod` fails with `Missing authentication token` / `No existing credentials found`. You must provide the token once (steps below) before any deploy can run.

## 2. Authenticate (one time)

Set the token persistently so future shells pick it up:

```powershell
# Run in YOUR terminal (not inside an agent shell that caches an older env):
setx VERCEL_TOKEN "<your_vercel_token>"

# CRITICAL: close and reopen your terminal so the new env var propagates.
# Verify:
echo $env:VERCEL_TOKEN          # must print the token
vercel whoami                    # must print your Vercel username
```

> Note: `setx` only affects processes started *after* it runs. If a shell was already open, its spawned processes won't see the token — reopen the terminal.

Alternative (single-shot, token not persisted):

```powershell
vercel --prod --token "<your_vercel_token>"
```

## 3. Sync `static/` → root (Vercel serves the REPO ROOT)

`static/` is the source of truth; the repo root is what Vercel deploys. **After any `static/` edit, mirror the affected files to root byte-for-byte before deploying.** All **18 mirrored files** must be identical (SHA-256 match).

| # | Root file | Source (`static/`) |
|---|-----------|--------------------|
| 1 | `index.html` | `static/index.html` |
| 2 | `privacy.html` | `static/privacy.html` |
| 3 | `impressum.html` | `static/impressum.html` |
| 4 | `data-processing-agreement.html` | `static/dpa.html` |
| 5 | `404.html` | `static/404.html` |
| 6 | `robots.txt` | `static/robots.txt` |
| 7 | `sitemap.xml` | `static/sitemap.xml` |
| 8 | `llms.txt` | `static/llms.txt` |
| 9 | `llms-full.txt` | `static/llms-full.txt` |
| 10 | `style.css` | `static/style.css` |
| 11 | `style.min.css` | `static/style.min.css` |
| 12 | `script.js` | `static/script.js` |
| 13 | `script.min.js` | `static/script.min.js` |
| 14 | `analytics.js` | `static/analytics.js` |
| 15 | `og-image.png` | `static/og-image.png` |
| 16 | `logo.svg` | `static/logo.svg` |
| 17 | `fonts/inter-variable.woff2` | `static/fonts/inter-variable.woff2` |
| 18 | `fonts/jetbrains-mono-variable.woff2` | `static/fonts/jetbrains-mono-variable.woff2` |

Sync command (run from repo root):

```powershell
Copy-Item static\index.html index.html -Force
Copy-Item static\privacy.html privacy.html -Force
Copy-Item static\impressum.html impressum.html -Force
Copy-Item static\dpa.html data-processing-agreement.html -Force
Copy-Item static\404.html 404.html -Force
Copy-Item static\robots.txt robots.txt -Force
Copy-Item static\sitemap.xml sitemap.xml -Force
Copy-Item static\llms.txt llms.txt -Force
Copy-Item static\llms-full.txt llms-full.txt -Force
Copy-Item static\style.css style.css -Force
Copy-Item static\style.min.css style.min.css -Force
Copy-Item static\script.js script.js -Force
Copy-Item static\script.min.js script.min.js -Force
Copy-Item static\analytics.js analytics.js -Force
Copy-Item static\og-image.png og-image.png -Force
Copy-Item static\logo.svg logo.svg -Force
Copy-Item static\fonts\inter-variable.woff2 fonts\inter-variable.woff2 -Force
Copy-Item static\fonts\jetbrains-mono-variable.woff2 fonts\jetbrains-mono-variable.woff2 -Force
```

Verify zero drift before deploying:

```powershell
$a=(Get-FileHash index.html -Algorithm SHA256).Hash; $b=(Get-FileHash static\index.html -Algorithm SHA256).Hash; "index.html: $(if($a -eq $b){'MATCH'}else{'DIFF'})"
# (repeat for each of the 18 pairs; or use a loop over the table above)
```

## 4. Deploy

```powershell
vercel --prod
```

Vercel builds from the repo root, applies `vercel.json`, and ignores `src/`/`tests/`/`gophish/`/secrets via `.vercelignore`. Deploy URL for the main production alias: `https://phishdefend-ai.vercel.app/`.

## 5. Post-Deploy Verification Checklist

Run these checks against the live site after `vercel --prod`:

1. **Privacy page serves the DPO email** — fetch `https://phishdefend-ai.vercel.app/privacy` (and `/privacy.html`): body contains `rorshopping@gmail.com` and does NOT contain `[dpo@email.com]` or `[your@email.com]`.
2. **Self-referencing canonicals** — every indexable page serves exactly one canonical matching its URL:
   - `/` → `https://phishdefend-ai.vercel.app/`
   - `/impressum` → `.../impressum`
   - `/privacy` → `.../privacy`
   - `/data-processing-agreement` → `.../data-processing-agreement`
3. **Zero Google Fonts references** — served HTML for all 4 pages must NOT contain `fonts.googleapis.com` or `fonts.gstatic.com`; fonts are self-hosted (`/fonts/inter-variable.woff2`, `/fonts/jetbrains-mono-variable.woff2`) with `<link rel="preload" as="font" type="font/woff2" crossorigin>`.
4. **JSON-LD intact** — `/` serves 6 schema blocks (Organization, WebSite, BreadcrumbList, SoftwareApplication, Service, FAQPage); legal pages serve Organization + BreadcrumbList; 404 serves Organization. All parse as valid JSON.
5. **Meta verification** — `google-site-verification` (live token) present on `/`; `msvalidate.01` present (token still a placeholder → replace before go-live).
6. **OG/Twitter images** — `og:image` and `twitter:image` = `https://phishdefend-ai.vercel.app/og-image.png` on all 4 pages; asset returns HTTP 200.
7. **robots.txt / sitemap.xml** — served with `Cache-Control: public, max-age=3600`; robots lists `Sitemap: https://phishdefend-ai.vercel.app/sitemap.xml` and AI-crawler allow rules.
8. **Fonts cache header** — `/fonts/inter-variable.woff2` returns `Cache-Control: public, max-age=31536000, immutable`.
9. **404 handling** — requesting a nonexistent path returns HTTP 404 with the styled 404 page (`noindex, follow`), not a Vercel default page.
10. **llms.txt** — `https://phishdefend-ai.vercel.app/llms.txt` and `/llms-full.txt` return 200; llms.txt links resolve (home, llms-full.txt, privacy, DPA, impressum, sitemap).

Quick PowerShell check for the key items:

```powershell
$pages = "https://phishdefend-ai.vercel.app/", "https://phishdefend-ai.vercel.app/privacy", "https://phishdefend-ai.vercel.app/impressum", "https://phishdefend-ai.vercel.app/data-processing-agreement"
foreach ($u in $pages) {
  $h = (Invoke-WebRequest $u).Content
  "{0} -> email={1} googlefonts={2}" -f $u, ($h -match "rorshopping@gmail.com"), ($h -match "fonts\.googleapis")
}
```

## 6. `vercel.json` Audit — no blockers found ✅

Current config (verified 2026-08-10):

```json
{
  "version": 2,
  "cleanUrls": true,
  "trailingSlash": false,
  "headers": [
    { "source": "/(.*)\\.(css|js|mjs)",            "headers": [ "Cache-Control: public, max-age=86400" ] },
    { "source": "/(.*)\\.(svg|png|jpg|jpeg|webp|avif|ico|gif)", "headers": [ "Cache-Control: public, max-age=86400" ] },
    { "source": "/(.*)\\.(woff|woff2|ttf|otf)",    "headers": [ "Cache-Control: public, max-age=31536000, immutable" ] },
    { "source": "/(robots\\.txt|sitemap\\.xml)",   "headers": [ "Cache-Control: public, max-age=3600" ] }
  ]
}
```

Findings:
- **`cleanUrls: true`** → `/privacy.html` is served at `/privacy`, matching the pages' self-referencing canonicals. No redirect/rewrite rules needed; nothing conflicts with the clean-URL canonicals.
- **`trailingSlash: false`** → consistent with canonical URLs (no trailing slash).
- **Font headers already present** (woff2 `immutable` 1y) — the self-hosted font serving is cache-optimized.
- No `routes`/`redirects` block deploy; no `buildCommand`/`outputDirectory` overrides — Vercel serves the root statically as intended.
- No `rewrites` for `/api/*` — the FastAPI backend is **not** deployed on Vercel (it's a separate/local service); the marketing site is fully static. This is expected.

## 7. `.vercelignore` Audit — no blockers found ✅

Excludes (all appropriate):
- `src/`, `tests/`, `*.py`, `__pycache__/`, `*.py[cod]`, `*.egg-info/`, `.pytest_cache/` — backend & tests never deployed.
- `gophish/`, `gophish.zip`, `start_gophish.ps1`, `*.xlsx`, `*.crt`, `*.key` — embedded binaries, local tooling, keys.
- `.env`, `.env.example` — secrets never deployed (token/API keys stay local).
- `*.db`, `*.log` — databases and logs excluded.
- `.vercel/` — local Vercel state.
- `architecture_visualization.html` — root-only dev artifact; excluded so it never becomes a public page.

Findings:
- Nothing in the ignore list blocks the 18 mirrored files (HTML, css/js, fonts, images, llms, robots, sitemap are all allowed through).
- **Recommendation (optional, not a blocker):** add `docs/` to `.vercelignore` so `docs/*.md` are not served publicly (harmless today since nothing links to them). If added, it does not affect the 18-file sync.

---

## 8. Current Deploy Status (2026-08-10)

- Deploy is **blocked on authentication only** — a `VERCEL_TOKEN` must be provided (Section 2), then `vercel --prod`.
- The 18-file root↔static sync was verified MATCH before this doc; the last pending deploy would ship the DPO-email privacy edit (`rorshopping@gmail.com`, `[dpo@email.com]` removed).
- Once deployed, run the Section 5 checklist to confirm live parity (prior live checks in `docs/seo-schema-checklist.md` describe the pre-edit deployment).
