# Launch Readiness — send-batch-1.csv

Consolidated pre-launch checklist for firing `leads/send-batch-1.csv` (117 touches, 39 sendable leads — see `leads/sendable-list.csv`, `leads/send-calendar.csv`). Every blocker below maps to the **artifact** that clears it and the **owner** responsible. Status of all items as of **2026-08-10**.

> **Launch rule:** send-batch-1 fires only when **B1–B4 are green**, the footer merge (B5) is complete, and the infra checks (B6–B8) pass. None of B1–B4 is green today — nothing may be sent yet.

---

## Core blockers

| # | Blocker | Current state (2026-08-10) | Required before first send | Resolving artifact | Owner |
|---|---|---|---|---|---|
| **B1** | **Legal entity data (Impressum)** | `static/impressum.html` is all placeholders: `YOUR_COMPANY_NAME_HERE`, `[Street & Number]`, `[Postal Code, City, Germany]`, `[Amtsgericht City]`, `[HRB XXXXX]`, `[DE XXX XXX XXX]`, `[Name of Managing Director]` | Registered legal entity published on the Impressum (name, street, postal code + city, register court + HRB, VAT ID, managing director); mirrored to root `impressum.html` (byte-for-byte, per AGENTS.md root-mirror rule) | `static/impressum.html` + root `impressum.html` → then fill `leads/send-footer-values.csv` (7 fields currently empty) | Founder / Legal counsel (impressum contact: `rorshopping@gmail.com`) |
| **B2** | **DE/AT consent records** | `leads/consent-log.md` is empty — **0 records**; all 39 sendable leads are DE/AT/CH, and DE/AT have **no B2B exemption** (UWG §7(2), TKG §174(3)) | One dated consent record per lead (double opt-in, or phone/LinkedIn consent with timestamp + scope + source) covering email marketing of phishing-simulation products — captured via the phone/LinkedIn-first paths in `leads/person-lookup-queue.md` | `leads/consent-log.md` (per-lead records, workflow §3 steps 1–6) | Outreach staff / consent manager |
| **B3** | **Unsubscribe endpoint (`{{UnsubscribeURL}}`)** | No unsubscribe target exists — every body in `send-batch-1.csv` still references `{{UnsubscribeURL}}` (195 occurrences) | Working 1-click, no-login, free unsubscribe page/endpoint that permanently suppresses the address (DE/AT/CH) and is honored ≤ 10 business days (US rule as fallback); suppress list retained | New `/unsubscribe` endpoint + suppression store (to be built) | Engineering |
| **B4** | **Per-lead `{{ConsentSource}}`** | `leads/send-footer-values.csv` has `ConsentSource` empty; bodies reference `{{ConsentSource}}` (117 occurrences) | Every lead has its consent-log source + date (e.g. `phone consent, 2026-08-04, S. Weber`) filled into its body; CH: `targeted outreach relevant to your role at {{CompanyName}}`; US: omit | `leads/consent-log.md` → `leads/send-footer-values.csv` → merge into each body | Outreach staff / consent manager |

---

## Merge & infra checks

| # | Check | Current state | Required | Resolving artifact | Owner |
|---|---|---|---|---|---|
| **B5** | **Footer merge** | `send-batch-1.csv` bodies still contain 13 placeholder fields (see `leads/send-footer-values.csv`); one unresolved FirstName is already fixed (Christoph Eggers) | No `{{...}}` remains in any body except none — all footer values + `{{ConsentSource}}` + `{{UnsubscribeURL}}` inlined per lead | Merge script consuming `leads/send-footer-values.csv` + consent log → regenerated `leads/send-batch-1.csv` | Engineering / outreach |
| **B6** | **Sender infrastructure** | No sending tool configured; `leads/tool-stack.md` §4 stack researched only | Verified, warmed inbox(es) with SPF/DKIM/DMARC; capacity for the calendar's max day (27 sends, ≤ 30/inbox/day); < 2% bounce | Sending tool + DNS records per `leads/tool-stack.md` §4 | Engineering / delivery |
| **B7** | **Pass-2 verification** | `leads/verified.csv` = Stage-3 pass-1 only (syntax/MX + role gate); 142 verified / 80 role_gate | SMTP mailbox + catch-all resolution (MillionVerifier bulk → Bouncer for high-value DACH) on the 39 sendable addresses | `leads/verified.csv` (pass-2 columns) | Outreach / data |
| **B8** | **Country-specific send rules** | `leads/outreach-plan.md` §4 gates #6/#7 defined, not applied | AT addresses: subject prefixed `[Werbung]` (TISA `markus.schrott@tisa.at`); CH addresses (ASSEPRO, Sumec, TISA CH, ARTUS — 15 leads): role-relevance + sender identity + opt-out; DE: Impressum footer complete | `leads/outreach-plan.md` §4 + `leads/email-templates.md` (footer note) → batch generation | Outreach lead |
| **B9** | **Reply handling & logging** | Defined in `leads/pipeline.md` §Stage 4 only | Per-touch send-date logged per lead; reply routing (trial client / nurture / opt-out / unresponsive) wired; D+14 park to nurture | `leads/progress.md` funnel update + send logs | Outreach lead |

---

## Definition of Ready (order of operations)

1. **B1** — publish legal entity on Impressum (static + root mirror) → fill `send-footer-values.csv` (7 empty fields).
2. **B2 + B4** — capture + log consent per lead in `consent-log.md`; only leads with a record become eligible; `{{ConsentSource}}` derived per lead.
3. **B3** — build + test the `/unsubscribe` endpoint with permanent suppression.
4. **B5** — merge all footer values into `send-batch-1.csv` bodies; scan for zero remaining placeholders.
5. **B6–B7** — sender infra + pass-2 verification on the 39 addresses.
6. **B8–B9** — apply `[Werbung]` (AT) and CH rules; wire reply handling; then fire per `send-calendar.csv` windows and track in `progress.md`.

## Status summary

| Blocker | Status |
|---|---|
| B1 Legal entity | 🔴 Blocked — placeholders in impressum |
| B2 Consent records | 🔴 Blocked — 0 records logged |
| B3 Unsubscribe endpoint | 🔴 Blocked — not built |
| B4 ConsentSource per lead | 🔴 Blocked — depends on B2 |
| B5 Footer merge | 🔴 Blocked — depends on B1/B2/B3/B4 |
| B6 Sender infrastructure | 🟡 Not configured |
| B7 Pass-2 verification | 🟡 Pending |
| B8 Country rules | 🟡 Defined, not applied |
| B9 Reply handling | 🟡 Defined, not wired |
