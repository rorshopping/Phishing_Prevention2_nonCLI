# PhishDefend AI — Lead Pipeline

The end-to-end outbound pipeline: **ICP → Discovery → Collection → Verification → Outreach**.
Track live counts per stage in [progress.md](progress.md). Every stage has an exit gate; a lead only moves forward when the gate passes.

```
ICP ──► Discovery ──► Collection ──► Verification ──► Outreach
 ^         │              │              │               │
 │         ▼              ▼              ▼               ▼
 └─ refines criteria   sources      raw CSV       email/ICP/GDPR   sequence
                       candidates    rows          checks          & follow-up
```

---

## Stage 0 — ICP (Ideal Customer Profile)

**Purpose:** Define who we target. Nothing is collected before this is locked.

| Attribute | Value |
|---|---|
| Company size | 10–500 employees (European SMEs / KMU) |
| Geography | Germany first (DE), then DACH / EU |
| Decision makers | Managing director, IT lead, Datenschutzbeauftragte (DSB), HR lead, small-company CISO |
| Industry focus | No security team, no dedicated IT security staff |
| Pain | No time to build phishing campaigns manually; must show GDPR/NIS2 compliance evidence |
| Trigger events | NIS2 scope (Oct 2024), ISO 27001 implementation, recent phishing incident, DSB mandate |
| Exclusions | Enterprises (>500 emp), companies with existing security team / KnowBe4-style platform, competitors |

**ICP gate:** candidate company must match company size AND geography AND at least one decision-maker role.

---

## Stage 1 — Discovery

**Purpose:** Build a target company list that matches the ICP.

**Sources:**
- LinkedIn Sales Navigator (company + contact search, saved searches)
- Bundesanzeiger / firmenwissen.de (German company registry, size + sector)
- NIS2-relevant sector lists (health, energy, transport, food, digital providers)
- Chamber of commerce / industry association member lists
- Referrals from existing clients

**Output:** `Company name, website, size, industry, HQ city, key contact name + role` (no email yet).

**Discovery gate:** company matches ICP (Stage 0 table). Reject out-of-scope companies immediately.

---

## Stage 2 — Collection

**Purpose:** Turn company records into raw contact rows (CSV).

**Raw CSV columns** (file: `leads/raw.csv`):

```
company,website,size,industry,city,contact_name,role,email,linkedin,notes
```

**Per-contact collection methods:**
- LinkedIn profile → email lookup (email permutators, hunter.io, Apollo)
- Company website contact pages / press releases (impressum)
- Personalization inputs: recent news, funding, hiring, LinkedIn activity
- Where no email found: collect LinkedIn profile URL as a **stage-2 only** record

**Collection gate:** every row has at least one identity channel — either an email address **or** a LinkedIn profile. Rows with neither are dropped.

---

## Stage 3 — Verification

**Purpose:** Remove dead addresses and non-ICP contacts before any outreach. **This stage is the spam/GDPR checkpoint.**

| Check | What it does | Fail action |
|---|---|---|
| Email syntax | regex validation | reject |
| MX / domain check | domain has valid MX record | reject |
| Mailbox verification | SMTP handshake / verification API (NeverBounce, ZeroBounce, verifalia) | reject |
| Role-account check | reject info@, sales@, support@, admin@ | convert to person lookup or reject |
| Role match | contact role ∈ decision-maker set (MD, IT lead, DSB, HR, CISO) | demote to secondary / reject |
| Company re-check | still matches ICP size + geography | reject |
| GDPR suitability | B2B, legitimate interest (Art. 6(1)(f)), no obvious opt-out/DNC marker | reject |

**Output:** verified row enters `leads/verified.csv` (adds `verified_at, verification_method, gdpr_note`).

**Verification gate:** **all** checks pass. A single failure blocks the row.

---

## Stage 4 — Outreach

**Purpose:** Send a personalized, GDPR-compliant sequence. First-touch follows within 48h of verification.

**Personalization inputs** (from Collection stage): company news, role-specific pain (NIS2/DSB/GDPR), LinkedIn activity.

**Sequence** (3 touches max, then park):

| Touch | Day | Channel | Message |
|---|---|---|---|
| 1 | D+0 | Email | Problem intro: phishing stats + NIS2 evidence requirement, 1-line value prop |
| 2 | D+3 | Email | Social proof: Bitkom 94% stat, €200B damage, case example, low-pressure CTA |
| 3 | D+7 | LinkedIn or email | Personalized follow-up on a trigger event, soft CTA to book 15-min call |
| — | D+14 | — | Park; move to nurture list (quarterly newsletter) or disqualify |

**Reply handling:**
- Positive → create trial client in PhishGuard (`client add`), hand to onboarding
- Negative but qualified → nurture, re-sequence in 90 days
- Negative/unsubscribed → mark `opted_out`, GDPR-log it, **never contact again**
- No reply → after D+14 park to nurture

**Outreach gate:** reply is classified; every lead ends in one of: `qualified`, `nurture`, `opted_out`, `unresponsive`.

---

## Stage mapping to progress.md

`progress.md` tracks the pipeline funnel. Counts come from:
- **Discovered** = rows in Stage 1 output
- **Collected** = rows in `raw.csv`
- **Verified** = rows in `verified.csv`
- **Outreach** = first touch sent
- **Replies / Qualified** = outreach outcomes

Each count is a single number in `progress.md`; update it whenever a stage gate is passed (see "How to update" in progress.md).

---

## KPIs & targets

| Metric | Target |
|---|---|
| Verification pass rate | ≥ 60% of collected |
| Deliverability (opens / sent) | ≥ 85% |
| Reply rate | ≥ 3–5% of sent |
| Positive reply rate | ≥ 1.5% of sent |
| Meetings booked / qualified | ≥ 1% of sent |
| Weekly verified new leads | ≥ 20 |
| Time from discovery → first touch | ≤ 7 days |

## Compliance notes (GDPR)

- B2B outreach on **legitimate interest** (Art. 6(1)(f) GDPR); document it per lead.
- Every verified row stores source + verification date + consent/opt-out state.
- Opt-outs are recorded and honored permanently — never re-added.
- Provide clear opt-out + identity in every message (Art. 21 objection right).
- No purchasing of lists from non-compliant brokers; all data self-sourced or API-sourced with legitimate-interest basis.
