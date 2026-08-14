# LinkedIn Scripts — Consent-First Connection & Email-Consent Ask (9 LinkedIn Companies)

**Created:** 2026-08-10 · **Source:** `leads/person-conversion.csv` (linkedin column) · **Consent rules:** `leads/consent-log.md` §1/§3 · **Legal gate:** `leads/tool-stack.md` §1

**Purpose:** LinkedIn-first outreach for the 9 companies where a decision-maker LinkedIn profile is recorded. The connection request is **non-promotional**; **emailing afterwards requires an explicit consent ask in the chat** — a connection alone is **not** consent (AG Düsseldorf, 23 C 120/25: "a LinkedIn connection does not constitute consent to email advertising").

**Hard rules (from `consent-log.md`):**
1. Connection request must be **non-promotional** (no product pitch, no link).
2. After the connection is accepted, ask **explicitly and specifically for email** (see Step 2 verbatim). A "yes to staying in touch" or a connection accept is **not** consent.
3. Log consent within 24 h of the prospect's written reply: type **LinkedIn**, source = message thread link, date, exact wording, prospect's reply text (`consent-log.md` §2).
4. Before the first email: verify the log, scope, no revocation, (AT) ECG list; fill `{{ConsentSource}}` footer, e.g. `LinkedIn consent, 2026-08-10, S. Weber`.
5. No explicit email consent in-chat → **do not email**; park as nurture or keep only the LinkedIn relationship.

---

## 1. Target board (9 companies)

| Company | Country | Decision-maker | LinkedIn profile | Note |
|---|---|---|---|---|
| Schinner Versicherungsmaklerkanzlei GmbH | AT | Dr. Constanze Schinner (GF) | linkedin.com/in/dr-constanze-schinner-mba-63a428a8 | VÖVM-Vizepräsidentin → relevant credentials; part of HBC Gruppe |
| Saegeling Medizintechnik GmbH | DE | Daniela Saegeling (GF) | linkedin.com/in/daniela-saegeling-2550716a | Alleinige GF seit 05/2026 → target her |
| Saegeling Medizintechnik GmbH | DE | Uwe Saegeling (GF, Übergang) | linkedin.com/in/uwe-saegeling-b4178919b | Strategisch/Übergang — secondary |
| ASKIN&CO GmbH | AT | Ing. Mag. (FH) Ralph Lugbauer (GF) | at.linkedin.com/in/ralph-lugbauer-bb280b6 | Managing Partner, 2nd gen — active |
| Hierzer Maschinenbau GmbH | AT | Andreas Hierzer (GF) | at.linkedin.com/in/andreas-hierzer-2b8b2a172 | GF seit 2002; co-GF Gerhard/Christian via phone |
| Intecso AG | CH | Hüseyin Sönmez (CEO) | linkedin.com/in/hsoenmez | CEO = tech lead (6-person MSP) |
| SEP IT AG | CH | Urs Philippe (Inhaber/GF) | linkedin.com/in/ursphilippe | Senior partner; info@sep.ch masked site-wide → LinkedIn is the only non-phone route |
| Biomed AG | CH | Thomas Wirth (CEO) | ch.linkedin.com/in/thomas-wirth-6893532 | Publicly visible (interviews) |
| Robert Ott AG | CH | Robert Ott (GF/Inhaber) | ch.linkedin.com/in/robert-ott-991986197 | Seetalfertigung/SMM press presence |
| Müller Martini Manufacturing AG | CH | Herbert Wicki (GF) | ch.linkedin.com/in/herbert-wicki-8941a2211 | Quoted in interviews; company posts tag him |

---

## 2. Step 1 — Connection request (non-promotional, max 300 chars)

> No product pitch, no links, no "I'd like to add you to my network". Reference a **neutral professional reason** tied to the person's own public activity.

```
Guten Tag Frau/Herr {{Nachname}},

wir sind gerade dabei, für den Mittelstand eine automatisierte Phishing-Simulation
aufzubauen. Da Sie {{Sektor-Hook}} verantworten, würde ich mich freuen, in Ihrem Netzwerk
zu sein – nicht mehr, nicht weniger.

Beste Grüße
{{CallerName}} — {{LegalEntityName}} / PhishDefend AI
```

**Sektor-Hooks (one line, neutral):**
- **Schinner / ASKIN&CO** (Versicherung): „im Bereich Versicherungs- und Risikoberatung" · (Schinner zusätzlich: „als Vizepräsidentin des VÖVM")
- **Saegeling / Biomed** (Gesundheit/Medizin): „im Medizinprodukte-Umfeld"
- **Hierzer / Robert Ott / Müller Martini** (Fertigung): „im Maschinen- und Fertigungsbereich"
- **Intecso / SEP IT** (IT-Dienstleistung): „als IT-Dienstleister für KMU"

> Personen aus **CH** (Sönmez, Philippe, Wirth, Ott, Wicki) können auch auf Englisch angeschrieben werden:
> "Dear Ms./Mr. {{Nachname}}, we're building an automated phishing-simulation platform for
> SMEs. Since you lead {{Sektor}} at {{Firma}}, I'd appreciate being part of your network.
> Best regards, {{CallerName}} — {{LegalEntityName}} / PhishDefend AI"

---

## 3. Step 2 — After acceptance: explicit email-consent ask (VERBATIM)

> Send this **only after** the connection is accepted. The ask is for **email specifically**, with scope (WHO/WHAT/HOW) and opt-out, per `consent-log.md` §1 (type "LinkedIn consent").

```
Vielen Dank für die Vernetzung, Frau/Herr {{Nachname}}!

Kurz und konkret: Für Unternehmen wie Ihres ist der Nachweis von Sensibilisierungsmaßnahmen
gegen Phishing inzwischen ein Prüfpunkt (NIS2 / ISO 27001 A.6.3 / DSGVO Art. 32). Wir bauen
dafür automatisierte Phishing-Simulationen mit messbaren Klick- und Meldequoten.

Darf ich Ihnen dazu eine E-Mail von {{LegalEntityName}} senden? Sie enthielte eine
Kurzübersicht und eine Demo-Variante – selbstverständlich mit Abmelde-Link.
[englisch: "May I send you a follow-up email about phishing simulations from
{{LegalEntityName}}? It would contain a short overview and a demo option – with an
opt-out link, of course."]

Nur zur Sicherheit: Ich meine ausdrücklich die E-Mail – die Vernetzung allein ist für
mich noch keine Zustimmung. Sie müssen nur kurz „ja" schreiben, dann schicke ich sie los.
```

**Acceptable reply (consent):** a written **"ja"** / "ja, schicken Sie" / "yes, please" — explicit and specific to the email.
**NOT consent:** connection accept, "keep in touch", "schauen wir mal", silence. Treat as nurture; do not email.

---

## 4. Step 3 — Consent logging BEFORE any email (consent-log.md §2, type = LinkedIn)

Complete a per-lead record within 24 h of the prospect's written yes:

| Field | Value (example) |
|---|---|
| Lead | Daniela Saegeling |
| Company | Saegeling Medizintechnik Service- und Vertriebs GmbH |
| Contact email | `[from consent or candidate, to be verified]` — `[ ]` confirmed role-relevant (named GF) |
| Country | DE |
| Consent type | **LinkedIn** |
| Consent source | Thread: linkedin.com/in/daniela-saegeling-2550716a — message of {{date}} |
| Consent date | {{YYYY-MM-DD}} |
| Consent scope | [x] told WHO ({{LegalEntityName}} / PhishDefend AI) · [x] told WHAT (phishing simulation) · [x] told HOW (email) · [x] active opt-in, no pre-tick |
| Opt-out offered | [x] opt-out/1-click announced in the ask · [x] link in every email |
| SMS/linkedin account | Thread-URL + prospect reply text saved |

**Before-every-send checklist (consent-log.md §3, steps 6–8):**
- [ ] Consent record exists and matches the exact email address
- [ ] Scope still covers the message content (own similar products only)
- [ ] No objection/revocation on file (suppression list checked)
- [ ] (AT only) Address NOT on RTR ECG list — `eintragen@ecg.rtr.at` checked {{date}}
- [ ] Email footer `{{ConsentSource}}` filled, e.g. `LinkedIn consent, 2026-08-10, S. Weber`
- [ ] Opt-out (1-click) link present in every email

**No consent in-chat →** park as `nurture` in `progress.md`; keep only the connection. Optionally offer a phone call (see `leads/phone-call-script.md`) — phone consent is a separate, equally valid route.

---

## 5. Per-company notes

- **Schinner** — mention VÖVM-Vizepräsidentschaft as the relevance hook; HBC-Gruppe context. Direct phone -12 also available (phone-call-script).
- **Saegeling** — address **Daniela** (sole operational GF since 05/2026); keep Uwe as fallback. If she consents, candidate email `d.saegeling@saegeling-mt.de` must be verified via the stack first (no published pattern anchor on the domain).
- **ASKIN&CO** — Ralph Lugbauer is the active 2nd-gen Managing Partner; Mariella/Herbert via phone. No person email published → verify any candidate before send.
- **Hierzer** — Andreas is the LinkedIn-active GF; co-GFs Christian/Gerhard only via phone (no profiles).
- **Intecso** — one message covers CEO + tech lead; MD replies fast (6-person firm). Role addresses info@/support@intecso.ch exist but are not persons.
- **SEP IT** — LinkedIn is the **only** non-phone email route (info@sep.ch masked). Philippe's partners (Marc/Benjamin Bregenzer) are the tech leads.
- **Biomed** — Thomas Wirth is publicly quoted; company LinkedIn (biomed-ag) active — good pre-message research. info@biomed.ch is role-only.
- **Robert Ott** — Robert Ott posts/share Seetalfertigung/SMM content; mention that as the hook. Pattern anchor `d.brechbuehl@robertottag.ch` exists → candidate `r.ott@robertottag.ch` verifiable before send.
- **Müller Martini** — Herbert Wicki is tagged in company posts (LinkedIn); a comment-then-connect approach fits his public profile. Role email `mmha-verkauf@mullermartini.com` is not a person.

## 6. Do-nots

- ❌ Never send the product pitch in the connection request (promotional requests get rejected and are poor consent material).
- ❌ Never treat the connection itself as consent (AG Düsseldorf 23 C 120/25).
- ❌ Never mail before the consent record is logged and the address verified.
- ❌ Never follow an unaccepted request with a second pitch message — park or move to the phone route.
