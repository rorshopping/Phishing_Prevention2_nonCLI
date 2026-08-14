# PhishDefend AI — Day-0 Send Prep

Prepared first-touch messages for the **9 sendable leads** (`leads/sendable-list.csv`, Touch 1 / D+0 only). Template bodies come verbatim from `leads/email-templates.md`; windows follow `leads/outreach-plan.md` §2–§3.

> **⚠️ Compliance gate (blocks every send below):** all 9 leads are **.de addresses**. Germany has **no B2B exemption** (`compliance.md` §2; `consent-log.md`). None of these leads currently has a logged consent record. **Do NOT send until** outreach-plan §4 gate #1 passes: phone/LinkedIn-first consent capture + `consent-log.md` entry + `{{ConsentSource}}` filled. Also required per send: suppression-list check (§4 #2), working `{{UnsubscribeURL}}` (§4 #4), verbatim Compliance Footer (§4 #5).

---

## Summary

| # | Company | Contact | Email | Persona | Template | Send window (CEST) |
|---|---|---|---|---|---|---|
| 1 | IT-HAUS GmbH | Tim Holste | tholste@it-haus.com | IT manager | Template 2 | Tue 2026-08-11, 09:30–09:45 |
| 2 | RVM Versicherungsmakler GmbH | Thomas Kalbacher | thomas.kalbacher@rvm.de | SMB owner | Template 1 | Tue 2026-08-11, 09:50–10:05 |
| 3 | RVM Versicherungsmakler GmbH | Oliver Scholl | oliver.scholl@rvm.de | SMB owner | Template 1 | Tue 2026-08-11, 10:10–10:25 |
| 4 | RVM Versicherungsmakler GmbH | Joachim Roth | roth@rvm.de | SMB owner | Template 1 | Tue 2026-08-11, 10:30–10:45 |
| 5 | RVM Versicherungsmakler GmbH | Katharina Bastians | katharina.bastians@rvm.de | SMB owner | Template 1 | Wed 2026-08-12, 09:30–09:45 |
| 6 | RVM Versicherungsmakler GmbH | Andreas Haberstock | andreas.haberstock@rvm.de | SMB owner | Template 1 | Wed 2026-08-12, 09:50–10:05 |
| 7 | RVM Versicherungsmakler GmbH | Uwe Janicki | uwe.janicki@rvm.de | SMB owner | Template 1 | Wed 2026-08-12, 10:10–10:25 |
| 8 | RVM Versicherungsmakler GmbH | Manuel Soares | manuel.soares@rvm.de | SMB owner | Template 1 | Thu 2026-08-13, 09:30–09:45 |
| 9 | Volk & Partner | Claus Volk | c.volk@volk-partner.de | SMB owner | Template 1 | Thu 2026-08-13, 09:50–10:05 |

**Window rules applied** (`outreach-plan.md` §3): Tue/Wed/Thu only (no Mon/Fri/weekend — first possible send day after D0=Mon 2026-08-10 is Tue 08-11), 09:30–11:30 recipient-local slot, staggered per lead, ≤20–30 sends/inbox/day (9 total — well under cap). Multiple RVM contacts spread across 3 days to avoid same-day burst to one company.

---

## 1. IT-HAUS GmbH — Tim Holste

- **Role:** Sales contact (person-level) · **Email:** tholste@it-haus.com · **Source:** https://www.it-haus.com/kontakt/
- **Persona:** IT manager → **Template 2**
- **Send window:** Tue 2026-08-11, **09:30–09:45 CEST**

**Subject:** Your phishing campaign templates are already leaked

> Hi Tim,
>
> Manual phishing tests are a losing game: identical templates your users recognize in seconds, hours of setup per campaign, and no audit trail when a real incident happens. Employees even share the "test" emails with each other.
>
> PhishDefend AI fixes that. AI generates fresh, personalized attacks per employee — spear-phishing, CEO fraud, vishing, smishing included — so your users can't game the test. Everything runs automated, with real-time Slack alerts, monthly PDF reporting, and GDPR/NIS2 evidence on demand.
>
> Set-up takes under an hour. Want a live demo against your own test group?
>
> Prefer not to hear from us? [Unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you immediately.
>
> ---
> *Compliance Footer (verbatim, `email-templates.md`):*
>
> **PhishDefend AI** — {{LegalEntityName}} · {{StreetAddress}}, {{PostalCode}} {{City}}, {{Country}} · {{RegisterCourt}} HRB {{RegisterNo}} · VAT {{VATId}} · Managing Director: {{ManagingDirector}} · [Imprint]({{ImpressumURL}}) · [Privacy policy]({{PrivacyURL}})
>
> **Ad notice:** This is a commercial advertisement. You receive it because {{ConsentSource}} — free to opt out at any time. [Unsubscribe — one click, no login]({{UnsubscribeURL}}) · Or reply "unsubscribe". Opt-outs honored within 10 business days; your address is permanently suppressed and never sold or transferred.

**Gates:** §4 #1 consent ❌ (none logged — capture first) · #2 suppression ✅ (not listed) · #4 unsubscribe ✅ (link in body) · #5 footer ✅

---

## 2. RVM Versicherungsmakler GmbH — Thomas Kalbacher

- **Role:** Geschäftsführer; Cyber-Risiko-Experte (person-level) · **Email:** thomas.kalbacher@rvm.de · **Source:** https://www.rvm.de/en/services/
- **Persona:** SMB owner → **Template 1**
- **Send window:** Tue 2026-08-11, **09:50–10:05 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Thomas,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1 — fill {{LegalEntityName}} … {{ConsentSource}} before send)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## 3. RVM Versicherungsmakler GmbH — Oliver Scholl

- **Role:** Cyberversicherungs-Experte (person-level) · **Email:** oliver.scholl@rvm.de · **Source:** https://www.rvm.de/en/services/
- **Persona:** SMB owner → **Template 1**
- **Send window:** Tue 2026-08-11, **10:10–10:25 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Oliver,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## 4. RVM Versicherungsmakler GmbH — Joachim Roth

- **Role:** Ansprechpartner (person-level) · **Email:** roth@rvm.de · **Source:** https://www.rvm.de/wp-content/uploads/2025/04/RVM-Gruppe_Kundenmagazin_V1_2025.pdf
- **Persona:** SMB owner → **Template 1**
- **Send window:** Tue 2026-08-11, **10:30–10:45 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Joachim,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## 5. RVM Versicherungsmakler GmbH — Katharina Bastians

- **Role:** Member of Exec. Board (person-level) · **Email:** katharina.bastians@rvm.de · **Source:** https://realestate.rvm.de/en/
- **Persona:** SMB owner → **Template 1**
- **Send window:** Wed 2026-08-12, **09:30–09:45 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Katharina,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## 6. RVM Versicherungsmakler GmbH — Andreas Haberstock

- **Role:** Member of Exec. Board (person-level) · **Email:** andreas.haberstock@rvm.de · **Source:** https://realestate.rvm.de/en/
- **Persona:** SMB owner → **Template 1**
- **Send window:** Wed 2026-08-12, **09:50–10:05 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Andreas,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## 7. RVM Versicherungsmakler GmbH — Uwe Janicki

- **Role:** Management (person-level) · **Email:** uwe.janicki@rvm.de · **Source:** https://realestate.rvm.de/en/
- **Persona:** SMB owner → **Template 1**
- **Send window:** Wed 2026-08-12, **10:10–10:25 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Uwe,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## 8. RVM Versicherungsmakler GmbH — Manuel Soares

- **Role:** Management (person-level) · **Email:** manuel.soares@rvm.de · **Source:** https://realestate.rvm.de/en/
- **Persona:** SMB owner → **Template 1**
- **Send window:** Thu 2026-08-13, **09:30–09:45 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Manuel,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## 9. Volk & Partner — Claus Volk

- **Role:** Geschäftsführer (person-level) · **Email:** c.volk@volk-partner.de · **Source:** https://volk-partner.de/impressum/ ; https://www.bibb.de/dienst/ausbildungplus/de/ausbildungsbetrieb/ansehen/18664
- **Persona:** SMB owner → **Template 1**
- **Send window:** Thu 2026-08-13, **09:50–10:05 CEST**

**Subject:** The one click that costs SMBs their business

> Hi Claus,
>
> You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.
>
> Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.
>
> GDPR-compliant, hosted in Germany.
>
> Want a free sample campaign for your team?
>
> If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.
>
> ---
> *Compliance Footer (verbatim):* *(as in §1)*

**Gates:** §4 #1 consent ❌ (none logged) · #2 suppression ✅ · #4 unsubscribe ✅ · #5 footer ✅

---

## Pre-send checklist (apply to every lead above)

- [ ] **Consent gate §4 #1:** consent-log entry exists for the exact address (phone/LinkedIn-first capture, timestamped). Until then — **no send**.
- [ ] **§4 #2:** address not on suppression list.
- [ ] **§4 #4/#5:** working `{{UnsubscribeURL}}` + verbatim Compliance Footer with filled legal-entity fields (`{{LegalEntityName}}`, `{{StreetAddress}}`, `{{PostalCode}}`, `{{City}}`, `{{Country}}`, `{{RegisterCourt}}`, `{{RegisterNo}}`, `{{VATId}}`, `{{ManagingDirector}}`, `{{ImpressumURL}}`, `{{PrivacyURL}}`).
- [ ] **§4 #10:** `{{ConsentSource}}` filled from the log entry.
- [ ] **§3:** send inside the assigned window; log the send date in the lead/consent record.
- [ ] **Day-3/7 follow-ups:** only fire Follow-Up 1 (D+3) and Follow-Up 2 (D+7) if the lead replies/engages per `outreach-plan.md` §2; re-check gates before each.
