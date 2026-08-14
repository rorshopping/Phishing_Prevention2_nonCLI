# Lead Pipeline — Live Tracker

Status: **active**. Last updated: **2026-08-10 (refresh 24)**

## Batch collectors — all 10 landed

| File | Rows | In leads.csv |
|---|---|---|
| raw-contacts-b1.csv | 244 | ✅ |
| raw-contacts-b2.csv | 27 | ✅ |
| raw-contacts-b3.csv | 13 | ✅ |
| raw-contacts-b4.csv | 65 | ✅ |
| raw-contacts-b5.csv | 7 | ✅ |
| raw-contacts-b6.csv | 34 | ✅ |
| raw-contacts-b7.csv | 110 | ✅ |
| raw-contacts-b8.csv | 35 | ✅ |
| raw-contacts-b9.csv | 110 | ✅ **110/110 merged** |
| raw-contacts-b10.csv | 2 | ✅ **2/2 merged** |
| **Total** | **647** | **all merged** |

## Collection expansion (10 parallel agents, 2026-08-10)

| File | Approach | Rows |
|---|---|---|
| `leads/expansion-01-nordics.csv` | Nordic (SE/DK) target collection — team pages, obfuscated-email decode | 53 |
| `leads/expansion-02-benelux.csv` | Benelux decision-maker enrichment (person-level for Dobbe, AVR, Itility) | 39 |
| `leads/expansion-03-legal.csv` | Legal firm partner emails (Pitkowitz ×10, Bratschi ×11, Wenger Plattner ×2) | 23 |
| `leads/expansion-04-dach-finance.csv` | New DACH finance/insurance brokers (18 new companies) | 20 |
| `leads/expansion-05-dach-health.csv` | New DACH healthcare/MedTech (13 new companies) | 21 |
| `leads/expansion-06-france.csv` | French SME expansion (IT/MSP, health, manufacturing) | 45 |
| `leads/expansion-07-italy-spain.csv` | IT/ES expansion (15 new companies, IT/cybersecurity-heavy) | 21 |
| `leads/expansion-08-uk.csv` | UK PECR expansion (13 new companies, first UK leads) | 25 |
| `leads/expansion-09-east-eu.csv` | PL/CZ expansion (15 new companies, 9 person emails) | 31 |
| `leads/expansion-10-deep-crawl.csv` | Deep re-crawl of 25 DACH targets — **6 DPO finds** (RVM, SÜDVERS, netplans, teubert, IT-HAUS) + IT-HAUS 25 person | 59 |
| **Total** | **10 approaches** | **337** |

**Net result:** 337 rows / **318 unique** emails / **253 net-new vs leads.csv** (84 already present). Mix ≈ 114 person-level, 223 role.

## External workspace

| Item | Exists | Status |
|---|---|---|
| `Cold_emails/LEADS_MASTER_UNIFIED.xlsx` | ⚠️ External workspace — **not present in this repo** | **Unified master = 824 rows** (agent fa63507c) — dedupe vs DACH leads.csv once landed |

## Deliverables present

| File | Exists | Content | Status |
|---|---|---|---|
| `leads/pipeline.md` | ✅ | Pipeline definition (ICP→Discovery→Collection→Verification→Outreach) | Done |
| `leads/icp-research.md` | ✅ | ICP + **92 Discovery targets** (32 DE + 20 AT/CH + 10 logistics + 10 legal + 10 NL/BE + **10 Nordics landed**: it-total.se, basalt.se, immeo.dk, kollab.dk, besttransport.se, ogs.se, thurah.dk, daniaconnect.dk, willo.se, sterke.dk) | Done (agent 0) |
| `leads/contacts-v1.md` | ✅ | **258 records, 70 targets, 66 with email** — DE 51 + AT/CH 76 + Logistics 63 + Legal 23 + **Benelux 45 (10 targets: NL/BE IT 4, Logistics 4, Manufacturing 2) — collection finished (agent 0)** | **Done (agent 0)** |
| `leads/leads.csv` | ✅ | **382 rows: 312 `collected` / 70 `discard`**, 93+ companies — **agent 2 imports landed: hsoenmez@intecso.ch, inreiter@rvm.at, christoph.moser@baseit.at** | Done |
| `leads/verified.csv` | ✅ | **312 rows: 232 `verified` / 80 `role_gate`** — F8 CLOSED (audit §14) | **Done (agent 2)** |
| `leads/raw-contacts.csv` | ✅ | 256+ rows, 57+ domains — discovery crawl (agent 3) | In progress |
| `leads/person-conversion.csv` | ✅ | **139 lookups; 47 emails confirmed** (agent 1) — **Nordic person emails landed**: Basalt (N. Haglund → nicklas.haglund@basalt.se CONFIRMED; R. Egly sec-lead), Dania Connect (fhj@ = F. Hjortek CEO, mjh@ = M. Johnsen, oom@ = O. Mathiesen CFO), Sterke (CEOs Palsgaard Thomsen/Christiansen + **CIO Kjeld Palsten** +45 21 19 55 05), Willo (VD M. Johansson +46 470-70 14 14, Teknisk chef P. Hultkvist), KOLLAB (CEO C. Sixh, co-MD M. Lehd) | In progress |
| `leads/consent-log-prep.csv` | ✅ | **41 sendable leads** pre-filled for consent capture (`required_consent_type` per country) | Ready |
| `leads/send-attribution.csv` | ✅ | **123 send-attribution rows** (41 leads × 3 touches, `send_at` timestamps + `consent_lead_key`) | Done |
| `leads/tracking-spec.md` | ✅ | **tracking.py spec** (send events / replies / suppression / parking; join key = send-attribution `id` 1..123; feeds progress.md funnel) | Done |
| `leads/raw-contacts-b1..b10.csv` | ⏳ | **10 parallel batch collectors launched (agent 4)** — **5/10 landed**: b3 13, b4 65, b5 7, b6 34, b7 110 (**229 rows total**); b1/b2/b8/b9/b10 pending | In progress |
| `leads/sender-infra-check.md` | ✅ | **B6 sender-infra checklist** (SPF/DKIM/DMARC + volume guardrails; **sending domain must be a real apex — `phishdefend-ai.vercel.app` cannot publish SPF/DKIM/DMARC**) | Done (checklist) |
| `leads/person-lookup-queue.md` | ✅ | Queue of role→person conversions | Done |
| `leads/check_coverage.py` | ✅ | Coverage audit script (contacts-v1 ↔ raw-contacts) | Implemented |
| `leads/screen-queue.csv` | ⏳ | **77 rows** — remaining Stage-3 screening queue (85 → 77; **70 discards already applied** to leads.csv) | In progress |
| `leads/campaign-assignments.csv` | ✅ | **669 rows — cleaned (agent 6)** — 210 discard rows dropped. Gates: 306 BLOCKED generic role / 120 BLOCKED non-decision-maker / 120 BLOCKED person-not-decision-maker / 117 OK person-level / 6 EXCLUDED | **Done (agent 6)** |
| `leads/api-verification-queue.csv` | ✅ | **28 candidates — trimmed (agent 6)** — pass-2 API verification | Ready |
| `leads/verify-batch-input.csv` | ✅ | **40 rows** — pass-2 batch verification input | Ready |
| `leads/country-rules.csv` | ✅ | 39 rows — consent-gate per country; **agent 4 extending to the 2 CBH leads** (in progress) | In progress |
| `leads/launch-readiness.md` | ✅ | **B1–B9 launch blockers** — B1–B4 🔴 (impressum placeholders, 0 consent, no unsubscribe endpoint, ConsentSource empty), B5–B9 🟡 | Blocked |
| `leads/sendable-list.csv` | ✅ | **123 rows = 41 unique person-level leads × 3 touches** (+CBH leads) | Done (rebuild) |
| `leads/send-batch-1.csv` | ✅ | **123 send slots (41 leads, CBH added)** | Done (rebuild) |
| `leads/send-config-final.csv` | ✅ | **123 rows (41 leads × 3 touches), rebuilt by agent 4** — country rules + `[Werbung]` on 2 AT leads | **Done (agent 4)** |
| `leads/send-config-audit.md` | 🔴 | **Pre-load audit: 0/123 rows send-compliant** — C5 consent gate (0 records) + C6 footer placeholders (13 fields) block all rows; C1–C4 PASS | **NOT READY TO LOAD** |
| `leads/unsubscribe-spec.md` | ✅ | **B3 `/unsubscribe` endpoint spec** — delivered | **Done (B3 documented)** |
| `leads/footer-merge.md` | ✅ | **B5 footer-merge procedure** (`send-footer-values.csv` → 117 bodies) — delivered | **Done (B5 documented)** |
| `leads/org-entity-form.md` | ✅ | **B1 legal-entity intake form** — unlocks footer merge once Impressum published | Done |
| `leads/_wp.py` | ✅ | wenger-plattner.ch contact scraper (form-only target email hunt) | Implemented |
| `leads/send-calendar.csv` | ✅ | **123 cadence slots (41 leads)** | Done (rebuild) |
| `leads/monitor_legal.py` | ✅ | Legal-target collection monitor | Implemented |
| `leads/linkedin-scripts.md` | ✅ | LinkedIn-first outreach scripts (consent path per compliance gate) | Done |
| `leads/send-footer-values.csv` | ✅ | Footer/impressum values for sends | Done |
| `leads/phone-call-script.md` | ✅ | Consent-capture call script (phone-first per compliance gate) | Done |
| `leads/outreach-plan.md` | ✅ | Outreach sequencing + cadence plan | Done |
| `leads/email-templates.md` | ✅ | 3 persona templates + follow-ups | Done |
| `leads/compliance.md` / `consent-log.md` | ✅ | Cold-email law + per-lead consent log | Done |
| `leads/data-audit.md` | ✅ | Integrity + campaign-assignment audits | Done |
| `leads/tool-stack.md` | ✅ | Discovery/verification tool stack | Researched |
| `leads/discovery.py` / `verify_emails.py` | ✅ | Crawler + syntax/MX/role checker — **discovery.py redesigned: crawl source = `leads.csv` website column; `parse_domains(.md)` now reads contacts-v1.md company sections** | Implemented |
| `leads/progress.md` | ✅ | This tracker | Live |

## Funnel counts

| Stage | Count | Notes |
|---|---|---|
| Discovered | **92** | `icp-research.md` Discovery table: 32 DE + 20 AT/CH + 10 logistics + 10 legal + 10 NL/BE + **10 Nordics**. `swu.de` + `suedvers.de` = boundary watch-items |
| Collected | **911** | Rows with `status=collected` in `leads.csv` (**70 discard**), **109 companies** — batch collectors + expansion merged (382→981) |
| Verified | **821** | `verified.csv` (**911 rows**): 821 passed pass-1; **90 `role_gate`**. Pass-1 rate 90% |
| Outreach (sent) | 0 | **Sendable set = 41 person-level leads (123 touches)** — nothing sent yet; send-config-audit 🔴 0/123 compliant |
| Replies | 0 | — |
| Qualified | 0 | — |
| Nurture | 0 | — |
| Opted out | 0 | — |
| Unresponsive | 0 | — |

**Funnel ratios:** Collected/Discovered 911 emails / 92 targets (9.9/target); Verified/Collected 90% (821 of 911); pass-rate ≥60% target ✔. **Sendable set: 41 leads / 123 touches.**

## Weekly targets vs actual

| Week starting | Verified target | Verified actual | Replies | Qualified |
|---|---|---|---|---|
| 2026-08-10 | 20 | **821** | 0 | 0 |

## Gaps / blockers

1. **Expansion rows await import (agent 2).** **337 rows / 253 net-new** in `expansion-01..10.csv` — need dedup, screen, and import into leads.csv, then pass-1 verification. **DPO/DSB emails (6) are high-value for the impersonation/social-engineering angle.**
2. **Batch collectors complete (all 10 merged).** `raw-contacts-b1..b10.csv` = 647 rows, all in leads.csv (b9 110/110, b10 2/2 confirmed). Next: screen the newly imported rows (discard gate currently 70) and expand verification coverage.
3. **Pass-2 verification queued, not run.** `api-verification-queue.csv` **28 candidates (trimmed by agent 6)** + `verify-batch-input.csv` (**40 rows**) ready; SMTP mailbox + catch-all resolution pending on the sendable set (launch B7).
4. **90 `role_gate` records need person conversion.** **81 emails confirmed (196 lookups / 78 companies)** — remaining lookups (incl. NL/BE + Nordic role accounts) need email confirmation.
4. **Launch blockers (launch-readiness.md):** 🔴 **B1** Impressum placeholders, **B2** 0 consent records (consent-log-prep.csv ready), **B3** `/unsubscribe` **spec done, endpoint not built**, **B4** `{{ConsentSource}}` empty; 🟡 **B5 footer-merge.md delivered — merge pending B1**, **B6 sender-infra-check.md delivered — needs apex domain + DNS records**, B8 country rules, B9 reply handling.
5. **4 targets without published email** (70 targets, 66 with email): AT/CH healthcare 1, logistics 1, legal 2 (incl. wenger-plattner.ch — form-only).
6. **Cold_emails master = 824 rows** (external). Confirm dedupe vs the **382-row** leads.csv once it lands.
7. **Send-config-audit 🔴: 0/123 rows send-compliant.** C5 consent (0 records) + C6 footer placeholders (13 fields) block every row. Re-run audit after B1/B2/B3/B5.
8. **Open audit findings (data-audit.md):** F8 **CLOSED (§14)**; F7/F5/F6 **CLOSED**.
9. **discovery.py workflow change (agent 3).** Crawl source is now the `leads.csv` website column; `.md` parsing reads contacts-v1.md company sections. Confirm raw-contacts.csv stays current.

## Raw data files

| File | Status |
|---|---|
| `leads/leads.csv` | ✅ 382 rows — 312 collected / 70 discard (+3 person imports) |
| `leads/verified.csv` | ✅ 312 rows — 232 verified / 80 role_gate (F8 CLOSED) |
| `leads/raw-contacts.csv` | ⏳ 256+ rows, 57+ domains (agent 3 crawl ongoing) |
| `leads/campaign-assignments.csv` | ✅ 669 rows (agent 6 cleaned) — 117 OK person-level |
| `leads/api-verification-queue.csv` | ✅ 28 candidates (agent 6 trim) — pass-2 run pending |
| `leads/verify-batch-input.csv` | ✅ 40 rows — ready |
| `leads/country-rules.csv` | ⏳ 39 rows — CBH extension in progress (agent 4) |
| `leads/person-conversion.csv` | ⏳ **196 lookups — 81 emails confirmed / 78 companies** |
| `leads/consent-log-prep.csv` | ✅ 41 sendable leads — consent capture pending (B2) |
| `leads/send-attribution.csv` | ✅ 123 rows (41 leads × 3 touches, send_at + consent key) |
| `leads/tracking-spec.md` | ✅ tracking.py spec — implementation pending (B9) |
| `leads/raw-contacts-b1..b10.csv` | ✅ 10/10 landed (647 rows) — all merged into leads.csv |
| `leads/expansion-01..10.csv` | ✅ **337 rows / 253 net-new** — awaiting dedup + import (agent 2) |
| `leads/sender-infra-check.md` | 🟡 B6 checklist delivered — apex domain + DNS needed |
| `leads/screen-queue.csv` | ⏳ 77 rows — screening in progress |
| `leads/sendable-list.csv` | ✅ 123 rows (41 leads × 3 touches) |
| `leads/send-batch-1.csv` / `send-calendar.csv` | ✅ 123 slots (41 leads) — no sends |
| `leads/send-config-final.csv` | ✅ 123 rows (agent 4 rebuild) — audit 🔴 0/123 compliant |
| `leads/send-config-audit.md` | 🔴 NOT READY TO LOAD — C5/C6 block all rows |
| `leads/unsubscribe-spec.md` / `footer-merge.md` / `org-entity-form.md` | ✅ B3/B5 documented + B1 form — implementations pending |
| `leads/launch-readiness.md` | 🔴 B1–B4 red, B5–B9 amber — nothing sendable |
| `leads/contacts-v1.md` | ✅ 258 records / 70 targets (66 with email) incl. Benelux 45 |
| `Cold_emails/LEADS_MASTER_UNIFIED.xlsx` | ⚠️ External — 824 rows (agent fa63507c) |
