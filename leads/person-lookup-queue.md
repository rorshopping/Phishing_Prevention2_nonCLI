# Person Lookup Queue — 37 Companies Without a Published Decision-Maker Email

**Created:** 2026-08-10 · **Source:** `leads/person-conversion.csv` (40 companies) minus the 3 that already have a published MD/IT-lead email (RVM Versicherungsmakler GmbH Reutlingen, Volk & Partner, Sumec AG).

**Goal:** convert the remaining role-gated accounts (`info@…`, `kontakt@…`, `office@…`) to a named decision-maker address.

**Lookup paths (per `leads/tool-stack.md` §4 & §1):**
1. **Hunter.io pattern/domain check** — search `<domain>` for the email pattern, then cascade-verify: MX-check (free gate) → MillionVerifier (bulk) → Bouncer (EU catch-all resolution, high-value only). Hunter also exposes the public **source URL** per lead (Art. 14 provenance asset).
2. **LinkedIn search** — non-promotional connection request → after accept, get explicit email consent in-message; log per `leads/consent-log.md` §1 (type "LinkedIn consent") before any send.
3. **Phone consent** — B2B cold call (DE UWG §7(2) Nr. 1 presumes consent *for the call itself*, not for email) → prospect explicitly agrees to an email follow-up → log per `leads/consent-log.md` §1 (type "Phone", incl. call ref + exact wording).

**Legal gate:** in DE/AT/CH there is **no B2B exemption** for cold email — a found/verified address is necessary but not sufficient. For every DE/AT lead an explicit, logged consent (phone or LinkedIn) must exist before the first send; for CH the same standard applies in practice. Companies without a confirmed address in queue can still be contacted by phone/LinkedIn *without* email.

Legend: **[H]** Hunter pattern check on domain · **[LI]** LinkedIn profile (link or search) · **[P]** published switchboard phone for consent call.

---

## Germany (18)

| Company | Target (from person-conversion.csv) | Lookup path | Specifics |
|---|---|---|---|
| IT-HAUS GmbH | Stefan Sicken (MD); Heiko Ulbrich (Head of IT) | **[H]** it-haus.com · **[LI]** linkedin.com/in/stefan-sicken-735b12122 · **[P]** +49 6502 9208-0 | Pattern test `first.last@it-haus.com`; Sicken confirmed MD since 01/2026. Fallback: Marco Barth (IT-Security Mgr), Volker Müller (ISB) |
| ORBIT IT-Solutions GmbH | Tobias Hejna (CEO); Dr. Uwe Alkemper (Head of Security Solutions) | **[H]** orbit.de · **[LI]** search `Tobias Hejna orbit.de` · **[P]** +49 228 95693-0 | Site masks all emails; `Tobias.Hejna@orbit.de` appears in public directory (dievertriebsmanager.de) — **verify via Hunter/MV before use**. Do not email `jobs@orbit.de` |
| NetPlans GmbH | Sascha Collin (GF); Tobias Lang (Abteilungsleiter Cyber Security) | **[H]** netplans.de · **[LI]** search `Sascha Collin NetPlans` · **[P]** +49 7243 3734-0 (Lang direkt -420) | Lang's direct phone is published on the managed-security page → phone-consent path is strongest |
| Nösse Datentechnik GmbH & Co. KG | André Nösse (GF) | **[H]** noesse.de · **[LI]** linkedin.com/in/andré-nösse · **[P]** 02171 700-300 | Small firm (~90) — LinkedIn first, then phone; MD active on LinkedIn |
| comito GmbH | Stefan Soubusta (CEO); Timo Kircher (IT-Berater) | **[H]** comito.de · **[LI]** linkedin.com/in/stefan-soubusta-24690855 · **[P]** 0221 9669 42-00 | CEO is highly active on LinkedIn (posts under CEO role) → strong LI consent path |
| SÜDVERS GmbH | Ralf Bender (CEO); Rolf Störr (IT-Leiter/Digitale Services) | **[H]** suedvers.de · **[LI]** linkedin.com/in/rolf-störr-870b20a8 · **[P]** +49 761 4582-0 | Störr (group IT lead) has both XING + LinkedIn; contact page lists MDs via forms only |
| RCU Versicherungsmakler GmbH | Michael Gick (GF) | **[H]** rcu-versicherungsmakler.de · **[LI]** linkedin.com/in/michael-gick-76b7b865 · **[P]** (02234) 91124-0 | ~12 staff, ETL group — Gick is sole long-running GF (since 2009) |
| ASSON Versicherungs- und Finanzmakler GmbH | Marc Loreth (GF) | **[H]** asson.de · **[LI]** search `Marc Loreth ASSON Kehl` · **[P]** 07851 4821-01 | Family-owned micro-broker — phone-first, MD answers directly |
| Saegeling Medizintechnik Service- und Vertriebs GmbH | Daniela Saegeling (GF) | **[H]** saegeling-mt.de · **[LI]** linkedin.com/in/daniela-saegeling-2550716a · **[P]** 03529 5626-0 | Daniela took sole GF 05/2026 — target her, not Uwe (strategic) |
| Medizintechnik Rostock GmbH (MTR) | Andreas Markschies (GF) | **[H]** mtronline.de · **[LI]** search `Andreas Markschies mtronline` · **[P]** 030 669910-0 | No person profile found → phone-consent first; ask for Markschies |
| Jüttner Orthopädie KG | Frank Jüttner (Inhaber); Lars Jäger (GF Verwaltung) | **[H]** juettner.de · **[LI]** linkedin.com/in/lars-jäger-02694018a · **[P]** 03601 4618-0 | Jäger (GF) is on LinkedIn; Frank Jüttner behind switchboard |
| MEDITECH Sachsen GmbH | Dirk Rauchfuß (GF/CEO); Ramón Skomda (IT-Manager) | **[H]** meditech-sachsen.de · **[LI]** linkedin.com/in/dirk-rauchfuß-bb3a11173 · linkedin.com/in/ramón-skomda-565a02272 · **[P]** 035955 746-600 | Both decision-maker and IT lead have LinkedIn profiles → strong path |
| medika Medizintechnik GmbH | Stefan Weiß (Geschäftsleitung) | **[H]** medika.de · **[LI]** search `Stefan Weiß medika Hof` · **[P]** 09281 7549-0 | No profile found; phone-consent first |
| Teubert Maschinenbau GmbH | Wolfgang Teubert (GF); Philip Teubert (Technik) | **[H]** teubert.de · **[LI]** search `Philip Teubert OR Wolfgang Teubert` · **[P]** +49 7702 4393-0 | Family firm; Philip co-leads Technology (3rd gen) — good IT-adjacent target |
| WEKAL Maschinenbau GmbH | Klaus Degenhardt (GF) | **[H]** wekal.de · **[LI]** linkedin.com/in/klaus-degenhardt-a0b73120b · **[P]** +49 5622 9957-0 | GF on LinkedIn + XING |
| Maschinen- und Metallbau Claaßen GmbH | Manfred Ossevorth (CEO); Johannes Wöste (GF/COO, ex-technischer Leiter) | **[H]** claassen-maschinenbau.de · **[LI]** linkedin.com/in/johannes-wöste-947637250 · **[P]** 04492 91 50 0 | Wöste = CEO-level + technical background — single target covers both roles |
| MEZ GmbH | Georgia Brielmann (GF); Antonio Planinac (Leitung Konstruktion) | **[H]** mez.de · **[LI]** linkedin.com/in/georgia-brielmann-aa931a179 · **[P]** +49 7072 917-0 | GF on LinkedIn; role accounts vertrieb@/kontakt@ must not be mailed without consent |
| Ebel Maschinenbau e.K. | Dagmar Ebel (Inhaberin); Heiko Ebel (GF) | **[H]** ebel-maschinenbau.de · **[LI]** linkedin.com/in/heiko-ebel-b22b47144 · **[P]** 03904 72410-0 | Heiko Ebel (GF) on LinkedIn; Dagmar is registered owner |

---

## Austria (11)

| Company | Target (from person-conversion.csv) | Lookup path | Specifics |
|---|---|---|---|
| base-it GmbH | Gregor Dedl (GF/CEO); Christoph Moser (GF) | **[H]** baseit.at · **[LI]** linkedin.com/in/gregor-dedl-a398b5168 · linkedin.com/in/christoph-moser-14481818 · **[P]** via baseit.at/kontakt | Both GFs have LinkedIn profiles → LI-consent path, then pattern check |
| techbold technology group AG | Gerald Reitmayr (Co-CEO); Fabian Zeeb (CIO) | **[H]** techbold.at · **[LI]** search `Gerald Reitmayr` / `Fabian Zeeb techbold` · **[P]** +43 59 555 | Target **Reitmayr** (active Co-CEO since 04/2025), not Izdebski (now Aufsichtsrat). CIO Zeeb = IT lead |
| SYSco EDV ist Vertrauenssache GmbH | Dipl.-Ing. Peter Wurm (GF) | **[H]** sysco.at · **[LI]** search `Peter Wurm SYSco` · **[P]** +43 7262 62432-0 (Wurm direkt -817) | Wurm's direct phone published on /kontakt → phone-consent path |
| RVM Versicherungsmakler GmbH (Linz, AT) | Günther Grössmann (GF); Mag. Nina Lautner (GF) | **[H]** rvm.at · **[LI]** linkedin.com/in/mag-nina-lautner-9313aa372 · **[P]** +43 732 6596-0 | Lautner (GF seit 11/2024) on LinkedIn; separate legal entity from RVM Reutlingen — do not reuse DE RVM contacts |
| Leading Brokers United Austria GmbH | Alois Schoder (CEO) — design. Nachfolger Tobias Kohl (CEO 04/2027) | **[H]** lbua.at · **[LI]** linkedin.com/in/alois-schoder-538b37166 · linkedin.com/in/tobias-kohl-msc-mba-08a48b1a0 · **[P]** +43 50 58 100 | Schoder = CEO now; Kohl takes over 04/2027 — log both for continuity |
| Schinner Versicherungsmaklerkanzlei GmbH | Dr. Constanze Schinner (GF) | **[H]** schinner.at · **[LI]** search `Constanze Schinner linkedin` · **[P]** via schinner.at/kontakt | Part of HBC Gruppe; GF since 2022, first woman on VÖVM board — LinkedIn search should hit |
| Hellmut Habel Gesellschaft m.b.H. (HABEL Medizintechnik) | Markus Schimel (GF) | **[H]** habel-medizintechnik.at · **[LI]** search `Markus Schimel HABEL` · **[P]** +43 1 292 66 42 | 3rd-gen family MD; no profile found → phone-consent first |
| ASKIN&CO GmbH | Ing. Herbert Lugbauer (GF/Gründer) | **[H]** askin.co.at · **[LI]** search `Herbert Lugbauer OR Ralph Lugbauer ASKIN` · **[P]** +43 1 979 88 44 | Founder hands over to children (Mariella/Ralph) — consider targeting Ralph (2nd gen) |
| Kerkoc GmbH | Dr. Alexander Kerkoc (GF) | **[H]** kerkoc.com / kerkoc.at · **[LI]** search `Alexander Kerkoc Orthopädie` · **[P]** +43 5 08 44 | 3rd-gen family MD; phone-consent path |
| Hierzer Maschinenbau GmbH | Gerhard Hierzer (GF) | **[H]** hierzer.at · **[LI]** search `Gerhard Hierzer OR Christian Hierzer` · **[P]** +43 7226 2242 | Family firm, 3 GF brothers — any of Gerhard/Christian/Andreas |
| Karl Rottmund Maschinen- und Industrietechnik GmbH | Stevan Jakovljevic (GF, seit 04/2025) | **[H]** rottmund.at · **[LI]** search `Stevan Jakovljevic Rottmund` · **[P]** +43 1 8886164 | New owner/GF since 04/2025 — fresh contact, no history to burn |

---

## Switzerland (8)

| Company | Target (from person-conversion.csv) | Lookup path | Specifics |
|---|---|---|---|
| Intecso AG | Hüseyin Sönmez (CEO/GF) | **[H]** intecso.ch · **[LI]** linkedin.com/in/hsoenmez · **[P]** +41 43 500 18 18 | 6-person MSP — MD IS the tech; LinkedIn + phone both direct |
| SEP IT AG | Urs Philippe (Inhaber/GF/VR-Präsident) | **[H]** sep.ch · **[LI]** linkedin.com/in/ursphilippe · **[P]** +41 71 227 40 20 | 3 GF-Partner are themselves IT-System Engineers — Philippe is the senior partner |
| ASSEPRO Brokerage AG | Jon Samuel Plotke (CEO); Roland Fröbel (Leiter IT) | **[H]** assepro.com · **[LI]** search `Jon Plotke OR Roland Fröbel ASSEPRO` · **[P]** via assepro.com/kontakt | Decision-maker email missing — but note advisor **claus.widrig@assepro.com** exists as warm-intro bridge (not for cold mail per consent-log). Part of Ardonagh Group |
| ARTUS Unicon AG | Jens Frank (GF/CSO); Ralph Nyffeler (GF/CFO) | **[H]** artus-gruppe.com / unicon.ch · **[LI]** linkedin.com/in/jens-frank-95914895 · linkedin.com/in/ralph-nyffeler-a6a269106 · **[P]** +41 61 716 90 90 | Both GF have LinkedIn profiles; ARTUS Gruppe is the parent domain |
| Biomed AG | Thomas Wirth (CEO/GL-Vorsitzender) | **[H]** biomed.ch · **[LI]** search `Thomas Wirth Biomed CEO` · **[P]** via biomed.ch/unternehmen | Family-owned (Tschudi); VR-Präsident Walter Hölzle also a candidate |
| Anandic Medical Systems AG | Arash Masoud Tehrani (CEO/VR-Präsident) | **[H]** anandic.com · **[LI]** ch.linkedin.com/in/arash-tehrani-ab4b2aa1 · **[P]** via anandic.com/kontakt | CEO on LinkedIn (also heads Duomed Swiss); now part of Palex Group |
| Müller Martini Manufacturing AG | Herbert Wicki (GF/CEO) | **[H]** mullermartini-manufacturing.ch · **[LI]** search `Herbert Wicki Müller Martini` · **[P]** +41 41 482 62 11 | Phone published on team page; GF quoted in interviews — LinkedIn search likely |
| Robert Ott AG | Robert Ott (GF/CEO/Inhaber) | **[H]** robertottag.ch · **[LI]** ch.linkedin.com/in/robert-ott-991986197 · **[P]** via robertottag.ch/kontakt | CEO/owner on LinkedIn; Leiter Betrieb Lukas Dietiker as ops-adjacent target |

---

## Method notes

- **Run order per company:** Hunter pattern check first (free tier 50 credits/mo covers the whole queue) → MX-check pre-filter → MillionVerifier bulk → Bouncer for the ~10 high-value DACH targets (EU catch-all verdict). Store the Hunter **source URL** per lead (Art. 14 + provenance).
- **Consent before send (DE/AT/CH):** for every address that resolves to a person, obtain consent on LinkedIn or by phone first and log it in `leads/consent-log.md` (type, date, exact wording, channel ref). Found-and-verified ≠ consent. CH has no express-consent statute for one-off B2B email but the same consent-first standard is the safe practice.
- **Do not mail `info@`/`kontakt@`/`jobs@`** as a workaround — generic addresses are protected in DE (OLG Munich 29 U 857/12) and are explicitly rejected by the Stage-3 role-account gate.
- **LinkedIn-only companies (no phone published):** base-it, Schinner, ASSEPRO, Biomed, Anandic, Robert Ott, medika, Teubert, MTR, HABEL, Kerkoc — use the LI-consent path first; the phone column lists the published switchboard where available.
- **Excluded (already have decision-maker email, not in queue):** RVM Versicherungsmakler GmbH (Reutlingen) — thomas.kalbacher@rvm.de / oliver.scholl@rvm.de; Volk & Partner — c.volk@volk-partner.de; Sumec AG — d.schneeberger@sumec.ch.
