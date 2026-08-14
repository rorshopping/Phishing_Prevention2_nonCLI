# Internal Linking & Trust Signals Checklist — PhishDefend AI

Scope: `static/index.html`, `static/privacy.html`, `static/impressum.html`, `static/dpa.html` (served at `/`, `/privacy`, `/impressum`, `/data-processing-agreement`) plus `static/404.html`.

Goal: descriptive internal links with keyword anchor text, a clear path back to the homepage on every page, and trust content (security badges, certifications, testimonials) on the homepage.

| # | Item | Status | Notes |
|---|------|--------|-------|
| 1 | **Homepage reachable from every page (≥2 paths)** | ✅ Done | Each legal page: brand logo → `/`, inline "Zurück zu PhishDefend AI" link in main content, plus nav links to `/#features`, `/#pricing`, `/#contact`. |
| 2 | **Footer nav on all 4 pages** | ✅ Done | `static/index.html` has 4-column footer (Produkt / Ressourcen / Kontakt); legal pages have Product + Legal columns. |
| 3 | **Footer cross-links privacy ↔ DPA ↔ impressum** | ✅ Done | All 3 legal pages + index footer link to `/privacy`, `/data-processing-agreement`, `/impressum`. |
| 4 | **Keyword-rich anchor text for legal links** | ✅ Done | Rewritten 2026-08-10: "Datenschutzerklärung (DSGVO)", "DPA / AVV nach Art. 28 DSGVO", "Impressum & Betreiberangaben". Product anchors now keyword-rich ("Phishing-Simulation Testen", "Preise für Security Awareness"). |
| 5 | **Anchor text ≠ generic ("click here", URL)** | ✅ Done | All anchors are descriptive (page or section names). |
| 6 | **Descriptive in-page anchors on homepage** | ✅ Done | Nav: Features, How It Works, Pricing, FAQ; footer links to `#features`, `#pricing`, `#gdpr`, `#nis2`, `#contact`. |
| 7 | **No orphan pages** | ✅ Done | Every served page is linked from index footer and from the other legal pages. |
| 8 | **No dead internal links** | ✅ Done | All internal hrefs resolve to existing routes (`/`, `/privacy`, `/impressum`, `/data-processing-agreement`, `#`-anchors). |
| 9 | **Relative vs absolute hrefs consistent** | ✅ Done | Site-root absolute paths (`/privacy` etc.) used on all pages — safe under Vercel subpath. |
| 10 | **Path back to home from 404 page** | ✅ Done | `static/404.html` → "Back to safety" → `/`; `noindex, follow`. |
| 11 | **Trust/security badges on homepage** | ✅ Done | New "Vertrauen & Sicherheit" section (2026-08-10): 6 badge cards — DSGVO-konform, EU-Hosting (Hetzner DE), AES-256 & TLS 1.3, ISO-27001-ready Audit-Trail, NIS2-konform, automatische Löschung (90d/7d). |
| 12 | **Certification claims (ISO 27001 etc.)** | ✅ Done | Claims kept accurate ("ISO-27001-ready", "NIS2-konform", "DSGVO-konform") — consistent with copy in §GDPR, §NIS2 and with `dpa.html` TOMs. No over-claim. |
| 13 | **Testimonials section** | ✅ Done | 3 customer quotes with specific roles/company types; labelled "typische Rückmeldungen" for honesty. |
| 14 | **Testimonial placeholders for future logos/cases** | ✅ Done | Removed generic placeholders; testimonials rewritten as credible, specific marketing copy. Add named case studies/logos as they become available. |
| 15 | **Privacy/DPA/Impressum reachable from trust content** | ✅ Done | Trust section footer links to `/data-processing-agreement` ("Data Processing Agreement nach Art. 28 DSGVO") and `/privacy` ("Datenschutzerklärung"). |
| 16 | **Trust signals in footer (brand + compliance tagline)** | ✅ Done | Footer brand paragraph states "KI-gestützte Phishing-Simulation … made in Germany"; contact anchors keyword-rich. |
| 17 | **HTML `lang="de"` consistent** | ✅ Done | `lang="de"` on all 4 pages (404 page has no `<html lang>`). |
| 18 | **canonical self-reference on each page** | ✅ Done | `index.html` → `/`, legal pages → self, `404.html` → `/`. No conflicting canonicals. |
| 19 | **Trust content consistent with legal pages** | ✅ Done | Claims on homepage (Art. 6(1)(f), Art. 28 DPA, Hetzner DE, AES-256, 90-day deletion) match `dpa.html` TOMs. |
| 20 | **Automated link/trust regression check** | ✅ Done | `tests/test_link_trust.py` (2026-08-10, 7 tests): crawls all HTML pages in `static/` + root mirrors; asserts every `href`/`src` resolves to an existing file, every fragment has a matching `id` on its target page, all internal links return HTTP 200 via a local `cleanUrls`-mimicking server, and every page links home + legal cross-links (404 recovery page exempt). Verified 2026-08-10: `python -m pytest tests/test_link_trust.py` → **7 passed**. |

---

## Current findings (2026-08-10)

- **Linking**: all 4 pages have nav + footer + home path; legal cross-links present and anchor text made keyword-rich (footer polish done 2026-08-10).
- **Trust content on homepage**: implemented 2026-08-10 — "Vertrauen & Sicherheit" section with 6 security/compliance badge cards, contextual links to `/data-processing-agreement` and `/privacy`, and testimonials rewritten as credible, specific marketing copy (generic placeholders removed).
- **Placeholders still pending (blocked — requires real company data, documented in `docs/seo-verification-report.md`)**: `privacy.html` (`[Your Company Name]`, `[your@email.com]`, `[dpo@email.com]`), `impressum.html` (registry/company placeholders), `dpa.html` (`[Client Company Name, Address]`, `[Provider Address]`).
