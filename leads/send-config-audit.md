# Send Config Audit — Pre-Load Validation

**Audited:** 2026-08-10 (refresh 2 — CBH leads added) · **Input:** `leads/send-config-final.csv` (123 rows) cross-checked against `leads/send-batch-1.csv`, `leads/country-rules.csv`, and the consent gate (`leads/consent-log.md`).
**Verdict: 🔴 NOT READY TO LOAD** — **0 of 123 rows are send-compliant.** Consent and footer values block every row.

---

## Summary

| # | Check | Rows checked | Result | Detail |
|---|---|---|---|---|
| C1 | Row integrity (config vs batch) | 123 | ✅ PASS | All shared fields (`id`, `company`, `lead_name`, `email`, `touch`, `send_at`, `template`, `subject`, `body`) identical between `send-config-final.csv` and `send-batch-1.csv`; 123 = 123 |
| C2 | Country mapping coverage | 123 | ✅ PASS | Every email maps to a country in `country-rules.csv`; 41 unique leads (incl. CBH `n.siebertz@cbh.de`, `j.ristelhuber@cbh.de`) ↔ 41 rule rows; 0 missing |
| C3 | `[Werbung]` prefix applied (AT) | 6 | ✅ PASS | All 6 Austrian rows (`markus.schrott@tisa.at` ×3, `p.wurm@sysco.at` ×3) start with `[Werbung] ` |
| C4 | No spurious `[Werbung]` (DE/CH) | 117 | ✅ PASS | 0 non-Austrian rows carry the prefix (incl. CBH DE rows) |
| C5 | **Consent gate** | 123 | 🔴 **FAIL (all)** | **0 consent records** in `consent-log.md`. DE/AT: no B2B exemption — send unlawful without logged consent (UWG §7(2), TKG §174(3)). CH: consent-first standard in practice. All 41 leads / 123 rows blocked |
| C6 | **Footer placeholders resolved** | 123 | 🔴 **FAIL (all)** | **13 placeholder fields remain** in every body (`send-footer-values.csv` values not yet merged — `launch-readiness.md` B5) |

**Send-compliant rows: 0 / 123.**

---

## C6 detail — unresolved footer fields (×117 bodies)

`{{LegalEntityName}}`, `{{StreetAddress}}`, `{{PostalCode}}`, `{{City}}`, `{{Country}}`, `{{RegisterCourt}}`, `{{RegisterNo}}`, `{{VATId}}`, `{{ManagingDirector}}`, `{{ImpressumURL}}`, `{{PrivacyURL}}`, `{{UnsubscribeURL}}`, `{{ConsentSource}}`

- `send-footer-values.csv` already provides values for `Country`, `ImpressumURL`, `PrivacyURL` — these are not yet inlined into the bodies (merge pending).
- `LegalEntityName`, `StreetAddress`, `PostalCode`, `City`, `RegisterCourt`, `RegisterNo`, `VATId`, `ManagingDirector` are **empty** in `send-footer-values.csv` (Impressum still placeholder — `launch-readiness.md` B1).
- `{{UnsubscribeURL}}` has no endpoint (B3). `{{ConsentSource}}` is per-lead and depends on C5 (B2/B4).

---

## Compliance status by country

| Country | Rows | Consent gate | `[Werbung]` | Footer | Send-compliant |
|---|---|---|---|---|---|
| Germany | 72 | 🔴 no consent logged | n/a (not required) | 🔴 placeholders | **0** |
| Austria | 6 | 🔴 no consent logged | ✅ applied | 🔴 placeholders | **0** |
| Switzerland | 45 | 🔴 consent-first practice not satisfied | n/a (not required) | 🔴 placeholders | **0** |

---

## Blockers to clear before load (from `launch-readiness.md`)

1. **B1** legal entity on Impressum → fill 8 empty fields in `send-footer-values.csv`.
2. **B2/B4** capture + log consent per lead → `consent-log.md` records → per-lead `{{ConsentSource}}`.
3. **B3** build + test `/unsubscribe` endpoint → working `{{UnsubscribeURL}}`.
4. **B5** merge footer values + consent source into all 117 bodies; re-scan for zero `{{...}}`.
5. Re-run this audit (C5, C6 must turn green) before loading `send-config-final.csv` into the sending tool.

## Actions already green (do not regress)

- ✅ `[Werbung]` prefix correct for Austrian leads (C3) and absent elsewhere (C4)
- ✅ Country + rules flags (`country`, `werbung_prefix_required`, `rules_flag`) consistent with `country-rules.csv`
- ✅ No `{{FirstName}}` placeholders remain (resolved previously — incl. Christoph Eggers)
