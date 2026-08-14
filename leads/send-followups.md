# PhishDefend AI — Follow-Up Send Prep (Day 3 & Day 7)

Prepared Day-3 (Follow-Up 1) and Day-7 (Follow-Up 2) messages for the **9 sendable leads** (`leads/sendable-list.csv`), using the follow-up templates in `leads/email-templates.md`, scheduled per the cadence in `leads/outreach-plan.md` §2–§3. Base dates assume Day-0 send windows from `leads/send-day0.md`.

> **⚠️ Compliance gate:** all 9 leads are **.de addresses** — **no B2B exemption** (`compliance.md` §2). Follow-ups may only fire **after** the Day-0 send was lawful (consent logged in `consent-log.md`, `{{ConsentSource}}` filled). Before each follow-up, re-run outreach-plan §4 gates: #1 consent record + scope still covers the message · #2 suppression list (a revocation between touches kills the sequence) · #4 working `{{UnsubscribeURL}}` · #5 Compliance Footer. If the lead replied → handle per `pipeline.md` §Stage 4 reply routing and skip the follow-up.

**Cadence rules applied** (`outreach-plan.md` §2–§3): D+3 = 3rd calendar day after D+0, D+7 = 7th. Follow-ups may not land on Fri/Sat/Sun → shift to next allowed day (Tue/Wed/Thu). Collision handling (shifted D+3 = D+7 day) → D+7 moves to the next allowed day so the two touches stay separate. Windows 09:30–11:30 / 13:30–16:00 CEST, staggered.

---

## Summary

| # | Company | Contact | Persona | Template | **FU1 (Day 3)** | **FU2 (Day 7)** |
|---|---|---|---|---|---|---|
| 1 | IT-HAUS GmbH | Tim Holste | IT manager | T2 | Tue 2026-08-18, 09:30–09:45 | Wed 2026-08-19, 09:30–09:45 |
| 2 | RVM Versicherungsmakler GmbH | Thomas Kalbacher | SMB owner | T1 | Tue 2026-08-18, 09:50–10:05 | Wed 2026-08-19, 09:50–10:05 |
| 3 | RVM Versicherungsmakler GmbH | Oliver Scholl | SMB owner | T1 | Tue 2026-08-18, 10:10–10:25 | Wed 2026-08-19, 10:10–10:25 |
| 4 | RVM Versicherungsmakler GmbH | Joachim Roth | SMB owner | T1 | Tue 2026-08-18, 10:30–10:45 | Wed 2026-08-19, 10:30–10:45 |
| 5 | RVM Versicherungsmakler GmbH | Katharina Bastians | SMB owner | T1 | Tue 2026-08-18, 13:30–13:45 | Wed 2026-08-19, 13:30–13:45 |
| 6 | RVM Versicherungsmakler GmbH | Andreas Haberstock | SMB owner | T1 | Tue 2026-08-18, 13:50–14:05 | Wed 2026-08-19, 13:50–14:05 |
| 7 | RVM Versicherungsmakler GmbH | Uwe Janicki | SMB owner | T1 | Tue 2026-08-18, 14:10–14:25 | Wed 2026-08-19, 14:10–14:25 |
| 8 | RVM Versicherungsmakler GmbH | Manuel Soares | SMB owner | T1 | Tue 2026-08-18, 14:30–14:45 | Thu 2026-08-20, 09:30–09:45 |
| 9 | Volk & Partner | Claus Volk | SMB owner | T1 | Tue 2026-08-18, 14:50–15:05 | Thu 2026-08-20, 09:50–10:05 |

*All Day-0 sends were Tue 08-11 / Wed 08-12 / Thu 08-13 (`send-day0.md`), so D+3 lands Fri/Sat/Sun for everyone → all FU1 shift to Tue 08-18. FU2: leads 1–7 land Wed 08-19 (leads 1–4 collided with shifted FU1 and moved from Tue 08-18), leads 8–9 land Thu 08-20.*

---

## 1. IT-HAUS GmbH — Tim Holste

- **Persona:** IT manager → Template 2 · **Email:** tholste@it-haus.com

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **09:30–09:45 CEST**
**Subject:** Your users already know the test

> Hi Tim,
>
> Quick follow-up — the problem you flagged is exactly what we fixed. AI generates fresh, per-employee attacks, so no two emails are alike and nothing leaks between users. Vishing and smishing included, so your coverage isn't just inboxes.
>
> A live demo against your own test group takes 30 minutes, and we handle the setup end-to-end on your infrastructure.
>
> Worth a look? If not, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Wed 2026-08-19, **09:30–09:45 CEST**
**Subject:** Demo is yours whenever — closing this out

> Hi Tim,
>
> Closing this out. Real incident triage beats running campaigns in-house: Slack alerts the moment someone clicks, and GDPR/NIS2 evidence is ready before your next audit.
>
> The demo runs on your infrastructure, your test group, zero production risk. Reply "demo" and I'll schedule it; reply "unsubscribe" and you're removed. Either way, thanks for reading.

*Compliance Footer (verbatim, `email-templates.md`) appended to both sends — as in `send-day0.md` §1.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check before each · unsubscribe link ✅ · footer ✅

---

## 2. RVM Versicherungsmakler GmbH — Thomas Kalbacher

- **Persona:** SMB owner → Template 1 · **Email:** thomas.kalbacher@rvm.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **09:50–10:05 CEST**
**Subject:** Thomas, the fake-invoice test is free

> Hi Thomas,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Wed 2026-08-19, **09:50–10:05 CEST**
**Subject:** Last note — free phishing test

> Hi Thomas,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## 3. RVM Versicherungsmakler GmbH — Oliver Scholl

- **Persona:** SMB owner → Template 1 · **Email:** oliver.scholl@rvm.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **10:10–10:25 CEST**
**Subject:** Oliver, the fake-invoice test is free

> Hi Oliver,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Wed 2026-08-19, **10:10–10:25 CEST**
**Subject:** Last note — free phishing test

> Hi Oliver,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## 4. RVM Versicherungsmakler GmbH — Joachim Roth

- **Persona:** SMB owner → Template 1 · **Email:** roth@rvm.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **10:30–10:45 CEST**
**Subject:** Joachim, the fake-invoice test is free

> Hi Joachim,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Wed 2026-08-19, **10:30–10:45 CEST**
**Subject:** Last note — free phishing test

> Hi Joachim,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## 5. RVM Versicherungsmakler GmbH — Katharina Bastians

- **Persona:** SMB owner → Template 1 · **Email:** katharina.bastians@rvm.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **13:30–13:45 CEST**
**Subject:** Katharina, the fake-invoice test is free

> Hi Katharina,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Wed 2026-08-19, **13:30–13:45 CEST**
**Subject:** Last note — free phishing test

> Hi Katharina,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## 6. RVM Versicherungsmakler GmbH — Andreas Haberstock

- **Persona:** SMB owner → Template 1 · **Email:** andreas.haberstock@rvm.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **13:50–14:05 CEST**
**Subject:** Andreas, the fake-invoice test is free

> Hi Andreas,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Wed 2026-08-19, **13:50–14:05 CEST**
**Subject:** Last note — free phishing test

> Hi Andreas,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## 7. RVM Versicherungsmakler GmbH — Uwe Janicki

- **Persona:** SMB owner → Template 1 · **Email:** uwe.janicki@rvm.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **14:10–14:25 CEST**
**Subject:** Uwe, the fake-invoice test is free

> Hi Uwe,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Wed 2026-08-19, **14:10–14:25 CEST**
**Subject:** Last note — free phishing test

> Hi Uwe,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## 8. RVM Versicherungsmakler GmbH — Manuel Soares

- **Persona:** SMB owner → Template 1 · **Email:** manuel.soares@rvm.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **14:30–14:45 CEST**
**Subject:** Manuel, the fake-invoice test is free

> Hi Manuel,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Thu 2026-08-20, **09:30–09:45 CEST**
**Subject:** Last note — free phishing test

> Hi Manuel,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## 9. Volk & Partner — Claus Volk

- **Persona:** SMB owner → Template 1 · **Email:** c.volk@volk-partner.de

### Day 3 — Follow-Up 1
**Window:** Tue 2026-08-18, **14:50–15:05 CEST**
**Subject:** Claus, the fake-invoice test is free

> Hi Claus,
>
> Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.
>
> That's worth 10 minutes of your week.
>
> If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Day 7 — Follow-Up 2
**Window:** Thu 2026-08-20, **09:50–10:05 CEST**
**Subject:** Last note — free phishing test

> Hi Claus,
>
> Final note — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.
>
> Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

*Compliance Footer (verbatim) appended to both sends.*

**Gates:** consent scope ✅ only if logged for D+0 · suppression re-check · unsubscribe ✅ · footer ✅

---

## Pre-send checklist (every follow-up)

- [ ] **§4 #1:** consent-log entry exists for the exact address and scope still covers this follow-up's content (own similar products only). No D+0 consent → **no follow-up**.
- [ ] **§4 #2:** address not on suppression list (re-checked since D+0; any opt-out/revocation ends the sequence permanently).
- [ ] **§4 #4/#5:** working `{{UnsubscribeURL}}` + verbatim Compliance Footer (legal-entity fields filled).
- [ ] **§4 #10:** `{{ConsentSource}}` filled from the log.
- [ ] **Reply routing:** if the lead replied since the last touch → handle per `pipeline.md` §Stage 4 (positive → trial client; qualified-negative → nurture) and **skip** the scheduled follow-up.
- [ ] **§3:** send inside the assigned window; log each send date in the lead/consent record.
- [ ] **D+14:** if still no reply after FU2 → park to nurture (`outreach-plan.md` §2).
