# Email Discovery & Verification Tool Stack — B2B Cold Outreach (DACH)

*Research compiled 2026-08-10. Pricing verified against vendor sites / third-party benchmarks July–Aug 2026. This is research, not legal advice.*

Context: this stack feeds the PhishDefend AI cold-outreach pipeline (`leads/email-templates.md`) targeting SMB/IT/HR decision makers in Germany, Austria, and Switzerland. Findings first, then the comparison, then the recommendation.

---

## TL;DR

- **Discovery:** Hunter.io. Best public-source transparency, EU hosting (GCP Belgium), and the higher verified find rate in independent head-to-heads (37.6% vs Snov.io's 20.1%).
- **Pre-filter:** MX-check (mxcheck.dev) — free 3,000 req/mo, discards syntax-invalid / disposable / dead-MX addresses before verification credits are spent. It is **not** a deliverability-grade verifier (no SMTP mailbox check).
- **Verification (pass 1, bulk):** MillionVerifier — $37/10K, refunds risky/unknown credits, credits never expire.
- **Verification (pass 2, DACH decision makers):** Bouncer — EU-hosted (AWS Frankfurt), GDPR-by-design, best catch-all resolution. If a ZoomInfo/US transfer is acceptable, NeverBounce is the in-ecosystem alternative.
- **Do not default to Snov.io** for DACH: low verified find rate, shared find+verify credit pool (double-charges), and weak coverage of SMB/non-English markets.
- **Legal gate that overrides all tooling:** in DE/AT/CH, unsolicited marketing email requires **prior express consent** — there is no B2B exemption. Verification tools clean your data; they do not legalise the send.

---

## 1. Legal reality check — cold email in DACH (the gate)

All three markets implement the ePrivacy Directive's "prior consent" rule for marketing email. German UWG §7(2) Nr. 3, Austrian TKG 2021 §174, and Swiss UWG Art. 3(1)(o) apply **identically to B2B and B2C recipients** — a business address is not a free pass. German courts have confirmed generic corporate addresses (info@, kontakt@) are protected too (OLG Munich, 29 U 857/12).

| Country | Statute | Rule for marketing email | B2B exemption? | Existing-customer exception | Fines / risk |
|---|---|---|---|---|---|
| **DE** | UWG §7(2) Nr. 3 + §25 TDDDG | Prior express consent required | **No** | Yes, §7(3), 5 strict conditions (prior sale, similar products only, no objection, opt-out every send, clear sender) | UWG up to €300,000; GDPR up to €20M or 4% global turnover; Abmahnung/cease-and-desist costs |
| **AT** | TKG 2021 §174 | Prior express consent required | **No** | Yes, §174(4) (same/similar products, opt-out, not on RTR Robinson/ECG list) | Up to €50,000 administrative fines; civil cease-and-desist |
| **CH** | UWG Art. 3(1)(o) + FMG | Consent required for mass advertising | **No** (UCA applies to individuals and corporations) | Yes, existing-customer exception (similar products, opt-out offered) | revFADP: **no corporate fines**, but criminal sanctions vs natural persons up to **CHF 250,000** (Art. 60–63); civil claims |

Key 2025–2026 rulings and clarifications:

- **AG Düsseldorf, 20 Nov 2025 (23 C 120/25):** a LinkedIn connection does not constitute consent to email advertising; an unsubscribe link does not cure a missing opt-in. Publicly discoverable business addresses are not a licence to send.
- **CJEU C-654-23 (Nov 2025):** where an email is sent for direct-marketing purposes under ePrivacy Art. 13(2), the GDPR Art. 6 legal-basis conditions do not apply (Art. 95 GDPR — ePrivacy acts as *lex specialis*). The same case confirmed a **free-trial/freemium registration qualifies as a "sale"** for the existing-customer soft opt-in.
- **Data processing layer (separate from marketing law):** building and enriching the prospect list is GDPR processing. Document a legitimate-interest assessment (Art. 6(1)(f), EDPB Guidelines 1/2024 three-step test) in DE/AT; in CH a balancing test under revFADP Art. 31. Art. 14 GDPR requires disclosing the **source** of the data to the data subject — this is why a discovery tool that exposes its public sources (Hunter) is a compliance asset.
- **Compliant outreach pattern** in practice: phone-first or LinkedIn-first, log consent (timestamp, scope, source), *then* email. See `leads/email-templates.md` for the templates; the reply-to "unsubscribe" line plus a suppression log is mandatory, not optional.

Consequence for tooling: accuracy isn't just a deliverability metric. Verified, correctly-sourced, EU-resident data reduces the risk surface for the whole operation.

---

## 2. Comparison table (pricing verified Aug 2026)

| | **Hunter.io** | **Snov.io** | **NeverBounce** | **MillionVerifier** | **MX-check (mxcheck.dev)** |
|---|---|---|---|---|---|
| **Category** | Discovery + verify + light outreach | All-in-one (find, verify, send, warm-up, CRM) | Verification only | Verification only (bulk) | Lightweight pre-filter API |
| **Free tier** | 50 credits/mo | 50 credits (Trial) | 1,000 free verifications (trial) | Free trial credits | 3,000 req/mo (100/day) |
| **Entry paid** | $49/mo ($34 annual), 2,000 credits | ~$39/mo (~$30 annual), 1,000 credits | PAYG $0.008/email (~$80/10K) | $37 per 10,000 (one-time) | $9/mo for 5,000 req |
| **Mid tier** | Growth $149/mo ($104 annual), 10,000 credits | Pro S $99/mo ($75 annual), 5,000 credits | $0.005 @10K–100K; Sync $10–$149/mo | $97/50K, $149/100K | $29/mo for 50,000 req |
| **High volume** | Scale $299/mo ($209 annual), 25,000 credits; Enterprise custom | Pro M $189/$142, Pro L $369/$277, Ultra custom | $0.004 @100K–250K; $0.003 @250K–1M | $349/500K, $549/1M | n/a (call for higher) |
| **Credit model** | 1 = 1 email found; 0.5 = 1 verified; domain search ≤10 emails/credit; **1.5 credits per find+verify lead** | **Shared pool**: 1 credit = 1 find OR 1 verify (2 credits per find+verify lead) | PAYG per verification, volume discounts | PAYG, credits **never expire**; refunds on risky/unknown/catch-all | per request |
| **SMTP mailbox check** | Yes (via sub-processor) | Yes (7-tier) | Yes | Yes | **No** — syntax/MX/disposable/typo only |
| **Data residency** | GCP **Belgium**; US sub-processors w/ SCCs | Not published (multi-jurisdiction) | US (ZoomInfo) | US (note: operates Hunter's verification via EU entity GBD Consulting, HU) | Not published |
| **Best for** | Public-web-sourced finding w/ source disclosure | Budget all-in-one, small teams | Enterprise list cleaning, ZoomInfo ecosystem | Cheap bulk first-pass cleaning | Zero-cost pre-filter in a pipeline |

### Discovery: Hunter vs Snov.io — verified find rate matters

Independent benchmark (Anymail Finder, 5,000 fresh contacts incl. DE/France):

- **Hunter: 37.6% verified find rate**
- **Snov.io: 20.1% verified find rate** (≈1 in 5 lookups yields a confirmed-valid address)

Hunter's database is smaller than Snov's 500M+ claims, but returns far more *usable* addresses. Snov.io's "98% accuracy" claim measures deliverability of emails it returns — not the rate at which a lookup produces an address. Both tools charge per find; Snov.io additionally charges again to verify.

### Verification accuracy — independent benchmarks

| Tool | Claimed | Independent real-world accuracy | Catch-all handling | Notes |
|---|---|---|---|---|
| NeverBounce | 97–99% | 96.9% (LeadMagic, Feb 2026); 95.9% (Overloop, May 2026) | Conservative — most catch-alls flagged risky/unknown | No spam-trap detection; no catch-all scoring; fastest bulk (10K in 18 min) |
| MillionVerifier | 99%+ | 95.8% (LeadMagic); 95.0% (Overloop); 98.9% (dev.to benchmark) | Basic flag, **no scoring**; credits for catch-all/risky refunded | Cheapest at scale; refunds on verified-good bounces (deliverability guarantee) |
| Bouncer (comparison) | 98%+ | 96.8% (Overloop); EU-GDPR flagship | Separate verdict + risk score; detects catch-alls on Google/Microsoft platforms | EU-hosted (AWS Frankfurt), anonymised, 60-day retention |
| Hunter (verify) | — | 94.7% (Overloop) | accept_all verdict w/ confidence | Verification is secondary to finding |
| Snov.io (verify) | 98% | 93.5% (Overloop); finder 75–85% in practice | 7-tier incl. catch-all, greylisting bypass | Verification is the strongest part of the platform |
| MX-check | — | n/a — **no mailbox-level check** | n/a | Catches syntax/format/typo/disposable/dead-MX only |

Takeaway for budgets: real-world accuracy on B2B lists runs 4–8 points **below** marketing claims. Plan around ~95–96% and cascade high-stakes addresses through a second verifier.

---

## 3. GDPR implications per tool (DACH lens)

After **Schrems II (2020)** invalidated Privacy Shield, transferring personal data to US-hosted processors requires SCCs plus a transfer impact assessment (TIA) — and post-*Schrems III* scrutiny, a US parent with EU servers still exposes a legal "route into the US". For DACH clients, EU-processed verification materially de-risks vendor assessments.

| Tool | GDPR posture | Notes for DACH |
|---|---|---|
| **Hunter.io** | Servers in Belgium (GCP eu-west-1); DPA + SCCs with US sub-processors; data removal / source disclosure for data subjects | Strongest transparency story of the five: per-lead public-source disclosure supports Art. 14; 6-month source expiry; verifications actually run via MillionVerifier's EU entity (GBD Consulting, Hungary) |
| **Snov.io** | GDPR-compliant claims; no published EU-only residency | LinkedIn automation add-on itself raises LinkedIn-ToS risk; source provenance for scraped addresses is harder to evidence |
| **NeverBounce** | US-based (ZoomInfo since 2019); DPA available | B2C-leaning (weaker on Yahoo); conservative catch-all verdicts shrink usable DACH B2B lists; US transfer overhead |
| **MillionVerifier** | US-based; EU sub-processor relationship (Hunter) | Fine for *format-level* hygiene; minimal documentation burden if used only as a pre-clean of non-sensitive lists |
| **MX-check** | Lightweight API; low data footprint | Processes only email strings; useful as a "no-PII-retained" pre-filter, but confirm retention in any DPA |

### GDPR angle no tool solves: the data *source*

German data-protection authorities treat address provenance as central (BDSG/GDPR: purpose limitation + Art. 14 transparency + accountability). Publicly listed addresses (Hunter's model, with per-lead source URLs) are the defensible source class. Bought or scraped lists without verifiable provenance are the high-risk class. Prefer tools whose results let you show *where* an address came from.

---

## 4. Recommended stack

**Staged pipeline (cost-optimised, DACH-compliant):**

```
1. Hunter.io (Starter $34 or Growth $104, annual) ──► find verified leads w/ source URLs
2. MX-check (free 3,000/mo) ──► discard syntax/typo/disposable/dead-MX before spending credits
3. MillionVerifier ($37/10K, one-time) ──► cheap bulk pass: drop invalids
4. Bouncer (EU-hosted, PAYG ~$8/1K) ──► resolve catch-all/risky on high-value DACH targets
   ──► store + consent log (timestamp, source URL, opt-out state) in CRM
```

Why this stack:

1. **Hunter first** — highest verified find rate in the head-to-head, per-lead public-source disclosure (Art. 14), EU hosting, clean API/MCP, and a genuine free tier to validate against your ICP before committing.
2. **MX-check as a free gate** — its limitations are a feature here: it filters junk *before* paid verification credits are burned. Latency <10 ms suits a pipeline stage.
3. **MillionVerifier for bulk** — $37 covers 10K addresses with refunds on inconclusive results and non-expiring credits; ideal for campaign-based (not continuous) prospecting.
4. **Bouncer (or NeverBounce) for the final, small, high-value list** — the only layer where catch-all decision-makers at big companies get a confident verdict. Bouncer is the DACH pick (EU-only processing, anonymised, 60-day retention); NeverBounce if you're already inside ZoomInfo and accept the US transfer assessment.

**Why not Snov.io as the primary:** 20.1% verified find rate, double credit-charge for find+verify, spotty SMB/non-English coverage, and warm-up paywalled behind Pro — the effective entry price is ~$75/mo, not ~$30. Keep it in mind only as a cheap all-in-one for very small test volumes.

### Indicative monthly cost (≈1,000 verified DACH leads)

| Layer | Tool | Cost |
|---|---|---|
| Discovery | Hunter Starter (annual) | ~$34/mo |
| Pre-filter | MX-check free tier | $0 |
| Bulk verify | MillionVerifier 10K pack | ~$4/mo amortised ($37 one-time) |
| Final verify (top ~500) | Bouncer PAYG | ~$40/mo |
| **Total** | | **~$80/mo** (≈$0.08 per verified lead) |

Scale-up path: Hunter Growth ($104/mo, 10K credits) + MillionVerifier 50K pack ($97). Never exceed ~1,000 sends/mo per warmed inbox; keep bounce rate <2% (Gmail/Yahoo 2024 sender rules).

---

## 5. DACH campaign compliance checklist

- [ ] **Consent gate:** for DE/AT, no marketing email to a cold contact. Use phone/LinkedIn-first, log consent, then email (see `leads/email-templates.md`).
- [ ] **Documented LIA** (Art. 6(1)(f), EDPB 1/2024 three-step test) for list building/processing; CH equivalent under revFADP Art. 31.
- [ ] **Source provenance:** store Hunter's source URLs per lead; honour the 6-month freshness/removal semantics.
- [ ] **Art. 14 notice** when data wasn't collected from the subject: state source, purpose, retention, rights.
- [ ] **Every email:** opt-out (one-click + reply-to line), full Impressum, clear sender identity, advertising flagged in subject (AT).
- [ ] **Suppression lists:** honour the Austrian RTR Robinson/ECG list and Swiss/existing-customer opt-outs; sync opt-outs across all campaigns.
- [ ] **Verification:** two-pass (bulk → catch-all resolution); keep bounces <2%.
- [ ] **DPAs** on file with every processor in the chain (Hunter, MillionVerifier, Bouncer, ESP).

---

## 6. Sources

- Hunter pricing page & help centre (GDPR/data residency, sub-processors, DPA) — hunter.io/pricing, help.hunter.io
- Snov.io pricing & knowledge base — snov.io/pricing
- NeverBounce reviews & pricing — SyncGTM (Jun 2026), Clay guide (Jun 2026), LeadMagic benchmark (Feb 2026)
- MillionVerifier pricing & reviews — PuzzleInbox (Apr 2026), LeadMagic, Overloop (May 2026)
- MX-check API — mxcheck.dev
- Overloop email-verification benchmark & DE cold-email guide (May 2026)
- DLA Piper Data Protection Laws of the World — DE/AT/CH electronic marketing
- AG Düsseldorf 23 C 120/25 (Nov 2025); CJEU C-654-23 (Nov 2025); WKO Austria TKG guidance
