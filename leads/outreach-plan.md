# PhishDefend AI — Outreach Plan (Pipeline Stage 4)

Concrete sending plan that sequences the three persona templates (`leads/email-templates.md`) into a Day 0/3/7 cadence. Gate for launch: leads pass **Stage 3 verification** in `leads/pipeline.md` and the consent gates below pass **before every single send**.

---

## 1. Persona → lead mapping

Current state: 46 collected emails, **45 are role accounts** (`info@`, `kontakt@`…) — per `pipeline.md` §Stage 3 these must be converted to person lookup **before** outreach. Named decision-makers already visible on sourced pages (`contacts-v1.md`) are the person-lookup targets below. Only person-level address collected so far: `tholste@it-haus.com`.

| Persona | Target decision-maker role | Sector focus (ICP) | Lead companies (from `contacts-v1.md`) | Person-lookup targets (named on page) | Current collected contact |
|---|---|---|---|---|---|
| **SMB owner** | Geschäftsführer / MD / small-company CISO | Manufacturing, MedTech, insurance brokers | NetPlans, SÜDVERS, RVM, ASSON, Volk & Partner, RCU, Jüttner, Claaßen, WEKAL, Teubert, Ebel, MEZ, medika, Saegeling, MTR, MEDITECH | NetPlans: Sascha Collin, Uwe Bretzinger · SÜDVERS: Ralf Bender, Manfred Karle · RVM: Michael Friebe, Thomas Kalbacher, Gerd Kunert · ASSON: Marc Loreth · Claaßen: Christine Schröder | `info@…`, `kontakt@…` (role) |
| **IT manager** | IT-Leiter / IT system house contact | IT system houses, managed cloud/hosting, telecom (NIS2 "digital providers") | comito, IT-HAUS, NetPlans, Nösse, ORBIT, plus icp-research targets (netcup, dogado, manitu, easybell, all-inkl, sipgate) | comito: Timo Kircher (IT-Berater) · IT-HAUS: Tim Holste (Sales) · ORBIT: Tobias Hejna (CEO) | `info@comito.de`, `tholste@it-haus.com` (person), `info@…` (role) |
| **HR lead** | Personal / HR-Leiter | Manufacturing, MedTech, system houses with >50 staff | MEZ, Teubert, Ebel, MEDITECH, NetPlans, SÜDVERS, Jüttner | MEZ: Gloria Marten (Personal) | `personal@mez.de`, `info@…` (role) |

**Mapping rule:** assign each verified person to exactly one persona. Priorities: (1) role as stated, (2) sector fit, (3) NIS2 relevance. If a contact's true role is unknown → treat as SMB owner (MD default). Never send the HR template to a known IT contact or vice versa — mismatched personas void the role-relevance defence (CH) and waste consent scope (DE/AT).

---

## 2. Cadence — Day 0 / 3 / 7

Uses `leads/email-templates.md`: the persona's **initial email** (subject + body), then **Follow-Up 1** and **Follow-Up 2** from the same persona section. Three touches max, then park at D+14 per `pipeline.md` §Stage 4.

| Touch | Day | Message (email-templates.md) | Sender / From | Purpose | CTA |
|---|---|---|---|---|---|
| 1 | **D+0** | Initial email for the persona (SMB Owner / IT Manager / HR Lead section) | Persona-matching sender identity + Compliance Footer | Lead with pain point, 1-line value prop | Free sample campaign (SMB) / live demo (IT) / walkthrough (HR) |
| 2 | **D+3** | Follow-Up 1 (Day 3) — same persona | Same identity | Objection handling + proof, low-pressure CTA | Reply "yes" / "demo" |
| 3 | **D+7** | Follow-Up 2 (Day 7) — same persona | Same identity | Last touch, close or park | Reply "yes" / "demo" / "unsubscribe" |
| — | **D+14** | — stop | — | Park: move to nurture (quarterly newsletter) or disqualify | — |

Rules:
- **One touch per day per lead**, 3 touches total, **no more**.
- **Day counting:** D+0 = send day; D+3 = third calendar day after D+0; D+7 = seventh. Recompute if a send is skipped for a compliance-gate failure (see §4).
- **No reply handling** → follow `pipeline.md` §Stage 4 "Reply handling": positive → create trial client; negative-qualified → nurture, re-sequence in 90 days; opt-out → `opted_out`, GDPR-log, **never contact again**.
- **Variable `{{FirstName}}`** must be filled from the verified person record; role accounts without a named person stay blocked until person lookup succeeds.

---

## 3. Sending windows

| Rule | Setting |
|---|---|
| Days | **Tue / Wed / Thu** preferred; Mon allowed only for low-priority; **no Fri, Sat, Sun** (no follow-ups landing on a weekend — if D+3/D+7 falls on a weekend, shift to the next Tuesday) |
| Hours (recipient-local) | 09:30–11:30 and 13:30–16:00; no sends 16:00–09:30, no sends on German/Austrian/Swiss public holidays (check regional holiday calendar per send week) |
| Timezones | DE/AT: CET/CEST · CH: CET/CEST · US: recipient's local timezone (e.g., 09:00–11:00 / 13:00–15:00 local) |
| Volume caps | ≤ 20–30 sends per warmed inbox per day; ≤ ~1,000/month per inbox (`tool-stack.md` §4); keep bounce rate < 2% |
| Follow-up timing | D+3 and D+7 touch at the same sender time-of-day window as D+0, unless recipient's engagement (e.g., open) suggests a different hour |
| Anti-spam backstop | If any send would exceed the caps or a gate fails → **hold, do not batch-skip gates** |

---

## 4. Compliance gates — must pass before EACH send

The consent gate below is **absolute for DE/AT** (no B2B exemption — `compliance.md` §2/§3, `consent-log.md`). A failure at any gate blocks the send, not the lead.

| # | Gate | Check | Applies | Fail action |
|---|---|---|---|---|
| 1 | **Consent log** | Consent record exists for this **exact address** in `consent-log.md` (double opt-in / phone / LinkedIn / inbound / existing-customer), with timestamp + scope covering this message's content | DE, AT | **Do not send.** Route to phone-first or non-promotional LinkedIn, capture + log consent, then send |
| 2 | **Suppression list** | Address not on suppression list / DNC (previous opt-out, revocation) | All | Do not send. Mark lead `opted_out`, never re-contact |
| 3 | **ECG list** | Address not on the Austrian Robinson/ECG list (`eintragen@ecg.rtr.at`) | AT only | Do not send |
| 4 | **Unsubscribe link** | Working `{{UnsubscribeURL}}` (1-click, free, no login) present in the message + in every template/follow-up; footer contains sender identity + physical address | All | Fix before send |
| 5 | **Compliance Footer** | Verbatim footer from `email-templates.md` (Impressum, legal entity, ad notice, opt-out, suppression promise) appended | All | Append before send |
| 6 | **Advertising label** | Subject prefixed `[Werbung]` | AT | Prepend subject |
| 7 | **Role-relevance** | Message matches the persona's verified role; not a generic bulk send; sender identity truthful | CH (also good practice everywhere) | Re-map to correct persona or drop |
| 8 | **CAN-SPAM** | Accurate header/`From`, physical postal address, ad identification, opt-out honored ≤ 10 business days | US | Fix before send |
| 9 | **Role-account gate** | Address is a verified person/role-holder (not `info@`/`kontakt@` generic unless role holder named); person lookup logged | All | Convert to person lookup (`pipeline.md` §Stage 3) or reject |
| 10 | **`{{ConsentSource}}`** | Placeholder filled from the consent log entry (DE/AT); for CH "targeted outreach relevant to your role at {{CompanyName}}"; omit for US | DE/AT/CH | Fill before send |

**Gate order before firing each of the three touches:** run §4 gates 1–10 → populate personalization fields (`{{FirstName}}`, `{{CompanyName}}`) from the verified record → attach Compliance Footer + unsubscribe link → send within §3 windows → log the send date in the lead's consent/lead record.

**Recurring gates (per touch, not just touch 1):** re-check suppression list and consent scope before Follow-Up 1 and Follow-Up 2 — a revocation between touches kills the sequence immediately, and consent scope must still cover the follow-up's content (own similar products only).

---

## 5. KPIs & targets (from `pipeline.md` §KPIs)

| Metric | Target |
|---|---|
| Verification pass rate | ≥ 60% of collected |
| Deliverability (opens/sent) | ≥ 85% |
| Reply rate | ≥ 3–5% of sent |
| Positive reply rate | ≥ 1.5% of sent |
| Meetings booked / qualified | ≥ 1% of sent |
| Weekly verified new leads | ≥ 20 |
| Discovery → first touch | ≤ 7 days |

---

## 6. Handoff

- **Positive reply** → create trial client, hand to onboarding; log outcome in `progress.md` (§Reply handling).
- **Blocked by consent gate** → lead stays in pipeline, routed to phone/LinkedIn consent capture; no email until `consent-log.md` entry exists.
- **Tracking:** update `leads/progress.md` funnel counts after each touch (Outreach/Replies/Qualified/Opted out).
