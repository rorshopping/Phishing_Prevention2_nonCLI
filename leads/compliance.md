# B2B Cold Email Compliance Reference

Research as of **2026-08-10**. Informational only — not legal advice. Verify with local counsel before launching campaigns.

**Bottom line across all four jurisdictions:** there is **no blanket "B2B exemption"** for unsolicited commercial email in Germany or Austria (and Switzerland is only moderately more permissive). The US (CAN-SPAM) is an **opt-out** regime; the EU/DACH jurisdictions are effectively **opt-in** regimes. Data-processing law (GDPR / nFADP) and marketing law (UWG / TKG / ePrivacy) are **two separate assessments** — a GDPR-compliant prospect list does not legalize the cold email itself.

---

## 1. EU baseline — ePrivacy Directive 2002/58/EC, Art. 13

Transposed nationally (DE: §7 UWG + §25 TDDDG; AT: §174 TKG 2021). Key rules:

- **Art. 13(1):** Email direct marketing only allowed with the recipient's **prior consent** (opt-in).
- **Art. 13(2) (soft opt-in):** No consent needed only if *all* of the following hold:
  1. contact details obtained **in the context of a sale of a product or service**;
  2. marketing is for the sender's **own similar** products/services (narrowly interpreted);
  3. opt-out opportunity given clearly at collection; and
  4. opt-out opportunity given with **each subsequent message**.
- **Art. 13(4):** It is *always* prohibited to disguise or conceal the sender's identity or to send without a **valid address** for opt-out requests.
- **Art. 13(5):** Opt-in applies to natural persons; Member States must protect the interests of **legal persons (businesses)** — this is where national differences arise (DE/AT: no B2B carve-out; UK PECR: corporate-subscriber carve-out).

**CJEU Case C-654/23 (Nov 2025)** — two holdings relevant to B2B:
1. A **free account/freemium/trial registration** can qualify as a "sale" for the soft opt-in (e.g., SaaS free-tier users can be marketed paid plans, similar products only).
2. When ePrivacy Art. 13(2) applies, the GDPR **Art. 6(1) legal-basis requirement does not apply** (via Art. 95 GDPR) — a separate GDPR lawful basis (consent or legitimate interest) is not additionally required for the sending itself. (Still debated whether GDPR sanctions apply in parallel where national marketing law is breached.)

---

## 2. Germany

### Framework
- **UWG §7(2) No. 2** (implementing ePrivacy): email advertising without **prior express consent** is per se "unreasonable harassment" — **applies identically to B2B and B2C**. No B2B exemption. Generic addresses (`info@`, `kontakt@`) are equally protected (OLG Munich 29 U 857/12).
- **§7(3) UWG — existing-customer (soft opt-in) exception.** All five conditions required:
  1. email address obtained **in connection with the sale of goods/services** (a mere account, quote request, or pre-contractual contact is *not* enough);
  2. marketing only for the sender's **own similar** products/services (no cross-selling; "similar" read strictly — interchangeable / same need);
  3. recipient has **not objected** (objections must be recorded; even verbal objection counts — AG Munich 142 C 1633/22);
  4. clear, distinct notice of the opt-out right **at collection and in every email**;
  5. opt-out free of charge except base-tariff transmission costs, via a clear contact/unsubscribe link.
- **§25 TDDDG** implements the cookie/communication-side ePrivacy rules.
- **Data processing:** GDPR applies (BDSG supplements). B2B contact data (incl. `vorname.nachname@firma.de`) is personal data. Art. 6(1)(f) **legitimate interest** can ground building/holding the prospect database, but **does not authorize sending** the email — UWG §7 governs that separately.

### Consent specifics (German courts are strict)
- Consent must be voluntary, specific, informed, unambiguous (GDPR standard). Recipient must know: (1) **who** is sending, (2) **which products/services**, (3) **by which channel**.
- **Double opt-in is the de facto standard** to prove consent — single opt-in is insufficient to discharge the sender's burden of proof (BGH I ZR 164/09; I ZR 218/07).
- A LinkedIn connection, XING contact, published business email, or trade-fair directory listing is **not** consent (AG Düsseldorf 23 C 120/25, Nov 2025). An unsubscribe link does **not** cure missing consent.
- Compliant cold-channel pattern: B2B **cold call** under UWG §7(2) No. 1 (**presumed consent** for businesses with concrete relevance) or a non-promotional LinkedIn message, then log the prospect's **explicit email-consent** (timestamp, scope, source) before the email fires.

### Required elements in every marketing email (if lawful)
- **Sender identity:** full legal name + **Impressum** (legal notice: registered office, HRB/register number, VAT ID where required, managing director, contact).
- **Opt-out:** clear, free, functional 1-click unsubscribe (plus any format prescribed by the consent scope).
- No deceptive/missing `From`, no concealed identity; valid reply address.

### Enforcement / risk
- **Abmahnung** (cease-and-desist) by competitors or the Wettbewerbszentrale — injunctive relief covering the whole practice, plus warning-fee reimbursement.
- UWG fines up to **€300,000**; GDPR fines up to **€20m / 4% global turnover**.
- Risk of repetition presumed after one violation; typically requires a penalty-clause cease-and-desist declaration.

---

## 3. Austria

### Framework
- **§174 TKG 2021** (successor to §107 TKG 2003) — implementing ePrivacy. **Abs. 3:** sending electronic mail (email, SMS, MMS) for **direct-advertising purposes without prior consent is prohibited** — **identically for B2B and B2C**, no business exemption. Applies extraterritorially where the message is *received* in Austria (Abs. 6).
- **§174 Abs. 4 TKG — existing-customer exception**, all four conditions:
  1. contact info obtained in connection with a **sale or service** to the customer;
  2. message is direct advertising of the sender's **own similar** products/services;
  3. customer was given a clear, distinct, free, easy opt-out **at collection and with each message**; and
  4. customer has **not pre-refused** — in particular must check the **ECG opt-out list** (E-Commerce-Gesetz §7(2); maintained by RTR — the "Robinson list" for email). Even with all other conditions met, never send to an address on the ECG list.
- **§174 Abs. 5 TKG:** always prohibited to conceal sender identity or send without an **authentic address** for opt-out requests; anonymous email banned.
- **§6(1) ECG:** advertising email must be **recognizable as advertising** (e.g., marked in the subject line).
- **Data processing:** GDPR + Austrian DSG. "Legitimate interest" under Art. 6(1)(f) rarely succeeds for unsolicited B2B email in Austria (stricter than in some other DACH readings).

### Consent specifics
- Consent = free, specific, informed, unambiguous (Art. 4(11) GDPR standard). Practically: **double opt-in** with documented timestamp + IP hash; burden of proof on the sender.
- Not consent: business card at a networking event, imprint/Firmenbuch address, pre-ticked box, blanket terms-of-service clause, webinar signup auto-enrolled in newsletter, LinkedIn connection.
- A single email suffices for a violation. **Mixed messages are risky:** adding promotional content to contractual/onboarding/welcome emails violates §174 TKG even with an existing relationship (BVwG 24 May 2024, W271 2269889-1) — keep transactional and marketing content strictly separate.

### Required elements in every marketing email
- **Sender identity:** full, non-disguised sender; real sending address (not anonymous); valid reply/opt-out address.
- **Opt-out:** free, easy mechanism in every message; maintain a permanent suppression list.
- **Advertising label** recognizable as such (subject line recommended).

### Enforcement / risk
- Administrative fines under **§188 TKG**: spam email/SMS up to **€50,000 per violation**; cold calls/fax up to **€100,000**; anonymity/concealment up to **€50,000**. Enforced by the Telekom-Control (Fernmeldebüro / RTR).
- Parallel **UWG §7** claims by competitors or the VKI: injunctive relief + costs; typical dispute values **€5,000–30,000**.
- DSB (data-protection authority) checks consent documentation under GDPR.

---

## 4. Switzerland

### Framework (not EU/EEA — GDPR does not apply)
- **revFADP / nFADP** (revised Federal Act on Data Protection, in force **1 Sept 2023**) governs data processing. Business email addresses that identify a person (`firstname.lastname@company.ch`) are **personal data** (Art. 5 nFADP). Legal basis under **Art. 31 revFADP** (more narrowly worded than GDPR Art. 6(1)(f)). Adequacy with the EU recognized by the Commission. Supervisor: **FDPIC** (EDÖB).
- **UWG Art. 3(1)(o)** (Federal Act Against Unfair Competition / UCA) is the anti-spam rule: **mass advertising via telecommunications (email, SMS) requires the recipient's prior express consent (opt-in)** — with a soft opt-in exception for existing customers (similar products only, opt-out offered at collection).
- **FMG** (Telecommunications Act) supplies the ePrivacy-type layer.

### B2B nuance (important)
- UCA Art. 3(1)(o) formally applies to B2B and B2C alike (no explicit carve-out), **but** FDPIC/SECO guidance reads it as targeting **bulk consumer marketing**. **Targeted, role-relevant B2B outreach** to a business contact at a corporate domain, with an **identifiable sender and clear opt-out**, is generally treated as **outside the abusive mass-marketing scope**. This makes Switzerland the most permissive of the three DACH jurisdictions for genuinely targeted B2B cold email.
- Legitimate interest (nFADP Art. 31) is a recognized basis for B2B prospecting where professionally relevant, but must be **documented** (purpose, necessity, balancing).
- Consent to a soft opt-in, existing-customer email requires a **completed sale or service** — a mere online account is not enough.

### Required elements in every marketing email
- **Sender identity:** full company name, registered address, working reply path.
- **Opt-out:** simple, clearly visible, **free-of-charge** unsubscribe in every message (one-click link or unsubscribe page; may not require unsubscribing by phone/post). Honor promptly (industry norm ~10 business days).
- No deceptive/misleading subject line or sender.

### Consent specifics / practice
- Consent must be free and informed (unticked checkbox; accepting general terms is not consent); revocable at any time.
- Double opt-in **not formally required** but strongly recommended — the sender bears the burden of proving consent.
- Document consent (who, when, via which form, wording). Privacy policy must cover marketing processing (Art. 19 nFADP duty to inform).

### Enforcement / risk
- **FDPIC** enforcement; criminal fines for privacy violations up to **CHF 250,000** (individual criminal liability), plus civil orders.
- UCA claims by competitors/consumer organizations (injunctive relief, costs).
- Cold **calls**: allowed under "presumed consent" if directly relevant to the prospect's business — but must respect the **Robinson list** (numbers marked `*` in the directory = do not call).

---

## 5. United States — CAN-SPAM Act (2003) + 16 CFR Part 316

### Model: opt-out, not opt-in
- **No consent required** to send — you may send until the recipient opts out. Applies to **all commercial messages**, **no B2B exception**, single or bulk.
- "Commercial message" = primary purpose is advertising/promotion of a product, service, or commercial website. Transactional/relationship messages are exempt from the ad-label and opt-out duties but **not** from header-accuracy rules.

### Required elements in every commercial email
1. **Accurate header/`From` info** — no false, misleading, or concealed transmission information.
2. **Non-deceptive subject line**.
3. **Ad identification** — clear and conspicuous that the message is an advertisement/solicitation (not required if prior affirmative consent given).
4. **Valid physical postal address** — street address, USPS-registered PO box, or registered commercial mailbox.
5. **Clear and conspicuous opt-out notice** with a working mechanism — a functioning return address or single web page; must process requests for **≥ 30 days after send**.
6. **Honor opt-outs within 10 business days**; no fee, no identity info beyond the email address, no extra steps beyond reply-email or one web page (16 CFR §316.5). After opt-out: stop sending **and do not sell/transfer the address** (except to a compliance vendor).
7. **Label sexually explicit content** as "SEXUALLY-EXPLICIT:" (16 CFR §316.4).

### Enforcement / risk
- FTC + state AGs + ISPs; penalties per violation (adjusted annually; ~**$51,000+ per email** in 2026), aggravated violations (harvesting, dictionary attacks, open relays) can triple.
- No private right of action for recipients, but state-law and ISP enforcement is real.
- Opt-out obligation attaches to the "sender" (the party whose product is advertised and who is in the `From` line); multi-marketer emails may designate a single sender.

---

## 6. Comparison table

| Requirement | Germany | Austria | Switzerland | US (CAN-SPAM) |
|---|---|---|---|---|
| Consent model | Opt-in (no B2B exemption) | Opt-in (no B2B exemption) | Opt-in for bulk; targeted B2B tolerated | Opt-out |
| Sender identity | Full identity + **Impressum** | Full, non-anonymous sender | Company name + address + reply path | Accurate header/`From`; physical postal address |
| Opt-out required | Yes, every email, 1-click, free | Yes, every email, free + easy; ECG list check | Yes, every email, simple + free | Yes, clear + conspicuous, honored ≤10 business days |
| Existing-customer soft opt-in | §7(3) UWG (5 conditions) | §174(4) TKG (4 conditions + ECG list) | UCA Art. 3(1)(o) (similar products, opt-out at collection) | N/A (no consent needed) |
| Legitimate interest | Data processing only (Art. 6(1)(f)); not a send basis | Rarely accepted for unsolicited email | nFADP Art. 31; workable for targeted B2B | N/A |
| Double opt-in | De facto required to prove consent | De facto required | Recommended, not required | Not applicable |
| Max penalties | UWG €300k; GDPR €20m/4% | TKG €50k/violation (calls €100k) | nFADP up to CHF 250k (criminal) + orders | ~$51k+ per email (FTC) |

---

## 7. Global required-elements checklist (apply to every send)

- [ ] Sender identity is truthful and non-disguised (no spoofed `From`, no concealed headers).
- [ ] For DE/AT: full legal Impressum; for US: valid physical postal address; for CH: company name + registered address + reply path.
- [ ] Working, visible, free opt-out/unsubscribe in **every** email (1-click where possible).
- [ ] Opt-outs honored promptly (US: 10 business days; EU/CH: immediate/short, suppress permanently).
- [ ] Marketing nature recognizable (subject/ad label; CH + AT expressly require identification as advertising).
- [ ] EU/AT/DE: consent documented (source, timestamp, scope, wording) — double opt-in where possible.
- [ ] AT: ECG-list suppression check; CH: Robinson-list check for any calling.
- [ ] Legal basis for data processing separate from legal basis for sending (GDPR Art. 6(1)(f) vs UWG/TKG/ePrivacy).
- [ ] Transactional/contractual emails kept free of promotional content (BVwG rule; CJEU C-654/23 risk area).
- [ ] Suppression list maintained and re-used; no re-marketing after objection.
- [ ] Tracking pixels/beacons: increasingly treated like cookies — require separate consent (esp. DE, FR-style DPA guidance).

---

## 8. Primary sources

- ePrivacy Directive 2002/58/EC, Art. 13 (as amended 2009/136/EC) — EUR-Lex `32002L0058`.
- CJEU Case C-654/23 (Nov 2025) — free-account "sale"; Art. 95 GDPR blocking effect.
- Germany: UWG §7 (gesetze-im-internet.de `uwg_2004/__7.html`); §25 TDDDG; BGH I ZR 164/09, I ZR 218/07; OLG Munich 29 U 857/12; AG Düsseldorf 23 C 120/25.
- Austria: TKG 2021 §174, §188 (RIS `bgbl/i/2021/190/P174`); ECG §6, §7(2) (RTR ECG list); BVwG 24.05.2024 W271 2269889-1; UWG §7.
- Switzerland: revFADP/nFADP (in force 1 Sept 2023, AS 2022 491); UCA/UWG Art. 3(1)(o); FMG; FDPIC/EDÖB guidance (edoeb.admin.ch "Advertising & marketing").
- US: CAN-SPAM Act, 15 U.S.C. §§7701–7713; CAN-SPAM Rule, 16 CFR Part 316; FTC Compliance Guide for Business (ftc.gov).
