# Unsubscribe Endpoint Spec — `/unsubscribe`

Technical spec for blocker **B3** (`leads/launch-readiness.md`): the working opt-out that fills `{{UnsubscribeURL}}` in every email of `leads/send-config-final.csv` (117 bodies). Requirements per `leads/compliance.md` §7 (global checklist) and `leads/consent-log.md` (revocation workflow). Target runtime: the existing FastAPI app (`src/main.py`) + SQLAlchemy DB (`src/database/models.py`).

---

## 1. URL format (per lead)

`{{UnsubscribeURL}}` is filled **per lead** with a unique, unguessable token:

```
https://phishdefend-ai.vercel.app/unsubscribe?token=<uuid4>
```

- **Token:** `uuid.uuid4()` — cryptographically random, single-use-per-lead, never derived from the email.
- **Per lead = per address:** one token per unique `email` in `sendable-list.csv`, generated at batch-prep time and stored in the suppression store (token ↔ email).
- **Placement:** replaces `{{UnsubscribeURL}}` in the body **and** the two footer links of that lead's 3 touches (Day 0 / Day 3 / Day 7 share the same token — opt-out at any touch suppresses all later touches).
- Alternative path style accepted: `/unsubscribe/{token}` (same behavior); the query-string form is preferred for email-client link sanitization.

## 2. Endpoint behavior

| Route | Method | Behavior |
|---|---|---|
| `/unsubscribe` | `GET ?token=<uuid>` | Processes the opt-out immediately (idempotent), renders confirmation page. 200 with HTML confirmation. |
| `/unsubscribe` | `POST {token}` | Same processing (supports form/JS clients); optional button on the confirmation page. |
| `/unsubscribe` | `GET/POST` invalid/missing/unknown token | 200 + "link invalid or already processed" page. **No email address echoed, no error leak** (token is a capability; do not reveal what it unlocks). |
| `/unsubscribe/health` | `GET` | liveness for the store (optional). |

**Processing steps (atomic, idempotent):**
1. Look up `token` → `email` in `suppression` store. Unknown → confirmation page (no write).
2. If not yet suppressed: insert suppression row (`email`, `token`, `opted_out_at=now`, `source='unsubscribe_link'`, `send_tool_reference=<batch id>`).
3. Update the lead's consent-log record: set REVOCATION block — `revoked on <date>`, `DNC=true` (`leads/consent-log.md` §2 template).
4. Return confirmation page: "Your address has been unsubscribed. You will receive no further marketing email from PhishDefend AI."

## 3. Suppression store (schema)

```sql
CREATE TABLE suppression (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    email       TEXT NOT NULL UNIQUE,          -- normalized lowercase
    token       TEXT NOT NULL UNIQUE,          -- uuid4 capability
    opted_out_at DATETIME NOT NULL,            -- when processed (source of truth for ≤10-day rule)
    source      TEXT NOT NULL DEFAULT 'unsubscribe_link',  -- channel of opt-out
    batch_id    TEXT,                          -- send-batch reference (e.g. send-batch-1)
    send_log    TEXT,                          -- ids of touches sent before opt-out (audit)
    created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_suppression_email ON suppression(email);
```

- **Permanent:** rows are never deleted, never re-marketed, never sold/transferred (`compliance.md` §7 "Suppression list maintained and re-used; no re-marketing after objection").
- **Normalization:** store lowercase; suppress variants (`FirstName.LastName` vs `firstname.lastname`).
- **Re-subscribe:** not supported via this endpoint. A new mailing requires fresh, logged consent (new consent-log record), not a token reset.

## 4. One-click, no-login

- **No authentication, no login, no fee** — the token is the credential.
- **No extra steps:** no re-typing email, no phone/post, no multi-step wizard, no CAPTCHA (`compliance.md` US §5 #6: "no extra steps beyond reply-email or one web page").
- GET processes the opt-out **immediately** (email clients only follow GET links reliably). The confirmation page is purely informational; the state change happens on the click itself.
- Idempotent: repeated clicks on the same token return the same confirmation and do not error.

## 5. Honoring within 10 business days

- **Immediate suppression** on click (`opted_out_at` = now) — comfortably inside the ≤10-business-day requirement (US CAN-SPAM 16 CFR §316.5; EU/CH "immediate/short, suppress permanently", `compliance.md` §7).
- **Send-time guard (defense in depth):** the sending tool must query `suppression` for every address immediately before each touch (outreach-plan §4 gate #2). A lead suppressed at any point cancels its remaining Day-3/Day-7 slots even if the token was clicked after the last send.
- **Audit trail:** `opted_out_at` + `send_log` let a reviewer confirm no send occurred after suppression (consent-log §4 quarterly audit).

## 6. Consent-log integration

- **On opt-out:** the REVOCATION block of the lead's record in `leads/consent-log.md` is completed — `Revoked on <date> → suppression list + DNC` (`consent-log.md` §2).
- **On every subsequent send attempt:** consent-log §3 step 6 verification must find no `DNC`/revocation; combined with §4.1 (suppression store) this is the double gate.
- **ECG/Robinson list (AT):** separate mandatory check (`eintragen@ecg.rtr.at`) — the suppression store is per-lead opt-out; the ECG list is statutory and checked independently (outreach-plan §4 #3).
- **Footer consistency:** after opt-out, the footer's "Ad notice / ConsentSource" line no longer applies to that lead; no further email is sent, so no update is needed in sent artifacts.

## 7. Compliance mapping

| Requirement | Source | How the endpoint satisfies it |
|---|---|---|
| Free, easy, 1-click opt-out | DE UWG §7(3)4 · AT TKG §174(4) · CH UCA Art. 3(1)(o) · US CAN-SPAM §316.5 | GET link, no fee/login/steps (sec. 4) |
| Honored ≤10 business days | US §316.5; EU/CH "promptly" | Immediate processing (sec. 5) |
| Permanent suppression, no sale/transfer | US §316.5; consent-log §3.9 | `suppression` rows permanent (sec. 3) |
| Opt-out given with each message | ePrivacy Art. 13(2)(4), §7 UWG | Every body carries `{{UnsubscribeURL}}` |
| Revocation → DNC in consent log | `consent-log.md` §2 REVOCATION | Step 3 of endpoint processing (sec. 6) |
| No reply address required | n/a (we keep the reply-"unsubscribe" line as fallback) | Reply line remains in bodies |

## 8. Edge cases & security

- **Malformed/unknown token:** confirmation page only; no data disclosure (sec. 2).
- **Re-click / replay:** idempotent; single suppression row.
- **Enumeration:** tokens are UUIDv4 — no practical enumeration; do not log raw tokens in app logs beyond the store.
- **Abuse/rate limit:** cap `POST /unsubscribe` per IP (e.g. 30/min) — GET stays unlimited (email-client friendly).
- **DB failure:** return 500, do **not** render "unsubscribed" (never claim suppression that didn't persist).
- **Case/whitespace:** token compared exact (URL-encoded); email normalized lowercase.

## 9. Testing checklist

- [ ] Clicking the link in any of the lead's 3 touches suppresses the email once; later touches (if any queued) are skipped.
- [ ] Suppressed address not sent in a subsequent batch (store check).
- [ ] `opted_out_at` recorded; ≤10-business-day requirement met trivially (immediate).
- [ ] Confirmation page renders; re-click returns same page, no duplicate row.
- [ ] Invalid token → neutral page, no email leak.
- [ ] Consent-log REVOCATION block updated for the lead.
- [ ] AT ECG list check still runs independently (not replaced by the store).

## 10. Integration points

| File | Change |
|---|---|
| `src/main.py` | Add `GET/POST /unsubscribe` routes (pattern: existing `@app.get` legal-page handlers, lines 140–161) |
| `src/database/models.py` | Add `Suppression` ORM model (schema in sec. 3) |
| `leads/send-footer-values.csv` | `UnsubscribeURL` column → per-lead tokenized URL at merge time (B5), not a single org value |
| `leads/consent-log.md` | REVOCATION block filled by the endpoint (sec. 6) |
| Sending tool | Query `suppression` before each touch; skip suppressed (outreach-plan §4 #2) |
