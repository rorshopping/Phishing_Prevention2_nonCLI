# Consent Log — DE / AT Outreach

Purpose: document **prior express consent** for every cold email sent to Germany (UWG §7(2) No. 2) or Austria (TKG §174(3)) addresses. Both jurisdictions have **no B2B exemption** — without a logged consent, the send is unlawful. This file matches the `{{ConsentSource}}` placeholder in `leads\email-templates.md` and the rules in `leads\compliance.md`.

---

## 1. Consent types (source of consent)

| Type | How obtained | Valid for DE/AT? | Evidence to store |
|---|---|---|---|
| **Double opt-in** | Web form → confirmation email → recipient clicks link | ✅ Standard | Signup timestamp, IP hash, consent wording, confirmation-click timestamp |
| **Phone consent** | B2B cold call (UWG §7(2) No. 1 presumed consent, or TKG permissive context); prospect explicitly agrees to email follow-up | ✅ if explicit & logged | Call date/time, caller, exact verbal script used, prospect's verbal "yes", call recording/note |
| **LinkedIn consent** | Non-promotional connection request → accepted → prospect agrees in message to email follow-up | ✅ if explicit & logged | Connection date, message text, prospect's reply text |
| **Existing customer (soft opt-in)** | Address obtained in connection with a **prior sale**; similar products only; opt-out offered at collection + each email | ✅ only if all §7(3) UWG / §174(4) TKG conditions met | Order/contract ref, product similarity, opt-out notice at collection, no prior objection |
| **Inbound request** | Prospect emailed you / requested a demo | ✅ | Inbound email or form, date, requested topic |
| ❌ **Not consent** | Business card, imprint/Firmenbuch address, LinkedIn connection alone, pre-ticked box, webinar signup, scraped/purchased list | ❌ Never | — |

---

## 2. Per-lead log template

Copy one block per lead into a lead row/record. Fill every field.

```
LEAD RECORD
──────────────────────────────────────────────
Lead:            {{FirstName}} {{LastName}}
Company:         {{CompanyName}}
Contact email:   {{EmailAddress}}          [ ] confirmed role-relevant (not generic info@/kontakt@ unless role holder named)
Country:         {{DE|AT|CH|US|other}}

CONSENT
──────────────────────────────────────────────
Consent type:    {{Double opt-in | Phone | LinkedIn | Existing customer | Inbound}}
Consent source:  {{Channel/URL/call-log ref}}
Consent date:    {{YYYY-MM-DD}}  (for phone: call time HH:MM; for double opt-in: confirmation-click date)
Consent scope:   [ ] told WHO sends (PhishDefend AI, {{LegalEntityName}})
                 [ ] told WHAT (phishing-simulation / security-awareness products)
                 [ ] told HOW (email marketing)
                 [ ] unticked/active opt-in (no pre-ticked box)
Opt-out offered: [ ] at collection     [ ] in every email (1-click link)
SMS/linkedin account: {{Link to recording / message thread / form entry}}

VERIFICATION (done by sender before each send)
──────────────────────────────────────────────
[ ] Consent record exists and matches this email address
[ ] Scope still covers this email's content (own similar products only)
[ ] No objection/revocation on file (suppression list checked)
[ ] (AT only) Address NOT on ECG list (eintragen@ecg.rtr.at)  [ ] checked {{date}}
[ ] Channel-specific: {{phone note / double opt-in confirm date / LinkedIn thread}}

REVOCATION
──────────────────────────────────────────────
[ ] Revoked on {{date}}  →  add to suppression list immediately, mark lead permanently DNC
```

**Filled example:**

```
LEAD RECORD
──────────────────────────────────────────────
Lead:            Anna Beispiel
Company:         Beispiel GmbH
Contact email:   a.beispiel@beispiel.de        [x] confirmed role-relevant (IT-Managerin, named role holder)
Country:         DE

CONSENT
──────────────────────────────────────────────
Consent type:    Phone
Consent source:  Call log 2026-08-04, caller: S. Weber, dialer ref #4821
Consent date:    2026-08-04 10:15
Consent scope:   [x] told WHO (PhishDefend AI)   [x] told WHAT (phishing simulation)
                 [x] told HOW (email)            [x] active opt-in, no pre-tick
Opt-out offered: [x] verbal at collection        [x] 1-click link in every email
SMS/linkedin account: recording clip #4821a: prospect: "ja, schicken Sie mir die Demo-Mail"

VERIFICATION (done before each send)
──────────────────────────────────────────────
[x] Consent record exists and matches a.beispiel@beispiel.de
[x] Scope covers demo-offer email (own similar product)
[x] No objection on file
[x] (AT only) ECG list — n/a (DE)
[x] Channel-specific: recording reviewed, explicit verbal yes

REVOCATION
──────────────────────────────────────────────
[ ] Revoked on ___  →  suppression list + DNC
```

---

## 3. Step-by-step workflow (outreach staff)

**Before first contact**
1. **Source the lead** from a lawful channel: inbound form, double-opt-in signup, cold call (DE: presumed-consent call per UWG §7(2) No. 1 — concrete relevance required), or a non-promotional LinkedIn message. Never from scraped/purchased lists, business cards, or imprints.
2. **Check suppression list** (and AT: ECG list) before any contact.

**Capturing consent**
3. **Make the ask explicit.** Read the exact script: *"Darf ich Ihnen dazu eine E-Mail von PhishDefend AI senden?"* / *"May I send you a follow-up email about phishing simulations?"* The prospect must say yes to **email** specifically — a yes to "sending information" or a LinkedIn connection is not enough.
4. **Log within 24 hours** using the per-lead template: type, source ref, timestamp, exact wording, scope checkboxes. For double opt-in, wait for the **confirmation-click** before logging as granted. For phone, attach the call note/recording.
5. **Never pre-tick or imply consent.** Silence, non-response, or prior business contact = no consent (BVwG 24.05.2024; AG Düsseldorf 23 C 120/25).

**Before every send**
6. **Verify** against the VERIFICATION checklist: record exists for this exact address, scope still covers the message content (own similar products only — no cross-selling), no revocation on file, AT: ECG check.
7. **Fill `{{ConsentSource}}`** in the footer with the logged source + date, e.g. *"phone consent, 2026-08-04, S. Weber"* or *"double opt-in, 2026-08-04"*. If no consent record exists for a DE/AT lead → **do not send**; route to call/LinkedIn or drop.
8. **Every email carries** the 1-click unsubscribe link; log each send's date in the lead record.

**Ongoing maintenance**
9. **On any opt-out/revocation:** timestamp it, add to the suppression list **immediately**, mark the lead DNC, and never re-market the address (or sell/transfer it).
10. **Retain** consent records at least 3 years (AT practice) and for the duration of any dispute risk; audit the log quarterly — sender carries the **burden of proof**, so an empty or sloppy log is treated as no consent.

---

## 4. Audit checklist (quarterly)

- [ ] Every DE/AT address in the send queue has a dated consent record with source + wording.
- [ ] No address on the suppression list or AT ECG list was emailed.
- [ ] `{{ConsentSource}}` in sent emails matches the log entry.
- [ ] Scope never exceeded (own similar products only).
- [ ] Opt-out link present in every email; revocations honored within 10 business days.
