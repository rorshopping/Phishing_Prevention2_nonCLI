# PhishDefend AI — Cold Email Templates

Three outreach templates, one per persona. Each leads with a phishing-training pain point and ends with a clear opt-out line. Word count kept under 120.

> **Compliance gate — read before any send:** per `compliance.md`, DE and AT have **no B2B exemption** (UWG §7(2); TKG §174(3)): cold email without **prior express consent** is unlawful there. Only send to DE/AT contacts with a **documented consent log** (double opt-in, or phone/LinkedIn consent captured with timestamp + scope + source). For CH, targeting must be **role-relevant** to the recipient's business and always include sender identity + opt-out. US sends need no consent but must comply with CAN-SPAM (ad label, physical postal address, working opt-out). Every send must append the **Compliance Footer** below.

---

## 1. SMB Owner

**Subject:** The one click that costs SMBs their business

Hi {{FirstName}},

You didn't hire a security team, so training is last on your list — until one employee clicks a fake invoice and a month of your cash flow walks out the door.

Running simulations yourself eats hours you don't have. PhishDefend AI does it for you: 25 realistic, AI-personalized campaigns a year, fully automatic. When someone slips, they get a 2-minute micro-training right on the click. You get a monthly PDF — no login, no dashboard, nothing to babysit.

GDPR-compliant, hosted in Germany.

Want a free sample campaign for your team?

If you'd rather not hear from us, [unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you.

### Follow-Up 1 (Day 3)
**Subject:** {{FirstName}}, the fake-invoice test is free

Wanted to circle back — is free really the blocker? Most owners tell us it's time, not money. PhishDefend AI runs itself: 25 campaigns a year, no login, no dashboards, monthly PDF in your inbox. We'll run a free campaign against your real team and send results within two weeks.

That's worth 10 minutes of your week.

If it isn't, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Follow-Up 2 (Day 7)
**Subject:** Last note — free phishing test

Final note, {{FirstName}} — I'll close this out. A single invoice-phishing click can cost an SMB five figures in lost cash flow. Our free campaign shows you where your team stands before attackers do.

Setup takes one reply from you. Say "yes" and we'll start; say "unsubscribe" and you'll never hear from us again.

---

## 2. IT Manager

**Subject:** Your phishing campaign templates are already leaked

Hi {{FirstName}},

Manual phishing tests are a losing game: identical templates your users recognize in seconds, hours of setup per campaign, and no audit trail when a real incident happens. Employees even share the "test" emails with each other.

PhishDefend AI fixes that. AI generates fresh, personalized attacks per employee — spear-phishing, CEO fraud, vishing, smishing included — so your users can't game the test. Everything runs automated, with real-time Slack alerts, monthly PDF reporting, and GDPR/NIS2 evidence on demand.

Set-up takes under an hour. Want a live demo against your own test group?

Prefer not to hear from us? [Unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you immediately.

### Follow-Up 1 (Day 3)
**Subject:** Your users already know the test

Quick follow-up, {{FirstName}} — the problem you flagged is exactly what we fixed. AI generates fresh, per-employee attacks, so no two emails are alike and nothing leaks between users. Vishing and smishing included, so your coverage isn't just inboxes.

A live demo against your own test group takes 30 minutes, and we handle the setup end-to-end on your infrastructure.

Worth a look? If not, [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Follow-Up 2 (Day 7)
**Subject:** Demo is yours whenever — closing this out

Closing this out, {{FirstName}}. Real incident triage beats running campaigns in-house: Slack alerts the moment someone clicks, and GDPR/NIS2 evidence is ready before your next audit.

The demo runs on your infrastructure, your test group, zero production risk. Reply "demo" and I'll schedule it; reply "unsubscribe" and you're removed. Either way, thanks for reading.

---

## 3. HR Lead

**Subject:** Security awareness training nobody ignores

Hi {{FirstName}},

Your team tunes out the annual security slides — yet you're accountable for the evidence, the GDPR paperwork, and what happens after the first click.

PhishDefend AI turns awareness into a habit, not a lecture. Employees receive realistic phishing simulations year-round, and the moment someone slips, a micro-training appears right where they are — 90 seconds, remembered. You get a monthly PDF for leadership, plus NIS2/GDPR documentation without chasing anyone for completion lists.

Employees who train in the flow report higher engagement, and your compliance file fills itself.

Worth a 15-minute walkthrough with your HR head?

No thanks? [Unsubscribe in one click — free, no login]({{UnsubscribeURL}}), or reply "unsubscribe" and we'll remove you right away.

### Follow-Up 1 (Day 3)
**Subject:** Training your team won't skip

Circling back, {{FirstName}} — you're accountable for the compliance evidence, not just the training. With PhishDefend AI, completion is tracked automatically, micro-trainings happen in the flow (90 seconds, no lectures), and the GDPR/NIS2 documentation fills itself.

A 15-minute walkthrough with your HR head shows the whole flow end-to-end.

Not interested? [unsubscribe in one click]({{UnsubscribeURL}}) — or reply "unsubscribe" and we'll remove you.

### Follow-Up 2 (Day 7)
**Subject:** Last call — a compliance file that fills itself

Final message, {{FirstName}}. HR teams spend weeks chasing completion lists and documenting training for auditors. Our platform delivers the documentation with every micro-training — while employees actually engage with it.

If your compliance file fills itself as your team learns, that's the pitch.

Reply "yes" for a walkthrough, or "unsubscribe" to end this. Thanks for your time.

---

## Compliance Footer (append verbatim to every send)

**PhishDefend AI** — {{LegalEntityName}}
{{StreetAddress}}, {{PostalCode}} {{City}}, {{Country}}
{{RegisterCourt}} HRB {{RegisterNo}} · VAT {{VATId}} · Managing Director: {{ManagingDirector}}
[Imprint]({{ImpressumURL}}) · [Privacy policy]({{PrivacyURL}})

**Ad notice:** This is a commercial advertisement. You receive it because {{ConsentSource}} — free to opt out at any time.
[Unsubscribe — one click, no login]({{UnsubscribeURL}}) · Or reply "unsubscribe". Opt-outs honored within 10 business days; your address is permanently suppressed and never sold or transferred.

---

## Placeholders & sending rules

- **{{FirstName}}, {{CompanyName}}** — lead data; the `From` address must match the persona's sender identity.
- **{{UnsubscribeURL}}** — functional, single-click, no login, no fee; must work ≥ 30 days after send (US), and suppress permanently (DE/AT/CH).
- **{{ConsentSource}}** — DE/AT: reference the logged consent (double opt-in or phone/LinkedIn consent, with timestamp); CH: "targeted outreach relevant to your role at {{CompanyName}}"; US: omit.
- **{{LegalEntityName}}, {{StreetAddress}}, {{PostalCode}}, {{City}}, {{Country}}** — full legal entity + physical postal address. Required for DE/AT Impressum and for the US CAN-SPAM valid-physical-postal-address rule (a USPS-registered PO box also qualifies).
- **{{RegisterCourt}} HRB {{RegisterNo}}, VAT {{VATId}}, {{ManagingDirector}}** — Impressum items required for DE (§5 DDG/§7 UWG); recommended for AT/CH.
- **{{ImpressumURL}}, {{PrivacyURL}}** — hosted legal-notice and privacy pages.
- **Advertising label:** AT (§6 ECG) and CH require the email to be recognizable as advertising — the "Ad notice" footer line covers this; for AT, also prefix the subject with `[Werbung]` when sending to Austrian addresses.
- **DE/AT consent gate:** never send templates 1–3 to DE/AT addresses without a documented consent source; cold email without prior express consent is unlawful there even in B2B (UWG §7(2), TKG §174(3)).
- **CH targeting:** keep outreach role-relevant (the IT Manager / HR Lead / SMB Owner personas already map to roles); generic bulk sends are not protected by the B2B tolerance reading of UCA Art. 3(1)(o).
- **Tracking pixels:** require separate, documented consent — remove tracking from DE sends unless consented.
