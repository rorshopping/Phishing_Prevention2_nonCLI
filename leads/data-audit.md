# Data Integrity Audit — leads.csv vs contacts-v1.md

**Audited:** 2026-08-10 (refresh 3)
**Files:** `leads/leads.csv` (105 rows) → `leads/contacts-v1.md` (source of truth, incl. "Named Decision-Makers — Enrichment v1" and "Austria & Switzerland Enrichment" appendices)

---

## Verdict

**PASS for all 105 CSV rows.** Every email in `leads.csv` appears in `contacts-v1.md`, every row has a `source_url` matching the MD table for that email, and every status is valid (`collected`).

Findings F2, F3, F5, and F6 are **CLOSED**. Remaining open: F4 (progress.md stale — still shows leads.csv as 25 discard rows / Collected=46).

---

## 1. Row-by-row comparison (leads.csv → contacts-v1.md)

| Check | Result |
|---|---|
| CSV data rows | 105 |
| Unique emails in CSV | 105 (no duplicates) |
| Emails in CSV **not** found in contacts-v1.md | **0** |
| Emails in MD **not** in CSV | **0** |
| Rows with empty `source_url` | 0 |
| Rows whose `source_url` ≠ MD source URL for that email | **0** |
| Rows with invalid `status` | 0 |
| **Total mismatched/missing rows** | **0** |

- `status`: all 105 = `collected` (valid per `pipeline.md` §Stage mapping).
- `contact_role`: **82 × `role`**, **23 × `person`** — all rows now use the standard type keys.
- Coverage: 20 DE targets + 20 AT/CH targets = 40 companies, all matched to MD tables.

---

## 2. Prior findings status

| # | Finding | Status |
|---|---|---|
| F2 | 8 person emails missing from CSV (RVM ×7, Volk ×1) | ✅ **CLOSED** — imported (v1 enrichment) |
| F3 | coverage summary in contacts-v1.md said 46 vs 51 actual | ✅ **CLOSED** — summary updated to 51 (15/8/14/14) |
| F4 | progress.md stale (25 discard rows, Collected=46) | ⚠️ Still open |
| F5 | 46 AT/CH appendix emails not in CSV | ✅ **CLOSED** — agent 2 imported all 46 AT/CH rows; CSV is now 105 rows (51 DE + 8 v1 persons + 46 AT/CH) |
| F6 | `contact_role` free-text roles on imported person rows | ✅ **CLOSED** — 9 rows normalized to `person` |

---

## 3. F6 fix detail (refresh 3)

The following rows had free-text German role strings in `contact_role`; all normalized to the standard `person` type key so `verify_emails.py` and `pipeline.md` §Stage 3 "Role match" work consistently:

| Row (CSV) | Email | was `contact_role` |
|---|---|---|
| 53 | thomas.kalbacher@rvm.de | Geschäftsführer; Cyber-Risiko-Experte (Thomas Kalbacher) |
| 54 | oliver.scholl@rvm.de | Cyberversicherungs-Experte (Oliver Scholl) |
| 55 | roth@rvm.de | Ansprechpartner (Joachim Roth) |
| 56 | katharina.bastians@rvm.de | Member of Exec. Board (Katharina Bastians) |
| 57 | andreas.haberstock@rvm.de | Member of Exec. Board (Andreas Haberstock) |
| 58 | uwe.janicki@rvm.de | Management (Uwe Janicki) |
| 59 | manuel.soares@rvm.de | Management (Manuel Soares) |
| 60 | c.volk@volk-partner.de | Geschäftsführer (Claus Volk) |
| 106 | claus.widrig@assepro.com | Senior Advisor (Claus H. Widrig) |

> Note: the 9th row (claus.widrig@assepro.com) came from the AT/CH import and is included so the whole file uses the type-key convention. `contact_role` is now exclusively `role`/`person`; the person's role detail lives in the source URL context (or can be moved to a `name`/`role_detail` column if needed).

---

## 4. Findings summary (refresh 3)

| # | Severity | Finding |
|---|---|---|
| F1 | ✅ none | All 105 CSV emails exist in contacts-v1.md with matching `source_url` and valid `status=collected` |
| F2 | ✅ closed | 8 person emails imported |
| F3 | ✅ closed | coverage summary corrected to 51 |
| F5 | ✅ closed | 46 AT/CH emails imported; CSV = 105 rows |
| F6 | ✅ closed | all `contact_role` values normalized to `role`/`person` |
| F4 | Low | progress.md still shows leads.csv as stale/25 discard rows and Collected=46 |

---

## 5. Recommended actions

- [ ] Update `leads/progress.md`: leads.csv rebuilt (105 collected), Collected=105, cover both DE and AT/CH cohorts.
- [ ] (Optional) add `name`/`role_detail` columns to the CSV if the person role strings from the source pages are needed downstream.

---

## 6. Campaign-assignments audit (refresh 4, 2026-08-10)

**Files:** `leads/campaign-assignments.csv` (177 rows) vs `leads/leads.csv` (176 rows)

### Result: 59 of 176 leads assigned; 117 leads missing from assignments

| Check | Result |
|---|---|
| `campaign-assignments.csv` rows | 177 (= 59 emails × 3 touches D+0/D+3/D+7) |
| Unique emails in assignments | 59 |
| Assignments emails **not** in leads.csv (mismatched/extra) | **0** |
| leads.csv emails covered by assignments | **59 of 176** |
| **leads missing from assignments** | **117** |
| Field mismatches (company/website/source_url/status) for assigned emails | 0 |

### Covered (59) — leads.csv rows 2–60

Exactly the original **DE cohort + v1 person enrichments**: IT-HAUS ×3, ORBIT ×1, NetPlans ×9, Nösse, comito, SÜDVERS, RVM (1 role + 7 persons), RCU, Volk & Partner (4 role + 1 person), ASSON, Saegeling, MTR ×2, Jüttner, MEDITECH ×9, medika, Teubert ×4, WEKAL, Claaßen, MEZ ×4, Ebel ×4. All have a `template`, `cadence_slot` (Touch 1/2/3) and `pipeline_gate`.

### Missing (117) — not present in campaign-assignments.csv

- **AT/CH enrichment cohort (rows 61–106, 46 emails):** base-it, techbold ×4, SYSco, Intecso ×3, SEP IT, RVM Linz, LBUA, Schinner ×2, ASSEPRO ×11 (incl. persons Peyer, Latifi, Wirz, Blum, Forster, Büttiker, Mezera, Steinbrück, Stehrenberger, Hunold, Widrig), ARTUS Unicon, HABEL Medizintechnik ×7, ASKIN&CO, Kerkoc, Biomed ×2, Hierzer, Rottmund, Müller Martini ×2, Robert Ott, Sumec ×4 (incl. persons Schneeberger, Horvath, Schenk).
- **New ISP/hosting/utility batch (rows 107–177, 71 emails):** netcup ×6, tado ×5, roboception ×2, swu ×3, medatixx, hetzner ×9, sipgate ×2, easybell, all-inkl ×7, dogado ×7, manitu ×7, shopware ×3, plus extra netplans ×7, noesse ×1, comito ×1, suedvers ×3, rcu ×2, volk ×4, SYSco persons ×24, ASSEPRO (Leyla Iljazi), HABEL office.

> **Note:** several of the missing rows look like secondary/legal emails harvested from Imprints (e.g. `poststelle@lfdi.bwl.de`, `available@adr.org`, `schlichtungsstelle-tk@bnetza.de`, `jugendschutz@all-inkl.com`) or contain concatenated garbage in the local part (`info@noesse.deUmsatzsteuer`, `info@volk-versicherungsmakler.deRegistergerichtAmtsgericht`). These are not outreach targets and should be screened out (Stage 3) rather than assigned.

### Field note

The 24 `contact_role` mismatches detected in the assigned person rows (`leads.csv` says `person`, assignments carry the pre-normalization free-text role like `Management (Uwe Janicki)`) are **not email mismatches** — the F6 normalization was applied to `leads.csv` only; `campaign-assignments.csv` was not regenerated. Emails themselves all match.

### Recommended actions

- [ ] Regenerate `campaign-assignments.csv` from the full 176-row `leads.csv` (or confirm assignments intentionally cover only the DE cohort).
- [ ] Apply the same `contact_role=person` normalization to `campaign-assignments.csv` person rows.
- [ ] Screen the garbage/secondary emails above out of the CSV at Stage 3 before assignment.

---

## 7. Post-screening assignments audit (refresh 5, 2026-08-10)

**Files:** `leads/campaign-assignments.csv` (879 rows) and `leads/sendable-list.csv` (117 rows) vs `leads/leads.csv` (320 rows: **250 collected, 70 discard**).

### Verdict

| File | Discard leads present? | Verdict |
|---|---|---|
| `sendable-list.csv` | **0 of 70** | ✅ **PASS** — fully clean |
| `campaign-assignments.csv` | **70 of 70** | ❌ **FAIL** — every discard lead still assigned |

### sendable-list.csv — PASS

- 117 rows, 39 unique emails, all `status=verified`.
- **0** emails in the discard set; **0** emails unknown to leads.csv.
- All 39 unique emails map to the current 250 `collected` leads. No action needed.

### campaign-assignments.csv — FAIL

- 879 rows, 293 unique emails; every email exists in leads.csv (0 orphans).
- **All 70 discard leads remain assigned** → **210 rows** (3 touches each) reference a discard email.
- Pipeline gate on those rows: `EXCLUDED - third-part…` (87), `BLOCKED - non-decisi…` (87), `BLOCKED - generic ro…` (36) — i.e. the assignments file was generated before screening and still carries the now-discarded rows.
- `status` column on all 879 rows still reads `collected`; it was not re-derived from leads.csv.

### Recommended actions

- [x] Regenerate or filter `campaign-assignments.csv`: drop the 210 rows whose email is `discard` in leads.csv (leaves 669 rows / 223 unique collected emails). — **done (refresh 6)**
- [x] Re-sync `status` on remaining assignment rows to match leads.csv (`collected`). — **done (refresh 6)**
- [x] Keep `sendable-list.csv` as-is (already compliant). — **verified (refresh 6)**

---

## 8. Post-cleanup re-verification (refresh 6, 2026-08-10)

**Files:** `leads/campaign-assignments.csv` (669 rows) vs `leads/leads.csv` (322 rows: **252 collected, 70 discard** — +2 legal person-email imports since refresh 5).

### Verdict: ✅ PASS

| Check | Result |
|---|---|
| Assignments rows | 669 (= 223 unique collected emails × 3 touches) |
| Unique emails in assignments | 223 |
| Emails in DISCARD set still present | **0** ✅ |
| Emails unknown to leads.csv | **0** ✅ |
| `status` column | `collected` × 669 (aligned with leads.csv) |
| Touches per email | 3 (D+0 / D+3 / D+7) |

- The 210 discard rows (70 × 3) are fully removed; no orphan or stale emails remain.
- The 2 newly imported legal person emails (`loreth@asson.de`, `dieter.schaeublin@artus-gruppe.com` style) are `collected` leads and are not yet in the assignments file — expected, since the assignments were not regenerated from the full 252-collected set. Re-generate only if those persons should be sequenced.

---

## 9. CBH person-email assignment (refresh 7, 2026-08-10)

**Change:** appended 2 legal person leads to `leads/campaign-assignments.csv` — `n.siebertz@cbh.de` and `j.ristelhuber@cbh.de` (CBH Rechtsanwälte, Managing Partners) × 3 touches = **6 rows**.

- **Persona:** SMB owner (Managing Partner → MD default per `outreach-plan.md` §1 mapping rule).
- **Templates:** Template 1 - SMB Owner (initial + Follow-Up 1 + Follow-Up 2).
- **Cadence:** Touch 1 - D+0 / Touch 2 - D+3 / Touch 3 - D+7.
- **Pipeline gate:** `OK - person-level`.
- Persona source: `named person: {contact_role} -> SMB owner` (matches existing convention).

### Re-verification: ✅ PASS

| Check | Result |
|---|---|
| Assignments rows | 675 (= 225 unique collected emails × 3 touches) |
| Unique emails | 225 (223 prior + 2 CBH) |
| Emails in DISCARD set present | **0** ✅ |
| Emails unknown to leads.csv | **0** ✅ |
| `status` column | `collected` × 675 |
| Touches per email | 3 |
| CBH rows present | n.siebertz 3, j.ristelhuber 3 (SMB owner, correct cadence) ✅ |

---

## 10. CBH sendable assessment (refresh 8, 2026-08-10)

**Assessment:** `n.siebertz@cbh.de` and `j.ristelhuber@cbh.de` (CBH Rechtsanwälte Managing Partners) **qualify as sendable** — all pipeline gates pass:

| Gate | Check | Result |
|---|---|---|
| Person-level | `contact_role` = Managing Partner (named person) | ✅ |
| Verification | `verified` in `leads/verified.csv` | ✅ |
| Assignment | `OK - person-level`, Template 1, cadence D+0/D+3/D+7 | ✅ |
| Not discard | `collected` in `leads/leads.csv` (not in 70-discard set) | ✅ |
| Compliance (pre-send) | consent-log, suppression, footer, opt-out still required per §4 before each touch | ⚠️ operational gate, not a blocker |

**Action:** appended 6 rows to `leads/sendable-list.csv` (2 leads × 3 touches), `status=verified`, `pipeline_gate=OK - person-level`, persona SMB owner.

### Updated sendable count

| Metric | Before | After |
|---|---|---|
| Sendable rows | 117 | **123** |
| Unique sendable leads | 39 | **41** |
| Status | verified ×117 | verified ×123 |
| Gate | OK - person-level ×117 | OK - person-level ×123 |
| Personas | SMB owner 111 / IT manager 6 | SMB owner 117 / IT manager 6 |
| Discard leaks | 0 | 0 |

---

## 11. Send-artifact sync for CBH leads (refresh 9, 2026-08-10)

**Change:** appended the 2 CBH leads (`n.siebertz@cbh.de`, `j.ristelhuber@cbh.de`) to the send artifacts to match the 41-lead sendable set.

### `send-calendar.csv` — 117 → **123 rows** (41 unique leads)

| Lead | Cadence | Dates | Window | TZ | Template |
|---|---|---|---|---|---|
| n.siebertz@cbh.de | D+0 / D+3 / D+7 | 08-25 / 09-01 / 09-02 | 09:30–09:45 | CEST | Template 1 (initial / FU1 / FU2) |
| j.ristelhuber@cbh.de | D+0 / D+3 / D+7 | 08-26 / 09-01 / 09-02 | 09:50–10:05 | CEST | Template 1 (initial / FU1 / FU2) |

Dates follow `outreach-plan.md` §3 (Tue/Wed/Thu; D+3=08-28 Fri & 08-29 Sat shift to Tue 09-01; D+7=09-01 collision shifts to 09-02). Windows in the 09:30–11:30 morning band.

### `send-batch-1.csv` — 117 → **123 rows** (41 unique leads)

- IDs 118–123; `send_at` = calendar date + window (`+02:00`); Template 1 body with `{{FirstName}}` filled (Nadja / Johannes), footer + unsubscribe link intact; subjects match the SMB-owner persona (initial / "Nadja|Johannes, the fake-invoice test is free" / "Last note — free phishing test").

### ⚠️ `send-config-final.csv` — **needs matching update (not applied)**

Still 117 rows / 39 leads. Must be regenerated to add the 2 CBH leads (IDs 118–123) with:
- `country` = Germany, `werbung_prefix_required` = false, `rules_flag` = `DE: consent+impressum+optout`
- same `send_at` / template / subject / body as `send-batch-1.csv`

### Re-verification: ✅ PASS

| Check | Result |
|---|---|
| Calendar rows / unique | 123 / 41 ✅ |
| Batch rows / unique | 123 / 41 ✅ |
| CBH rows per file | 6 (2 × 3 touches) ✅ |
| Cadence D+0/D+3/D+7 | correct per lead ✅ |
| First-name substitution | applied, no `{FNAME}` leak ✅ |
| Discard / unknown emails | 0 / 0 ✅ |

---

## 12. Send artifact cross-file consistency check (refresh 10, 2026-08-10)

**Files:** `sendable-list.csv`, `send-calendar.csv`, `send-batch-1.csv`, `send-config-final.csv` — all post agent-4 123-row rebuild.

### Verdict: ✅ PASS

| Check | sendable-list | send-calendar | send-batch-1 | send-config-final |
|---|---|---|---|---|
| Rows | 123 | 123 | 123 | 123 |
| Unique leads | 41 | 41 | 41 | 41 |
| Touches per lead | 3 | 3 | 3 | 3 |
| Email set vs sendable-list | — | identical | identical | identical |

- **Calendar ↔ batch date alignment:** 0 mismatches (D+0/D+3/D+7 dates equal).
- **Batch ↔ config alignment:** 0 mismatches across `send_at` / `template` / `subject` for all 123 rows.
- **Config CBH rows correct:** Germany, `werbung_prefix=false`, `rules_flag=DE: consent+impressum+optout`, send_at matches calendar/batch.
- **Config distribution:** Germany 72, Switzerland 45, Austria 6 (werbung prefix only on the 6 AT rows).
- **Sendable:** 41 unique leads × 3 touches, personas SMB owner 117 / IT manager 6, all `verified`, all `OK - person-level`.

All four artifacts describe the **same 41-lead / 123-touch** send set — consistent with `leads\leads.csv` (252 collected at that snapshot) and the sendable assessment (§10).

---

## 13. Final data-integrity sweep (refresh 11, 2026-08-10)

**Scope:** `leads.csv` ↔ `verified.csv` reconciliation, consent-prep ↔ country-rules coverage, stale-figure check in this file.

### 13.1 leads.csv ↔ verified.csv — ⚠️ FAIL (verified.csv includes discard leads)

| Metric | Value |
|---|---|
| leads.csv rows | 373 (**303 collected**, 70 discard) |
| verified.csv rows | 373 |
| Email sets identical (no orphans either way) | ✅ |
| verified.csv rows referencing **discard** leads | **70 ❌** (status `verified` ×53, `role_gate` ×17) |
| Expected verified.csv rows (collected only) | 303 |
| Delta | **+70** |

> verified.csv should contain **only collected leads** (303 rows). It currently mirrors all 373 leads, re-marking the 70 discard emails as `verified`/`role_gate`. **Action required:** regenerate verified.csv from the 303 collected leads (exclude discards), same as refresh 6.

### 13.2 Consent-prep & country-rules coverage — ✅ PASS

| Check | Result |
|---|---|
| sendable unique leads | 41 |
| consent-log-prep.csv rows / unique | 41 / 41 |
| country-rules.csv rows / unique | 41 / 41 |
| Sendable emails missing from prep | **0** ✅ |
| Sendable emails missing from rules | **0** ✅ |
| Per-lead country match (prep ↔ rules) | **0 mismatches** ✅ |
| Country distribution | Germany 24, Switzerland 15, Austria 2 (both files) |
| Config country consistency (send-config-final) | 41 leads, 0 inconsistencies, matches rules ✅ |
| CBH leads country | Germany (prep + rules agree) ✅ |

### 13.3 Stale figures in data-audit.md

- §12 line "consistent with `leads\leads.csv` (252 collected)" — **corrected** to note it was a snapshot figure (252 → 303 collected today).
- Earlier sections (§7–§12) are point-in-time audit records and are left as-is; §1–§6 historical counts (105/176/46) remain as archived snapshots.

### Verdict

| Area | Result |
|---|---|
| leads.csv ↔ verified.csv counts | ❌ **FAIL** — verified.csv must drop the 70 discard rows (→ 303) |
| consent-log-prep covers 41 sendable, countries match country-rules | ✅ PASS |
| No stale figures in this file | ✅ PASS (after §12 correction) |

---

## 14. Verified.csv reconciliation — FAIL CLOSED (refresh 12, 2026-08-10)

**Agent 2 fix landed:** `verified.csv` regenerated to 303 rows, discards excluded.

### Re-run results

| Metric | Value |
|---|---|
| leads.csv rows | 373 (303 collected, 70 discard) |
| verified.csv rows | **303** |
| verified.csv status | `verified` 223 · `role_gate` 80 |
| Emails in verified.csv not in leads.csv | **0** ✅ |
| Collected leads missing from verified.csv | **0** ✅ |
| Discard leads present in verified.csv | **0** ✅ |
| Status-logic mismatches (GENERIC_ROLES rule) | **0** ✅ |
| verified rows == collected leads | 303 == 303 ✅ |

### Verdict: ✅ PASS

§13 FAIL (verified.csv containing 70 discard leads) is **CLOSED**. verified.csv now mirrors the 303 collected leads exactly — every collected lead is in verified.csv, no discard lead survives, no orphans, status mapping correct.
