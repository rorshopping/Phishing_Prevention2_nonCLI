# SEO Content Checklist — PhishDefend AI

**Scope:** Phishing-Prevention / Email-Security SEO for the German market (site is `lang="de"`, target = German/EU KMU)
**Status:** Draft v4 · 2026-08-10 (v1 keywords + FAQ; v2 Smishing/pricing/NIS2; v3 Phishing-Test/E-Mail-Sicherheit/Benchmarks; v4 adds Anti-Phishing-Training, KMU, Vergleich/Alternativen, Mitarbeiter-Sicherheit sections)
**Referenced files:** `static/index.html` (+ root `index.html` mirror — Vercel serves repo root; both files kept byte-identical), `static/robots.txt`, `static/sitemap.xml`
**Keyword basis:** German phishing-prevention market (DACH), benchmarked against KnowBe4, Proofpoint Security Awareness, SoSafe, Hoxhunt, Sophos Phish Threat, G DATA, msecure/synaforce, IT-Seal.

---

## 1. Target Keywords — Top 20

Ordered by commercial value × fit for a B2B phishing-simulation vendor.

| # | Keyword | Intent | Coverage in `index.html` |
|---|---------|--------|--------------------------|
| 1 | Phishing-Simulation | Commercial | Strong — H1, meta, features, FAQ |
| 2 | Security Awareness Training | Commercial | Strong — H2s, features, footer |
| 3 | Phishing-Test | Commercial | Covered — dedicated H2 section `static/index.html:360-386` (H2 `:364`) |
| 4 | Phishing-Prävention | Commercial | Partial — body copy in Phishing-Test section (`:360-386`) |
| 5 | Anti-Phishing-Training | Commercial | Covered — dedicated H2 section `static/index.html:495-521` (H2 `:499`) |
| 6 | E-Mail-Sicherheit | Informational | Covered — dedicated H2 section `static/index.html:467-493` (H2 `:471`) |
| 7 | Phishing-E-Mail erkennen / Phishing erkennen | Informational | Partial — new FAQ Q9 |
| 8 | Spear-Phishing | Informational | Covered — definition section + FAQ |
| 9 | CEO-Fraud / CEO-Betrug | Informational | Covered — definition + FAQ + features |
| 10 | Social Engineering | Informational | Covered — features, how-it-works |
| 11 | Vishing | Informational | Covered — features, FAQ, pricing |
| 12 | Smishing | Informational | Covered — FAQ Q8 + dedicated definition section |
| 13 | Security Awareness für Unternehmen | Commercial | Covered — H2s |
| 14 | Phishing-Schutz für Unternehmen | Commercial | Partial — body copy in E-Mail-Sicherheit section (`:467-493`) |
| 15 | Phishing-Simulation Kosten | Commercial/Tx | Covered — FAQ Q10 + objection-handling block in `#pricing` |
| 16 | DSGVO-konforme Phishing-Simulation | Commercial | Covered — GDPR section, FAQ |
| 17 | NIS2 / NIS-2-Richtlinie Security Awareness | Informational | Covered — FAQ Q11 + dedicated `#nis2` section `static/index.html:830-868` |
| 18 | Mitarbeiter-Sicherheit / Mitarbeiter sensibilisieren | Commercial | Covered — dedicated H2 section `static/index.html:870-896` (H2 `:874`) |
| 19 | Phishing-Klickrate / Phishing-Statistik | Informational | Covered — benchmarks-ROI section `static/index.html:758-788` + hero stat + FAQ Q5 |
| 20 | Phishing-Simulation für KMU | Commercial | Covered — dedicated H2 section `static/index.html:610-636` (H2 `:614`) |

---

## 2. Copy Audit Findings

**Well covered:** Phishing-Simulation, Security Awareness Training, CEO-Fraud, Spear-Phishing, Vishing, Social Engineering, DSGVO, KMU, click-rate reduction.

**Gaps found in the audit (status as of v3):**
- "Phishing-Test" rarely used — **completed v3** (verified 2026-08-10): dedicated "Phishing-Test für Mitarbeiter" H2 section `static/index.html:360-386` (H2 `:364`, Klickrate/Report-Rate Kennzahlen + 3 stat cards).
- "E-Mail-Sicherheit" absent — **completed v3**: dedicated H2 section `static/index.html:467-493` (H2 `:471`, defense-in-depth copy + 3 threat stat cards).
- "Phishing-Prävention" / "Phishing-Schutz" — **partial v3**: now present in German body copy (Phishing-Test section `:360-386`, E-Mail-Sicherheit section `:467-493`); headings still English/absent.
- NIS2 / ISO 27001 detail — **completed v2** (verified 2026-08-10; lines corrected v4 after insertions, footer link corrected after testimonial rewrite): dedicated `#nis2` section at `static/index.html:830-868` (H2 `:835`; checklist NIS2 Art. 21, ISO 27001 A.6.3 & A.5.36, DSGVO Art. 32, audit-ready; badge) + footer link `static/index.html:1074`. FAQ Q11 supports it.
- Smishing definition — **completed v2** (verified 2026-08-10): dedicated "Was ist Smishing?" section at `static/index.html:336-358` (H2 `:340`; E-Mail-Phishing vs. Smishing comparison cards). FAQ Q8 supports it.
- Pricing cost objection handling — **completed v2** (verified 2026-08-10; lines corrected v4 after insertions): 4-card objection-handling block in `#pricing` at `static/index.html:584-607` — `:588` Keine versteckten Kosten, `:593` Lohnt sich die Investition? (ROI), `:598` In Minuten einsatzbereit, `:603` Sofort nachweisbarer ROI. FAQ Q10 supports it.
- Anti-Phishing-Training heading — **completed v4** (verified 2026-08-10): dedicated H2 section `static/index.html:495-521` (H2 `:499`; embedded micro-training + 3 stat cards). FAQ Q9 supports it.
- Phishing-Simulation für KMU heading — **completed v4**: dedicated H2 section `static/index.html:610-636` (H2 `:614`; >40 % KMU-Angriffsziel stat, CSV-setup, dashboard-los).
- Vergleich & Alternativen — **completed v4**: section `static/index.html:672-756` (H2 `:676`; comparison table vs. KnowBe4/SoSafe/Hoxhunt/gophish + alternatives paragraph).
- Mitarbeiter-Sicherheit heading — **completed v4**: dedicated H2 section `static/index.html:870-896` (H2 `:874`; non-punitive awareness, team KPIs, Meldekultur).
- `meta name="keywords"` is stale/brief (line 11) — refresh to match the keyword list. *Still open.*
- Mixed language: features/pricing contain English copy inside a `lang="de"` page; consider a `hreflang="en"` variant. *Still open.*
- No `og:image` for social/AI-engine sharing. *Still open.*
- FAQPage JSON-LD was shortened vs. visible text — **aligned 2026-08-10**, all 11 Q&A pairs match.
- FAQPage JSON-LD array order differs from the visible FAQ order (Vishing/Klickrate/Dashboard/Unterschied sequence) — cosmetic, Google does not require order; reorder only if desired.

---

## 3. FAQ Coverage Map (after 2026-08-10 update)

| FAQ Question | Primary keywords targeted |
|---|---|
| Was ist eine Phishing-Simulation und wie funktioniert sie? | Phishing-Simulation |
| Ist PhishDefend AI DSGVO-konform? | DSGVO, Art. 28 DPA |
| Wie viele Phishing-Kampagnen ... | Kampagnenhäufigkeit |
| Was ist Vishing (Voice Phishing) ... | Vishing |
| Wie schnell sinkt die Klickrate ... | Phishing-Klickrate, Statistiken |
| Ist ein Dashboard oder Login erforderlich? | Usability differentiator |
| Unterschied Phishing / Spear-Phishing / CEO-Fraud | Spear-Phishing, CEO-Fraud, BEC |
| Was ist Smishing ... | Smishing / SMS-Phishing *(new)* |
| Wie erkenne ich eine Phishing-E-Mail? | Phishing-E-Mail erkennen, Anti-Phishing-Training *(new)* |
| Was kostet eine Phishing-Simulation ... | Phishing-Simulation Kosten *(new)* |
| Erfüllt PhishDefend AI NIS2 / ISO 27001? | NIS2, ISO 27001 *(new)* |

---

## 4. Content Gaps vs. Competitors

| Competitor content type | PhishDefend AI status | Priority |
|---|---|---|
| "What is phishing" threat glossary / resource hub | Partial — definition + Smishing + Phishing-Test + Anti-Phishing-Training sections | High |
| How-to: recognize phishing emails | Now covered via FAQ Q9 only | Medium |
| NIS2 / ISO 27001 compliance explainers | Now covered via FAQ Q11 + dedicated `#nis2` section (v2) | High |
| Benchmarks & stats pages (click rates, cost per breach, Bitkom damage data) | Covered — dedicated Benchmarks & ROI section `static/index.html:758-788` (H2 `:762`: $140k/incident, Bitkom 94%, 18–32% → 4–8% click rates) + E-Mail-Sicherheit threat stats `:467-493` (v3) | High |
| Template / scenario library showcase | Missing | Medium |
| Report button / Outlook add-in concept | Missing (dashboard-less positioning instead) | Medium |
| Integration pages (Microsoft 365, Outlook, Slack, Google Workspace) | Missing | Medium |
| Comparison / alternatives pages (vs. KnowBe4, SoSafe, Hoxhunt, gophish) | Covered — comparison table + alternatives paragraph, section `static/index.html:672-756` (H2 `:676`, 7 criteria vs. 4 alternatives) (v4) | High |
| Blog / resource center | Missing | Medium |
| Transparent pricing / pricing FAQ | Now covered via FAQ Q10 + on-page objection-handling block in `#pricing` (v2) | Medium |
| Case studies with named, quantified results | Anonymous testimonials only | Medium |
| Smishing / Vishing deep-dive content | Now covered via FAQ Q8 + dedicated Smishing definition section; Vishing via feature card + FAQ (v2) | Low |

---

## 5. Prioritized Actions

1. Work "Phishing-Test", "E-Mail-Sicherheit", "Phishing-Schutz" into German headings/body — **completed v3** (verified 2026-08-10): Phishing-Test H2 `static/index.html:360-386`, E-Mail-Sicherheit H2 `:467-493`; Phishing-Prävention/Phishing-Schutz now in body copy, headings optional.
2. Build a dedicated NIS2 + ISO 27001 compliance section/page — **completed v2** (verified 2026-08-10; lines corrected v4 after insertions, footer link corrected after testimonial rewrite): `#nis2` section `static/index.html:830-868`, badge + checklist of Art. 21 / A.6.3 / A.5.36 / Art. 32 / audit-ready; footer link `static/index.html:1074`.
3. Add a comparison page ("PhishDefend AI vs. KnowBe4 / SoSafe") — **completed v4** (verified 2026-08-10): on-page comparison section `static/index.html:672-756` (H2 `:676`) with 7-criteria table vs. KnowBe4 / SoSafe / Hoxhunt / gophish + alternatives paragraph.
4. Align all 11 FAQPage JSON-LD answers with the visible `<details>` answers — **done 2026-08-10** (re-verified: 11/11 question names and answers match, membership + per-item text check).
5. Refresh `meta keywords`, add `og:image`. *Open.*
6. Evaluate an English hreflang variant to capture the international head terms. *Open.*
7. Consider a statistics/benchmarks section with cited industry data (Bitkom, etc.) — **completed v3** (verified 2026-08-10; lines corrected v4 after insertions): Benchmarks & ROI section `static/index.html:758-788` (avg breach cost $140k, Bitkom 94 %/€200B, click-rate benchmarks 18–32 % → 4–8 %) + threat-stats cards in E-Mail-Sicherheit `:467-493`.
