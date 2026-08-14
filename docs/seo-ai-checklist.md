# AI-SEO Checklist — Top 20

Checklist for making phishdefend-ai discoverable and accurately describable by AI/LLM crawlers (GPTBot, ClaudeBot, PerplexityBot, Google-Extended, etc.) and AI search assistants (ChatGPT, Perplexity, Gemini, Claude, Copilot).

Status legend: `[ ]` todo · `[x]` done · `[~]` partial

## Foundation

- [x] **1. `llms.txt` in site root** — Short (≤2 KB) entity card: name, one-line description, key links, what/who/offers.
- [x] **2. `llms-full.txt` in site root** — Full plain-language entity details (features, pricing, compliance, FAQ digest, related pages).
- [x] **3. `llms.txt` links to `llms-full.txt`** — So crawlers that only read the short file can escalate to full detail.
- [x] **4. Keep it plain-language & markdown** — No HTML, no JavaScript, no login walls. Simple H1, blockquote, bullets, markdown links.
- [x] **5. Serve from the same domain & HTTPS** — `/llms.txt` and `/llms-full.txt` must be reachable at the canonical domain root.

## Crawlability / robots.txt

- [x] **6. Explicitly allow major AI crawlers** — `GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `anthropic-ai`, `PerplexityBot`.
- [x] **7. Allow secondary AI crawlers** — `Google-Extended`, `Applebot-Extended`, `Meta-ExternalAgent`, `CCBot`, `Amazonbot`, `cohere-ai`, `Bytespider`.
- [x] **8. Never block AI crawlers in the `*` rule** — Keep a permissive default (`User-agent: *` / `Allow: /`).
- [x] **9. Sitemap referenced in robots.txt** — `Sitemap: https://<domain>/sitemap.xml`.
- [x] **10. Verify `robots.txt` is served and current** — App route must read the same file crawlers receive; test after every change.

## Entity clarity (what / who / offers)

- [x] **11. One unambiguous product name** — State canonical name and all alternates ("PhishDefend AI" / "Phish Defend").
- [x] **12. One-sentence "what it does"** — Plain, first-touch definition (no marketing fluff): *AI-powered, fully automated phishing simulation & security awareness training.*
- [x] **13. Explicit "who it is for"** — Target market: European SMEs, 10–500 employees, no dedicated security team.
- [x] **14. Explicit "what it offers"** — Feature list: 25 campaigns/year, AI-personalized templates, vishing/smishing, alerts, reports, risk scoring.
- [x] **15. Concrete facts LLMs can quote** — Pricing numbers, deliverability (99.7%), click-rate improvement (30% → <5% in 6 months), GDPR basis (Art. 6(1)(f)).

## Accuracy & consistency

- [x] **16. Facts match the website** — Pricing, feature counts, and compliance claims must agree between `llms.txt`, `llms-full.txt`, `index.html`, and structured data.
- [x] **17. Structured data matches too** — `Organization` / `WebSite` / `SoftwareApplication` / `FAQPage` JSON-LD in `index.html` must not contradict `llms.txt`.
- [x] **18. No placeholders in AI-facing content** — `llms.txt`/`llms-full.txt` are placeholder-free; all placeholders fillable from existing site data are filled with the operator's consistent contact identity (`rorshopping@gmail.com` — controller + DPO email). Remaining `[…]` tokens are **by-design operator-supplied legal registration data** (company name/address, phone, register court, HRB, VAT ID, managing director) that cannot be invented — final classification in `docs/seo-audit.md` §9.3.
- [x] **19. Answer-formatting for FAQ content** — LLMs quote FAQ answers; keep them short, factual, and self-contained (Q&A pairs).
- [x] **20. Automated regression test** — A test that (a) asserts the files exist and are served, (b) simulates an LLM prompt and asserts the content answers entity-clarity questions.

---

## Current status (August 2026)

- [x] `llms.txt` and `llms-full.txt` created in repo root and served via `/llms.txt`, `/llms-full.txt` (`src/main.py`)
- [x] AI-crawler directives added to `static/robots.txt` (GPTBot, OAI-SearchBot, ClaudeBot, anthropic-ai, PerplexityBot, Google-Extended, Applebot-Extended, Meta-ExternalAgent, Amazonbot, cohere-ai, CCBot, Bytespider)
- [x] `robots.txt` route reads the static file (single source of truth)
- [x] `llms.txt` / `llms-full.txt` URLs added to `static/sitemap.xml` (served by the `/sitemap.xml` route, which reads the static file)
- [x] LLM-prompt test added in `tests/test_llms_txt.py` (incl. endpoint-response and sitemap-discoverability checks)
- [x] `llms.txt` refreshed against site state: €1,000/€2,500 tiers, NIS2/ISO 27001 (A.6.3 & A.5.36), Smishing module, 11-FAQ digest — kept at ~2.0 KB (≤2 KB spec)
- [x] `llms-full.txt` refreshed with NIS2/ISO 27001 compliance section, Smishing details, and FAQ digest aligned to the 11 site FAQ items
- [x] **New sections reflected** (content agent additions): `llms.txt` + `llms-full.txt` now cover Anti-Phishing-Training (micro-learning), Mitarbeiter-Sicherheit (no-sanction security culture), KMU focus, and Positioning & Alternatives (KnowBe4 / SoSafe / Hoxhunt / gophish) + Benchmarks & ROI
- [x] **Trust & Security reflected**: `llms-full.txt` gained a "Trust & Security (Vertrauen & Sicherheit)" section; `llms.txt` compliance line now covers TLS 1.3, Hetzner Frankfurt hosting, and 90-day/7-day auto-deletion per the new trust badges
- [x] Prompt-grader extended to new topics + trust standards; `src/llms_txt.py` now serves the `static/` mirrors (single source of truth); root & static llms files byte-identical; tests assert root/static mirroring and served==root
- [x] All fillable legal placeholders filled (emails → `rorshopping@gmail.com`, incl. DPO); remaining tokens are operator-supplied legal registration data (cannot be invented) — item 18 closed, see `docs/seo-audit.md` §9.3
- [ ] Root mirror files must stay byte-for-byte in sync with `static/` after every edit (16-file list in AGENTS.md §Root mirror files, see `docs/seo-audit.md` §Root-Duplicate Fix); `index.html` verified in sync 2026-08-10

---

## Mirror inventory note (appended 2026-08-10)

The root ↔ `static/` mirror set was expanded from **14 to 18 files** to include the AI-SEO files `llms.txt`/`llms-full.txt` and the self-hosted fonts `fonts/inter-variable.woff2`/`fonts/jetbrains-mono-variable.woff2`. Current inventory (documented in `AGENTS.md` §Root mirror files, `docs/seo-audit.md` §1b):

| # | File | Root source | Served by |
|---|---|---|---|
| 1 | `index.html` | `static/index.html` | Vercel root + FastAPI mount |
| 2 | `privacy.html` | `static/privacy.html` | Vercel root + FastAPI route |
| 3 | `impressum.html` | `static/impressum.html` | Vercel root + FastAPI route |
| 4 | `data-processing-agreement.html` | `static/dpa.html` | Vercel root + FastAPI route |
| 5 | `404.html` | `static/404.html` | Vercel root + FastAPI mount |
| 6 | `robots.txt` | `static/robots.txt` | Vercel root + FastAPI route (`src/main.py` → `src/llms_txt.py`) |
| 7 | `sitemap.xml` | `static/sitemap.xml` | Vercel root + FastAPI route |
| 8 | `llms.txt` | `static/llms.txt` | Vercel root + FastAPI route (`/llms.txt` → `src/llms_txt.py.get_llms_txt`) |
| 9 | `llms-full.txt` | `static/llms-full.txt` | Vercel root + FastAPI route (`/llms-full.txt` → `src/llms_txt.py.get_llms_full_txt`) |
| 10 | `style.css` | `static/style.css` | Vercel root + FastAPI mount |
| 11 | `style.min.css` | `static/style.min.css` | Vercel root + FastAPI mount |
| 12 | `script.js` | `static/script.js` | Vercel root + FastAPI mount |
| 13 | `script.min.js` | `static/script.min.js` | Vercel root + FastAPI mount |
| 14 | `analytics.js` | `static/analytics.js` | Vercel root + FastAPI mount |
| 15 | `og-image.png` | `static/og-image.png` | Vercel root + FastAPI mount |
| 16 | `logo.svg` | `static/logo.svg` | Vercel root + FastAPI mount |
| 17 | `fonts/inter-variable.woff2` | `static/fonts/inter-variable.woff2` | Vercel root + FastAPI mount |
| 18 | `fonts/jetbrains-mono-variable.woff2` | `static/fonts/jetbrains-mono-variable.woff2` | Vercel root + FastAPI mount |

**Read path:** `src/llms_txt.py` reads all three serving files (`llms.txt`, `llms-full.txt`, `robots.txt`) from `static/` — the FastAPI routes and Vercel's root serving therefore expose byte-identical content. **Rule:** after editing any `static/` file, copy it to root before `vercel --prod`; `tests/test_llms_txt.py::test_root_mirrors_static_serving_files` guards byte-identity for all four SEO/AI files.

---

## Audit evidence — AI crawler access & llmstxt.org spec compliance (2026-08-10)

Verified against the **current** `static/` files (source of truth) and the root mirrors; methodology = programmatic parse + `tests/test_llms_txt.py` (47 passed).

### robots.txt — crawler access
| Check | Result | Evidence |
|---|---|---|
| `GPTBot` allowed | ✅ | `User-agent: GPTBot` + `Allow: /` block present |
| `ClaudeBot` allowed | ✅ | `User-agent: ClaudeBot` + `Allow: /` block present |
| `PerplexityBot` allowed | ✅ | `User-agent: PerplexityBot` + `Allow: /` block present |
| `Google-Extended` allowed | ✅ | `User-agent: Google-Extended` + `Allow: /` block present |
| Permissive default (`*`) | ✅ | `User-agent: *` / `Allow: /`, no global `Disallow` |
| Sitemap referenced | ✅ | `Sitemap: https://phishdefend-ai.vercel.app/sitemap.xml` |
| Also allowed | ✅ | OAI-SearchBot, ChatGPT-User, anthropic-ai, Claude-Web, Applebot-Extended, Meta-ExternalAgent, Amazonbot, cohere-ai, CCBot, Bytespider |
| Served & mirrored | ✅ | `/robots.txt` route → `src/llms_txt.py` reads `static/robots.txt`; root `robots.txt` byte-identical (SHA-256) |

### llms.txt — llmstxt.org v2 format
| Spec rule | Result | Evidence |
|---|---|---|
| H1 (only required) | ✅ | `# PhishDefend AI (Phish Defend)` is first heading |
| Blockquote summary | ✅ | Present immediately after H1 |
| No H3+ headings | ✅ | None found |
| Non-heading detail sections | ✅ | Entity metadata bullets now a plain (non-heading) list |
| H2 sections = file lists | ✅ | Single `## Key pages` section, all 5 entries are `[name](url)[: notes]` markdown links |
| Markdown links resolve | ✅ | 5 links (/, /llms-full.txt, /privacy, /data-processing-agreement, /impressum) — all valid |
| Size | ✅ | 2040 bytes ≤ 2048 (≤2 KB guidance); no HTML |
| Links to llms-full.txt | ✅ | Present |
| **Fix applied** | 🛠️ | Prior `## Entity` H2 held 11 non-link metadata bullets (spec violation); restructured → entity detail as non-heading section, links under `## Key pages` |

### llms-full.txt — plain-language markdown
| Check | Result | Evidence |
|---|---|---|
| Markdown / no HTML | ✅ | 13 H2 sections, no H3+, no HTML/JS |
| Size | ✅ | 9976 bytes (no limit for full file) |
| Links | ✅ | `Related Pages` converted from plain URLs → markdown links (`[name](url)`); all resolve |
| Content consistency | ✅ | Trust & Security, Anti-Phishing-Training, Mitarbeiter-Sicherheit, Benchmarks & ROI, 11-Q&A FAQ digest, pricing/compliance — all match `index.html` |

### Regression tests
`python -m pytest tests/test_llms_txt.py -q` → **47 passed** (presence, size, sitemap disclosure, root↔static mirroring, served-vs-root identity, AI-crawler directives, LLM prompt-grader for all 11 questions on both files).

### Live production verification (2026-08-10, post-deploy)
Fetched the deployed site with a Python `urllib` client (no cache) and compared bytes against the repo `static/` files:

| URL | HTTP | Content-Type | Result |
|---|---|---|---|
| `https://phishdefend-ai.vercel.app/robots.txt` | 200 | `text/plain; charset=utf-8` | ✅ byte-identical to repo `static/robots.txt` |
| `https://phishdefend-ai.vercel.app/llms.txt` | 200 | `text/plain; charset=utf-8` | ✅ byte-identical to repo `static/llms.txt` |
| `https://phishdefend-ai.vercel.app/llms-full.txt` | 200 | `text/plain; charset=utf-8` | ✅ byte-identical to repo `static/llms-full.txt` |

Live `/robots.txt` crawler blocks — all present with `Allow: /`:
- `GPTBot` ✅ · `ClaudeBot` ✅ · `PerplexityBot` ✅ · `Google-Extended` ✅
- Default `User-agent: *` / `Allow: /` ✅ · `Sitemap:` reference ✅

Live `/llms.txt` structure (llmstxt.org v2):
- H1 `# PhishDefend AI (Phish Defend)` ✅ · blockquote summary ✅ · no H3+ ✅
- Single H2 `## Key pages` file list with 5 markdown links (`[name](url)[: notes]`): Homepage, llms-full.txt, Privacy Policy, Data Processing Agreement, Impressum ✅
- Links to `llms-full.txt` ✅

Live `/llms-full.txt`: H1 ✅ · 13 H2 sections · no H3+ ✅ · `Related Pages` = 5 markdown links ✅.

**Conclusion:** the production deploy serves the exact AI-crawler config validated in the repo — status, content-type, crawler Allow blocks, and llms.txt H1 + link-list structure all confirmed live.

### Live llms link graph & sitemap verification (2026-08-10)

Extracted every markdown link and internal URL from the live `/llms.txt` and `/llms-full.txt` and resolved each against production:

| Link source | Target | Live status |
|---|---|---|
| `/llms.txt` | `/` (Homepage) | 200 text/html |
| `/llms.txt` | `/llms-full.txt` | 200 text/plain |
| `/llms.txt` | `/privacy` | 200 text/html |
| `/llms.txt` | `/data-processing-agreement` | 200 text/html |
| `/llms.txt` | `/impressum` | 200 text/html |
| `/llms-full.txt` | `/` (Official website + Related Pages) | 200 text/html |
| `/llms-full.txt` | `/impressum` | 200 text/html |
| `/llms-full.txt` | `/privacy` | 200 text/html |
| `/llms-full.txt` | `/data-processing-agreement` | 200 text/html |
| `/llms-full.txt` | `/sitemap.xml` | 200 application/xml |

- **All 6 unique internal targets resolve to 200** (`/`, `/impressum`, `/privacy`, `/data-processing-agreement`, `/llms-full.txt`, `/sitemap.xml`). No dead links in the AI link graph.
- No external links in either llms file (every URL is on `phishdefend-ai.vercel.app`).

Live `/sitemap.xml`:
- Lists **6 URLs** = exactly the **4 indexable HTML pages** (`/`, `/impressum`, `/privacy`, `/data-processing-agreement`) + `/llms.txt` + `/llms-full.txt`.
- **No `dpa.html`** entry — the DPA is correctly referenced as `/data-processing-agreement` only.
- The 5th HTML file in the repo (`404.html`) is `noindex, follow` and **correctly excluded** from the sitemap.
- Static `sitemap.xml` is byte-consistent with the live response (6 URLs, same `loc` set); FastAPI `/sitemap.xml` route reads `static/sitemap.xml`.

### Pre-deploy baseline — legal pages: JSON-LD, canonical, DPO placeholder (2026-08-10)

Fetched the three legal pages from production and compared against the repo (`static/`) so the state can be re-verified after the next deploy.

| Page | HTTP / CT | JSON-LD (live) | Canonical (live) | Self-ref | `[dpo@email.com]` live | `[dpo@email.com]` repo |
|---|---|---|---|---|---|---|
| `/privacy` | 200 text/html | Organization + BreadcrumbList | `https://phishdefend-ai.vercel.app/privacy` | ✅ | ✅ **present** | ❌ removed (→ `rorshopping@gmail.com`) |
| `/impressum` | 200 text/html | Organization + BreadcrumbList | `https://phishdefend-ai.vercel.app/impressum` | ✅ | n/a (no DPO field) | n/a |
| `/data-processing-agreement` | 200 text/html | Organization + BreadcrumbList | `https://phishdefend-ai.vercel.app/data-processing-agreement` | ✅ | n/a | n/a |

Details:
- All three live pages serve **Organization + BreadcrumbList JSON-LD** and a **self-referencing canonical** — matching the repo.
- **The served `/privacy` still contains the placeholder `[dpo@email.com]`.** The repo version replaced it with `rorshopping@gmail.com`. A line-by-line diff of live vs repo `/privacy` shows exactly **one content difference**: the DPO line. **This confirms the DPO fix is staged but not yet live** (agent 6's deploy has not run).
- Remaining placeholders in live `/privacy`: `[Postal Code, City, Germany]`, `[Street & Number]`, `[dpo@email.com]` (repo has the first two only).
- **Post-deploy re-check:** re-run this comparison after the next deploy — expected: live `/privacy` shows `rorshopping@gmail.com` and the placeholder set drops to `[Postal Code, City, Germany]` + `[Street & Number]`.

### AI-SEO deliverables — content & link-graph audit (2026-08-10)

Fetched live `/llms.txt` and `/llms-full.txt`, parsed every referenced URL, and validated each against the served page set + anchor-id resolution.

**Link graph — every referenced page exists (0 issues):**
- `/llms.txt` references 10 URLs (5 markdown links + 5 bare, all internal): `/`, `/llms-full.txt`, `/privacy`, `/data-processing-agreement`, `/impressum` — all map to existing `static/` files.
- `/llms-full.txt` references 11 URLs (5 markdown links + 6 bare, all internal): `/`, `/impressum`, `/privacy`, `/data-processing-agreement`, `/sitemap.xml` — all map to existing `static/` files.
- **No fragment anchors (`#…`) are referenced** by either file (all links are page roots), so there are no anchor-id dependencies to resolve; the generic fragment resolver found nothing to fail.
- No external URLs in either llms file.

**llms-full.txt mirrors current page content (all 15 informative sections covered):**

| index.html section | llms-full.txt evidence |
|---|---|
| Definition (Phishing-Simulation) | "What the Product Does", Smishing |
| Phishing-Test | "phishing test" / "What the Product Does" |
| Features | "What It Offers (Features)", vishing, smishing, reports |
| How It Works | "What the Product Does", 25 campaigns |
| Anti-Phishing-Training | "Anti-Phishing-Training", micro-training, 2-minute |
| E-Mail-Sicherheit | "What the Product Does", phishing emails |
| Für KMU | "Who It Is For", KMU/SME |
| Warum PhishDefend AI | "Positioning & Alternatives", differentiators |
| Vergleich & Alternativen | KnowBe4, SoSafe, Hoxhunt, gophish |
| Benchmarks & ROI | 140,000, 94%, 18–32 |
| GDPR & Compliance | GDPR, Art. 28, Hetzner, Trust & Security |
| NIS2 & ISO 27001 | NIS2, ISO 27001, A.6.3, A.5.36 |
| Mitarbeiter-Sicherheit | "Mitarbeiter-Sicherheit", no sanctions |
| Vertrauen & Sicherheit | "Trust & Security", TLS 1.3, 90 days, Frankfurt |
| FAQ | "Common Questions (FAQ Digest)", 11 questions |

(`Testimonials` and `Get Started` on `index.html` are quotes/form — not entity-clarity content — correctly not mirrored.)

**Conclusion:** every page/anchor the llms files reference resolves to a real served file, and `llms-full.txt` reflects all informative content sections of the live homepage.

### Item 18 — closed (was "Open item")
- **Closed 2026-08-10 — item 18 is `[x]`.** All placeholders fillable from existing site data are filled (`[your@email.com]` + `[dpo@email.com]` → `rorshopping@gmail.com`, root ↔ `static/` byte-identical). The only remaining `[…]` tokens are **by-design operator-supplied legal registration fields** (company name/address, phone, register court, HRB, VAT ID, managing director) — legally required and cannot be invented by an agent; to be supplied by the operator before formal go-live (classification + evidence in `docs/seo-audit.md` §9.3).
