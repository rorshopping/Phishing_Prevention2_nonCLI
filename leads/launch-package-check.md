# Launch Package Check — Batch 1 (final verification & sign-off)

**Checked:** 2026-08-10 · **Package:** batch-1 launch artifacts for 41 sendable leads / 123 touches.
**Verdict: ✅ Package is internally consistent — data defects: 0. 🔴 NOT launch-ready — blocked by 7 open items below.**

---

## 1. Package inventory & consistency matrix

| Artifact | Rows | Unique leads | Column set | Consistent with |
|---|---|---|---|---|
| `leads/send-config-final.csv` | 123 | 41 | 12 ✅ | — (baseline) |
| `leads/send-attribution.csv` | 123 | 41 | 15 ✅ | ids/emails/touches/send_at identical to config-final (0 mismatches); ids = 1..123 |
| `leads/consent-log-prep.csv` | 41 | 41 | 10 ✅ | email set == config-final (41/41) |
| `leads/country-rules.csv` | 41 | 41 | 7 ✅ | email set == config-final (41/41) |
| `leads/send-batch-1.csv` | 123 | 41 | 9 ✅ | id/email/subject/body identical to config-final (0 mismatches) |
| `leads/sendable-list.csv` | 123 | 41 | 12 ✅ | Touch-1 email set == config-final (41/41) |
| `leads/send-footer-values.csv` | 1 | — | 13 ✅ | present; **10 fields empty** (see B1) |

**Cross-checks (automated, all PASS):**

| Check | Result |
|---|---|
| Row counts (123/123/123/123) & 41 unique leads across all registries | ✅ PASS |
| Email sets identical (config = attribution = prep = rules = sendable) | ✅ PASS |
| `send-attribution` rows 1:1 with `send-config-final` (id, email, touch, send_at) | ✅ PASS |
| `send-batch-1` ↔ `send-config-final` subjects/bodies identical | ✅ PASS |
| `[Werbung]` on 6/6 Austrian rows; 0 spurious on DE/CH | ✅ PASS |
| Country + `rules_flag` values match `country-rules.csv` | ✅ PASS |
| 41 per-lead unsubscribe tokens present in attribution (uuid4, one per lead) | ✅ PASS |
| Docs present: `dry-run-batch1.md`, `launch-readiness.md`, `footer-merge.md`, `unsubscribe-spec.md`, `send-config-audit.md`, `org-entity-form.md` | ✅ PASS |

## 2. Expected open items (verified, by design — not defects)

- **Placeholders:** 13 fields × 123 bodies still unresolved (`{{LegalEntityName}}` … `{{UnsubscribeURL}}`, `{{ConsentSource}}`).
- **Consent:** 0/41 consent-prep rows carry any date/source/wording/recording (all empty).
- **Unsubscribe:** tokens exist in the registry but the `/unsubscribe` endpoint is not built and `{{UnsubscribeURL}}` is not yet replaced.

---

## 3. Final sign-off — exact remaining blockers before any send

| # | Blocker | Evidence | Blocked count | Resolver |
|---|---|---|---|---|
| **B1** | Legal entity data (Impressum) | `send-footer-values.csv` empty: LegalEntityName, StreetAddress, PostalCode, City, RegisterCourt, RegisterNo, VATId, ManagingDirector | all 123 touches | Founder / Legal counsel → fill `org-entity-form.md` |
| **B2** | DE/AT consent records | `consent-log.md` 0 records; `consent-log-prep.csv` 0/41 filled | 30 leads (24 DE + 2 AT + TISA-DE …) | Outreach staff / consent manager |
| **B3** | `/unsubscribe` endpoint | not built; `{{UnsubscribeURL}}` unresolved in bodies | all 123 | Engineering (`unsubscribe-spec.md`) |
| **B4** | Per-lead `{{ConsentSource}}` | empty in `send-footer-values.csv`; depends on B2 | all 123 | Outreach staff / consent manager |
| **B5** | Footer merge | 13 placeholder fields × 123 bodies | all 123 | Engineering / outreach (`footer-merge.md`) |
| **B6** | Sender infrastructure | no sending tool configured (tool-stack §4 researched only) | all 123 | Engineering / delivery |
| **B7** | Pass-2 verification | `verified.csv` = pass-1 only; no SMTP/catch-all on the 41 | 41 leads | Outreach / data |
| **B9** | Reply handling & logging | defined in `pipeline.md` §Stage 4, not wired | — | Outreach lead |

**Completed and NOT blockers:** B8 country rules (`[Werbung]` applied, `country`/`rules_flag` per lead — audit C3/C4 ✅) · dry-run procedure documented (`dry-run-batch1.md`) · attribution/token accounting (`send-attribution.csv`) · FirstName resolution (all 41 incl. Christoph Eggers).

## 4. Definition of launch (all must hold)

- [ ] B1 green → `send-footer-values.csv` 10 empty fields → 0
- [ ] B2/B4 green → `consent-log.md` records for all 30 DE/AT leads; `consent-prep.csv` filled; CH consent-first logged
- [ ] B3 green → `/unsubscribe` live; tokens from `send-attribution.csv` persisted to suppression store
- [ ] B5 green → `footer-merge.md` run; 0 `{{...}}` across 123 bodies (audit C6)
- [ ] B6/B7 green → tool configured + verified inboxes; pass-2 verification on 41 leads
- [ ] B9 green → reply routing wired
- [ ] `dry-run-batch1.md` executed with Steps 1–5 green (after B5, placeholder expectation = 0)
- [ ] `send-config-audit.md` C5 + C6 both green

**Sign-off: launch blocked — 8 open blockers (B1–B7, B9). Package data is clean; nothing further to fix at the artifact level before proceeding through the blockers in `launch-readiness.md`.**
