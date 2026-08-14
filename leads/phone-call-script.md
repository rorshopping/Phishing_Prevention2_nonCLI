# Phone-Call Script — Consent-First Outreach (11 Phone-Route Companies)

**Created:** 2026-08-10 · **Source:** `leads/person-conversion.csv` (phone + LinkedIn columns) · **Consent rules:** `leads/consent-log.md` §1/§3 · **Legal gate:** `leads/tool-stack.md` §1

**Purpose:** First touch by phone for the 11 companies without a confirmed decision-maker email. The **call itself** is lawful under presumed consent for a business call (DE UWG §7(2) Nr. 1 — concrete relevance required; AT/CH permissive for business contact), but **emailing afterwards is only lawful with explicit, logged consent**. This script is built around that consent ask.

**Hard rules (from `consent-log.md`):**
1. The prospect must say **yes to email specifically** — a yes to "sending information", a LinkedIn connection, or "keep me posted" is **not** consent.
2. Log consent **within 24 h** (call date/time, caller, exact wording used, prospect's verbal "yes", call note/recording ref) using the per-lead template in `consent-log.md` §2.
3. Before the **first email**: verify the log record exists, scope still covers the message, no revocation/suppression hit, and (AT only) address not on the RTR ECG list. Fill `{{ConsentSource}}` in the email footer, e.g. `phone consent, 2026-08-10, S. Weber`.
4. No explicit email-consent → **do not email**. Route to LinkedIn follow-up or park (nurture) instead.
5. On any "no" or opt-out → log it, mark DNC, never re-market (Art. 21 GDPR / §7 UWG objection).

---

## 1. Target board (11 companies)

| Company | Country | Decision-maker target | Phone (published) | Direct line / note | LinkedIn |
|---|---|---|---|---|---|
| Saegeling Medizintechnik GmbH | DE | Daniela Saegeling (GF) / Uwe Saegeling (GF) | +49 3529 5626-0 | Zentrale; ask for GF | linkedin.com/in/daniela-saegeling-2550716a / in/uwe-saegeling-b4178919b |
| Schinner Versicherungsmaklerkanzlei GmbH | AT | Dr. Constanze Schinner (GF) | +43 1 71 20 777 | **Direkt -12 (Constanze)** | linkedin.com/in/dr-constanze-schinner-mba-63a428a8 |
| HABEL Medizintechnik GmbH | AT | Markus Schimel (GF) | +43 1 292 66 42 | Zentrale; no LinkedIn → phone-first | — |
| ASKIN&CO GmbH | AT | Ralph Lugbauer (GF) / Mariella Zilahi-Lugbauer / Herbert Lugbauer | +43 1 979 88 44 | Zentrale | at.linkedin.com/in/ralph-lugbauer-bb280b6 |
| Hierzer Maschinenbau GmbH | AT | Gerhard / Christian / Andreas Hierzer (GF) | +43 7226 2242 | Zentrale | at.linkedin.com/in/andreas-hierzer-2b8b2a172 |
| Karl Rottmund Maschinen- und Industrietechnik GmbH | AT | Stevan Jakovljevic (GF, seit 04/2025) | +43 1 8886164 | Zentrale; new owner → fresh contact | — |
| Intecso AG | CH | Hüseyin Sönmez (CEO) | +41 43 500 18 18 | Small MSP — MD answers | linkedin.com/in/hsoenmez |
| SEP IT AG | CH | Urs Philippe (Inhaber/GF) | +41 71 227 40 20 | Zentrale | linkedin.com/in/ursphilippe |
| Biomed AG | CH | Thomas Wirth (CEO) | +41 44 802 16 16 | Zentrale | ch.linkedin.com/in/thomas-wirth-6893532 |
| Robert Ott AG | CH | Robert Ott (GF/Inhaber) | +41 62 769 10 70 | **Direkt 10 71 (Ott)** | ch.linkedin.com/in/robert-ott-991986197 |
| Müller Martini Manufacturing AG | CH | Herbert Wicki (GF) | +41 41 482 62 11 | **Wicki-Direkt 482 62 11**; Zentrale 482 62 62 | ch.linkedin.com/in/herbert-wicki-8941a2211 |

**Country statutes for the call/email:** DE = UWG §7(2) Nr. 1 (call) → §7(2) Nr. 3 (email consent) · AT = TKG §174 (email consent, ECG-list check) · CH = UWG Art. 3(1)(o) / FMG (consent-first practice; no corporate fines under revFADP but criminal risk vs. natural persons).

---

## 2. Call script (German — consent-first)

> Replace `{{LegalEntityName}}` with the operator's registered company name before use. Read the **consent ask verbatim** (step 4).

```
1) OPENING (identify who you are and why you're calling)
   "Guten Tag, mein Name ist {{CallerName}} von {{LegalEntityName}} – wir entwickeln
    PhishDefend AI, eine automatisierte Phishing-Simulation für den Mittelstand.
    Ich habe eine kurze fachliche Frage – störe ich gerade?"

   [Wenn "ja" → "Wann darf ich Sie kurz zurückrufen?" – Termin notieren, auflegen.]

2) RELEVANCE (concrete per-sector hook – 15–30 s)
   "Kurz zum Hintergrund: Seit NIS2/der DSGVO müssen Firmen wie die Ihre nachweisbare
    Sensibilisierungsmaßnahmen gegen Phishing vorweisen – Klickraten und Meldequoten
    gelten als Prüfnachweis. Unsere Software baut solche Kampagnen automatisiert auf,
    ohne eigenes IT-Team. Dürfte ich Ihnen dazu die wichtigsten zwei, drei Punkte
    zuschicken? Eine E-Mail mit einer Kurzübersicht und einer Demovariante – das wäre
    unverbindlich."

   [Sector hooks – choose one:]
   - Healthcare/MedTech (Saegeling, HABEL, Biomed): "gerade im Medizinprodukte-Umfeld
     sind Phishing-Angriffe und Ausfälle ein Haftungsthema (ISO 27001 A.6.3)."
   - Manufacturing (Hierzer, Rottmund, Robert Ott, Müller Martini): "Zulieferer müssen
     ihren Kunden zunehmend Sicherheitsnachweise erbringen (Lieferketten-Anforderungen)."
   - IT services (Intecso, SEP IT): "Sie bauen das Vertrauen Ihrer Kunden auf – da
     wäre ein eigener, automatisierter Awareness-Nachweis auch für Ihr Haus sinnvoll."
   - Insurance (Schinner, ASKIN&CO): "Versicherer fordern zunehmend dokumentierte
     Awareness-Maßnahmen für Deckung und Schadensfall."

3) IDENTIFY THE DECISION MAKER (if not reached)
   "Darf ich fragen, ob ich mit der Geschäftsführung oder dem IT-/Security-Verantwortlichen
    sprechen könnte? Es geht um eine kurze, fachliche Einschätzung."
   [Wenn GF nicht erreichbar: Namen + Durchwahl erfragen, Rückruftermin oder Weiterleitung.]

4) EXPLICIT EMAIL-CONSENT ASK (VERBATIM – per consent-log.md)
   "Darf ich Ihnen dazu eine E-Mail von {{LegalEntityName}} senden?"
   ["May I send you a follow-up email about phishing simulations?" für englische Kontakte]

   ACHTUNG: Ein "Ja, schicken Sie mal was" genügt NICHT. Es muss eine konkrete, aktive
   Zustimmung zur E-Mail sein. Bei Unklarheit nachfragen:
   "Nur damit ich das richtig notiere: Sie sind einverstanden, dass ich Ihnen eine
    E-Mail mit Infos zur Phishing-Simulation an [E-Mail-Adresse nennen] schicke?"

5) YES → capture + log promise
   "Vielen Dank! Ich schicke Ihnen die E-Mail an [Adresse bestätigen lassen].
    Jede E-Mail enthält selbstverständlich einen Abmelde-Link."

6) NO / zurückhaltend → don't push; offer LinkedIn or park
   "Verstanden, kein Problem. Darf ich Ihnen stattdessen auf LinkedIn folgen, damit wir
    in Kontakt bleiben? Ich melde mich dann nicht unaufgefordert per E-Mail."
   [Wenn auch das abgelehnt: danken, als 'nurture' oder 'opted_out' kennzeichnen.]
```

---

## 3. Consent logging — do this BEFORE any email is sent

For every lead that said **yes**, complete the per-lead record from `consent-log.md` §2 **within 24 h**:

| Field | Value (example) |
|---|---|
| Lead | Daniela Saegeling |
| Company | Saegeling Medizintechnik Service- und Vertriebs GmbH |
| Contact email | `[from consent / candidate]` — `[ ]` confirmed role-relevant (named GF) |
| Country | DE |
| Consent type | **Phone** |
| Consent source | Call log YYYY-MM-DD, caller S. Weber, dialer ref #NNN |
| Consent date | YYYY-MM-DD HH:MM |
| Consent scope | [x] told WHO ({{LegalEntityName}} / PhishDefend AI) · [x] told WHAT (phishing simulation) · [x] told HOW (email) · [x] active opt-in, no pre-tick |
| Opt-out offered | [x] verbal at collection · [x] 1-click link in every email |
| SMS/linkedin account | recording/note ref #NNNa: prospect: "ja, schicken Sie mir die E-Mail" |

**Before-every-send checklist (consent-log.md §3, steps 6–8):**
- [ ] Consent record exists and matches the exact email address
- [ ] Scope still covers the message content (own similar products only)
- [ ] No objection/revocation on file (suppression list checked)
- [ ] (AT only) Address NOT on ECG list — `eintragen@ecg.rtr.at` checked {{date}}
- [ ] Email footer `{{ConsentSource}}` filled, e.g. `phone consent, 2026-08-10, S. Weber`
- [ ] Opt-out (1-click) link present in every email

**If consent was NOT obtained (no / LinkedIn-only / parked):**
- Mark `nurture` or `opted_out` in `progress.md`; log the "no" + timestamp (proves burden-of-proof compliance)
- Never add the prospect to any email list; a later written opt-in (e.g. via a signed demo request) resets the state

---

## 4. Notes per company

- **Schinner** — use the direct line **-12** (Constanze Schinner's published direct). LinkedIn profile confirmed (Vizepräsidentin VÖVM → relevant credentials).
- **Robert Ott** — direct **10 71** for Robert Ott; switchboard 10 70. Pattern anchor exists (`d.brechbuehl@robertottag.ch`) → if Ott consents, candidate `r.ott@robertottag.ch` should be verified (MX/MV/Bouncer) before sending.
- **Müller Martini** — Wicki's **direct** number is published on the team page (+41 41 482 62 11); Zentrale 62 62. Role address `mmha-verkauf@mullermartini.com` exists but is not a person → do not cold-mail.
- **HABEL / Rottmund** — no LinkedIn profile found for the MDs; the phone call is the primary (and currently only) direct channel. If email consent is given, verify the pattern-derived candidates first (`m.schimel@habel-medizintechnik.at`?, `s.jakovljevic@rottmund.at`? — **no published pattern anchor; treat as unverified**).
- **Intecso** — 6-person MSP: Hüseyin Sönmez (CEO) is also the technical lead; a single call covers both roles.
- **Biomed** — CEO Thomas Wirth is publicly visible (interviews); LinkedIn-first as an alternative, but phone consent remains the email prerequisite.
- **SEP IT** — GF Urs Philippe is reachable via switchboard; info@sep.ch is masked site-wide, so the phone path is the only email route at present.
- **Saegeling** — Daniela Saegeling took sole operational GF 05/2026; address her, not Uwe (strategic/Übergang).

## 5. Post-call actions

1. Update `leads/consent-log.md` with the lead record (within 24 h).
2. Update `leads/person-conversion.csv` notes with the call outcome (consent granted / LinkedIn only / opted out / DNC).
3. Update `leads/progress.md` funnel counts (Replies / Qualified / Nurture / Opted out).
4. If consent granted but no verified address yet → run the email through the verification stack (`tool-stack.md` §4: MX-check → MillionVerifier → Bouncer) before the first send.
