# Org Entity Form — Unlock the Footer Merge

Fill in every field below to complete the Compliance Footer in `leads/send-batch-1.csv` / `leads/send-config-final.csv`. Once complete, copy the values into `leads/send-footer-values.csv`, run the merge (B5), and re-run `leads/send-config-audit.md`.

**Source of truth for legal values = the published Impressum** (`static/impressum.html`, mirrored byte-for-byte to root `impressum.html` per AGENTS.md). After editing the Impressum, fill the CSV, then merge.

> ⚠️ Before any send: DE/AT consent still required per lead (`consent-log.md`, B2) — this form only unlocks the footer merge, not the consent gate.

---

## Fill-in form (13 fields)

| # | Field (`send-footer-values.csv` column) | Placeholder in email bodies | Current value | **Enter value here** | Impressum location (`static/impressum.html`) | Verified on Impressum |
|---|---|---|---|---|---|---|
| 1 | `LegalEntityName` | `{{LegalEntityName}}` | *(empty)* | `________________` | §Impressum, first placeholder block, line 98: `YOUR_COMPANY_NAME_HERE` | ☐ |
| 2 | `StreetAddress` | `{{StreetAddress}}` | *(empty)* | `________________` | Same block, line 99: `[Street & Number]` | ☐ |
| 3 | `PostalCode` | `{{PostalCode}}` | *(empty)* | `________________` | Same block, line 100: `[Postal Code, City, Germany]` (postal code part) | ☐ |
| 4 | `City` | `{{City}}` | *(empty)* | `________________` | Same block, line 100 (city part) | ☐ |
| 5 | `Country` | `{{Country}}` | `Germany` ✅ (prefilled) | `Germany` | Same block, line 100 ("Germany"); JSON-LD `addressCountry: DE` (line 34) | ☐ |
| 6 | `RegisterCourt` | `{{RegisterCourt}}` | *(empty)* | `________________` | §Handelsregister, line 111: `[Amtsgericht City]` | ☐ |
| 7 | `RegisterNo` | `{{RegisterNo}}` | *(empty)* | `________________` | §Handelsregister, line 112: `[HRB XXXXX]` | ☐ |
| 8 | `VATId` | `{{VATId}}` | *(empty)* | `________________` | §Umsatzsteuer-ID, line 118: `[DE XXX XXX XXX]` | ☐ |
| 9 | `ManagingDirector` | `{{ManagingDirector}}` | *(empty)* | `________________` | §Vertretungsberechtigt, line 123: `[Name of Managing Director]` | ☐ |
| 10 | `ImpressumURL` | `{{ImpressumURL}}` | `https://phishdefend-ai.vercel.app/impressum` ✅ | *(no change — canonical URL)* | URL of the Impressum page itself (`<link rel="canonical">`, static/index.html line 16) | ☐ |
| 11 | `PrivacyURL` | `{{PrivacyURL}}` | `https://phishdefend-ai.vercel.app/privacy` ✅ | *(no change — canonical URL)* | URL of the privacy page (no impressum §; verify the page exists) | ☐ |
| 12 | `UnsubscribeURL` | `{{UnsubscribeURL}}` | *(empty — **no endpoint exists**)* | `________________` | **No impressum §** — requires a new 1-click `/unsubscribe` endpoint + permanent suppression store (launch-readiness **B3**, owner: Engineering) | ☐ |
| 13 | `ConsentSource` | `{{ConsentSource}}` | *(empty — per-lead)* | *(per-lead, e.g. "phone consent, 2026-08-04, S. Weber")* | **No impressum §** — filled per lead from `consent-log.md` (launch-readiness **B2/B4**, owner: outreach/consent manager) | ☐ |

---

## After filling — do

- [ ] Copy fields 1–9 into `leads/send-footer-values.csv` (keep 5, 10, 11 as-is; 12/13 handled separately).
- [ ] Mirror the Impressum changes to root `impressum.html` (byte-for-byte, AGENTS.md sync list).
- [ ] Merge `send-footer-values.csv` + per-lead `ConsentSource` + `UnsubscribeURL` into all 117 bodies (launch-readiness B5).
- [ ] Re-run `leads/send-config-audit.md` — C6 must turn green (0 placeholders).
- [ ] Consent gate (C5) remains open until `consent-log.md` has a record per lead.
