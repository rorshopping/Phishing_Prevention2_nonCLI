# ICP Research — Prospect Company List (DACH KMU)

**Status:** Draft v1 · 2026-08-10
**Method:** Desk research, sector lists, company registries (firmenwissen.de). Sizes are public estimates — verify on Bundesanzeiger before outreach.
**Purpose:** Stage 0/1 input for the pipeline (`leads/pipeline.md`). Feeds `leads/discovery.py`, which crawls the contact/impressum pages below and writes public business emails to `leads/raw-contacts.csv`.

---

## ICP summary (from `leads/pipeline.md` §Stage 0)

| Attribute | Value |
|---|---|
| Company size | 10–500 employees (European SMEs / KMU) |
| Geography | Germany first, then DACH/EU |
| Decision makers | MD, IT lead, Datenschutzbeauftragte, HR lead, small-company CISO |
| Industry focus | No dedicated security team |
| Pain | Manual phishing campaigns + GDPR/NIS2 evidence |
| Exclusions | >500 emp, existing security team / KnowBe4-style platform, competitors |

**Sector rationale:** NIS2 scope (in force Oct 2024) covers health, digital providers (hosting/telecom/MSP), energy, transport, food. These mid-size operators must now document security-awareness measures (Art. 21) — PhishDefend AI's exact value prop.

---

## Discovery targets

*One domain per line. `leads/discovery.py` parses this section; rows are deduplicated against `leads/raw-contacts.csv`.*

| Domain | Company | Sector | Size (est.) | NIS2 relevance |
|---|---|---|---|---|
| medatixx.de | medatixx GmbH (Bad Camberg) | Healthcare IT (practice software) | ~300 | Health — in scope |
| netcup.de | netcup GmbH (Karlsruhe) | Hosting / cloud infrastructure | ~150 | Digital provider — in scope |
| hetzner.com | Hetzner Online GmbH (Gunzenhausen) | Hosting / cloud | ~350 | Digital provider — in scope |
| sipgate.de | sipgate GmbH (Düsseldorf) | Telecom / cloud telephony | ~200 | Digital provider — in scope |
| easybell.de | easybell GmbH (Berlin) | VoIP provider | ~50 | Digital provider — in scope |
| all-inkl.com | all-inkl.com GmbH (Leipzig) | Web hosting | ~50 | Digital provider — in scope |
| dogado.de | dogado GmbH (Dortmund) | Managed cloud / hosting | ~50 | Digital provider — in scope |
| manitu.de | manitu GmbH (St. Wendel) | Web hosting | ~40 | Digital provider — in scope |
| shopware.com | shopware AG (Schöppingen) | E-commerce software | ~300 | Software vendor — digital |
| tado.com | tado GmbH (Munich) | Smart home / IoT | ~200 | IoT — digital |
| roboception.de | roboception GmbH (Munich) | Robotics perception software | ~50 | Software vendor — digital |
| swu.de | Stadtwerke Ulm/Neu-Ulm GmbH | Municipal energy | ~600 (boundary) | Energy — in scope (boundary case) |
| it-haus.com | IT-HAUS GmbH (Föhren/RP) | IT services / system house | ~400 | Digital provider — in scope |
| orbit.de | ORBIT IT-Solutions GmbH (Bonn) | IT services / system house | ~350 | Digital provider — in scope |
| netplans.de | NetPlans GmbH (Ettlingen) | IT services / system house | ~400 | Digital provider — in scope |
| noesse.de | Nösse Datentechnik GmbH & Co. KG (Leverkusen) | IT services / system house | ~90 | Digital provider — in scope |
| comito.de | comito GmbH (Köln) | IT services / system house | ~50–100 | Digital provider — in scope |
| suedvers.de | SÜDVERS GmbH (München/Hamburg) | Finance / insurance broker | ~635 (boundary) | Financial — in scope (DORA) |
| rvm.de | RVM Versicherungsmakler GmbH (Reutlingen) | Finance / insurance broker | ~370 | Financial — in scope (DORA) |
| rcu-versicherungsmakler.de | RCU Versicherungsmakler GmbH (Frechen/Köln, ETL-Gruppe) | Finance / insurance broker | n/a (ETL-Gruppe) | Financial — in scope (DORA) |
| volk-partner.de | Volk & Partner (Haslach i.K.) | Finance / insurance broker | family-owned | Financial — in scope (DORA) |
| asson.de | ASSON Versicherungs- und Finanzmakler GmbH (Kehl) | Finance / insurance broker | small | Financial — in scope (DORA) |
| saegeling-mt.de | Saegeling Medizintechnik Service- und Vertriebs GmbH (Heidenau) | Healthcare / MedTech | ~135 | Health — in scope |
| mtronline.de | Medizintechnik Rostock GmbH (Rostock) | Healthcare / MedTech | ~200 | Health — in scope |
| juettner.de | Jüttner Orthopädie KG (Mühlhausen, 25 Standorte) | Healthcare / MedTech | ~310 | Health — in scope |
| meditech-sachsen.de | MEDITECH Sachsen GmbH (Pulsnitz/Dresden) | Healthcare / MedTech | 300+ | Health — in scope |
| medika.de | medika Medizintechnik GmbH (Hof) | Healthcare / MedTech | ~200 | Health — in scope |
| teubert.de | Teubert Maschinenbau GmbH (Blumberg) | Manufacturing / machinery | ~115 | Manufacturing — supply chain |
| wekal.de | WEKAL Maschinenbau GmbH (Fritzlar) | Manufacturing / machinery | ~200 | Manufacturing — supply chain |
| claassen-maschinenbau.de | Maschinen- und Metallbau Claaßen GmbH (Saterland) | Manufacturing / machinery | ~280 | Manufacturing — supply chain |
| mez.de | MEZ GmbH (Reutlingen) | Manufacturing / machinery | ~100 | Manufacturing — supply chain |
| ebel-maschinenbau.de | Ebel Maschinenbau (Haldensleben) | Manufacturing / machinery | ~100 | Manufacturing — supply chain |
| baseit.at | base-it GmbH (Ansfelden, AT) | IT services / system house | ~150 | Digital provider — in scope |
| techbold.at | techbold GmbH (Wien, AT) | IT services / system house | ~170 | Digital provider — in scope |
| sysco.at | SYSco EDV GmbH (OÖ, AT) | IT services / system house | ~54 | Digital provider — in scope |
| intecso.ch | Intecso AG (Glattbrugg, CH) | IT services / MSP | ~40 | Digital provider — in scope |
| sep.ch | SEP IT AG (St. Gallen, CH) | IT services / system house | ~30 | Digital provider — in scope |
| rvm.at | RVM Versicherungsmakler GmbH (Linz, AT) | Finance / insurance broker | ~110 | Financial — in scope (DORA) |
| lbua.at | Leading Brokers United Austria (AT) | Finance / insurance network | ~150–250 | Financial — in scope (DORA) |
| schinner.at | Schinner Versicherungsmaklerkanzlei GmbH (Wien, AT) | Finance / insurance broker | ~20 | Financial — in scope (DORA) |
| assepro.com | ASSEPRO (CH) | Finance / insurance broker | ~200 | Financial — in scope (DORA) |
| unicon.ch | ARTUS Unicon AG (Reinach, CH) | Finance / insurance broker | ~40 | Financial — in scope (DORA) |
| habel-medizintechnik.at | HABEL Medizintechnik (Wien, AT) | Healthcare / MedTech | ~80 | Health — in scope |
| askin.co.at | ASKIN&CO (Wien, AT) | Healthcare / MedTech | ~85 | Health — in scope |
| kerkoc.com | Kerkoc GmbH (Wien, AT) | Healthcare / orthopaedics | ~80 | Health — in scope |
| biomed.ch | Biomed AG (Dübendorf, CH) | Healthcare / MedTech | ~60 | Health — in scope |
| anandic.com | Anandic AG (Feuerthalen, CH) | Healthcare / MedTech | ~100 | Health — in scope |
| hierzer.at | Hierzer GmbH (Wilhering, AT) | Manufacturing / steel & machine | ~50 | Manufacturing — supply chain |
| rottmund.at | Rottmund Maschinenbau (Wien, AT) | Manufacturing / machining | ~40 | Manufacturing — supply chain |
| mullermartini-manufacturing.ch | Müller Martini Manufacturing (Hasle, CH) | Manufacturing / machine parts | ~140 | Manufacturing — supply chain |
| robertottag.ch | Robert Ott AG (CH) | Manufacturing / CNC | ~120 | Manufacturing — supply chain |
| sumec.ch | Sumec AG (Biberist, CH) | Manufacturing / machine & plant | ~50 | Manufacturing — supply chain |
| gericke-spedition.de | Gericke Spedition (Hohenstein-Ernstthal) | Logistics / transport | ~150 | Transport — in scope |
| ttm.de | TTM GmbH (Mannheim/Leipzig) | Logistics / transport | ~160 | Transport — in scope |
| transport-betz.de | Transport Betz Gruppe (Malsch/Baden) | Logistics / transport | ~99 | Transport — in scope |
| meidel-gruppe.de | Meidel-Gruppe (Markt Einersheim) | Logistics / transport | ~200 | Transport — in scope |
| spedition-eggers.de | Eggers Spedition GmbH (Lebensmittel-Logistik) | Logistics / transport | ~150 | Transport — in scope |
| ritter-trans.at | Ritter Trans GmbH (Loipersdorf/Theresienfeld, AT) | Logistics / transport | ~125 | Transport — in scope |
| k-logistics.at | K-Logistics (AT) | Logistics / transport | 100+ | Transport — in scope |
| saexinger.at | Saexinger Gefahrgutlogistik (Wien/Ennsdorf, AT) | Logistics / transport | n/a (mittelständisch) | Transport — in scope |
| tisa.ch | TISA Speditions AG (St. Margrethen, CH) | Logistics / transport | ~100 | Transport — in scope |
| schneider-transport.com | Schneider Gruppe (Basel, CH) | Logistics / transport | n/a (mittelständisch) | Transport — in scope |
| oppenlaender.de | Oppenländer Rechtsanwälte (Stuttgart) | Legal / law firm | ~90 lawyers | Legal — GDPR & NIS2-adjacent |
| sza.de | SZA Schilling Zutt & Anschütz (Mannheim) | Legal / law firm | ~60 lawyers | Legal — GDPR & NIS2-adjacent |
| arqis.com | ARQIS Rechtsanwälte (Düsseldorf/München/Tokio) | Legal / law firm | ~80 lawyers | Legal — GDPR & NIS2-adjacent |
| cbh.de | CBH Rechtsanwälte (Köln) | Legal / law firm | ~100 lawyers | Legal — GDPR & NIS2-adjacent |
| pitkowitz.com | Pitkowitz & Partners (Wien, AT) | Legal / law firm | ~30 lawyers | Legal — GDPR & NIS2-adjacent |
| metzler.law | Metzler Rechtsanwälte (Linz, AT) | Legal / law firm | ~25 lawyers | Legal — GDPR & NIS2-adjacent |
| bindergroesswang.at | Binder Grösswang (Wien/Innsbruck, AT) | Legal / law firm | ~125 lawyers | Legal — GDPR & NIS2-adjacent |
| bratschi.ch | Bratschi AG (7 Standorte, CH) | Legal / law firm | ~120 lawyers | Legal — GDPR & NIS2-adjacent |
| wenger-plattner.ch | Wenger Plattner (Basel/Zürich/Bern, CH) | Legal / law firm | ~100 staff | Legal — GDPR & NIS2-adjacent |
| lclaw.ch | Lenz Caemmerer (Basel/Karlsruhe, CH) | Legal / law firm | ~45 lawyers | Legal — GDPR & NIS2-adjacent |
| kembit.nl | KEMBIT (Wijnandsrade/Eindhoven, NL) | IT services / MSP | ~101 | Digital provider — in scope |
| itility.nl | Itility (Eindhoven, NL) | IT services / cloud & data | ~201 | Digital provider — in scope |
| appsysictgroup.com | AppSys ICT Group (Houthalen/Peer, BE + Eindhoven, NL) | IT services / MSP | ~70 | Digital provider — in scope |
| axi.be | AXI Group (BE/NL) | IT & telecom services | ~300 | Digital provider — in scope |
| bauwens-logistics.be | Bauwens Logistics (BE/NL) | Logistics / transport | ~200 | Transport — in scope |
| dilissen-logistics.com | Dilissen Logistics (Pelt, BE) | Logistics / transport | ~140 | Transport — in scope |
| dobbetransport.nl | Dobbe Transport (Roelofarendsveen, NL) | Logistics / transport | ~200 | Transport — in scope |
| dlg-logistics.com | DLG Daily Logistics Group (Maasdijk, NL) | Logistics / conditioned transport | ~108 | Transport — in scope |
| avr.be | AVR (Roeselare, BE + Veendam, NL) | Manufacturing / agricultural machinery | ~120 | Manufacturing — supply chain |
| hvlmetaal.nl | HVL (machinebouw, NL) | Manufacturing / metaalbewerking | ~100 | Manufacturing — supply chain |
| it-total.se | IT-Total Sweden AB (Stockholm/Solna, SE) | IT services / MSP & cyber | ~107 | Digital provider — in scope |
| basalt.se | Basalt AB (Stockholm/Enköping, SE) | IT security services | ~108 | Digital provider — in scope |
| immeo.dk | immeo (København/Aalborg/Aarhus, DK) | IT consultancy | ~139 | Digital provider — in scope |
| kollab.dk | KOLLAB (Kolding + 8 DK offices, DK) | IT services | ~118 | Digital provider — in scope |
| besttransport.se | Best Transport Group (Stockholm, SE) | Logistics / courier & distribution | ~115 | Transport — in scope |
| ogs.se | ÖGS Örebro Göteborg Samverkan (Örebro, SE) | Logistics / transport | ~130 | Transport — in scope |
| thurah.dk | Thurah Transport A/S (Ishøj, DK) | Logistics / transport | ~90 | Transport — in scope |
| daniaconnect.dk | Dania Connect / Dania Group (DK + Helsingborg/Katrineholm, SE) | Logistics / trucking | ~179 | Transport — in scope |
| willo.se | Willo (Växjö, SE) | Manufacturing / precision parts | ~140 | Manufacturing — supply chain |
| sterke.dk | Sterke A/S (Aalborg, DK) | Manufacturing / steel structures | ~150 | Manufacturing — supply chain |

---

## Notes

- **Boundary cases:** `swu.de` (~600) and `suedvers.de` (~635) sit above the 500-employee ICP cap; keep as watch items, do not prioritise.
- **Reconciled 2026-08-10:** added the 20 DE domains already collected in `leads/leads.csv` (IT-HAUS, ORBIT, NetPlans, Nösse, comito, SÜDVERS, RVM, RCU, Volk, ASSON, Saegeling, MTR, Jüttner, MEDITECH, medika, Teubert, WEKAL, Claaßen, MEZ, Ebel) so `discovery.py` crawls them alongside the hosting/telecom set. **92 domains total** (32 DE + 20 AT/CH + 10 logistics + 10 legal + 10 NL/BE + 10 Nordics).
- **Competitor exclusion check:** none of the above operate a commercial phishing-simulation/security-awareness platform (compare `leads/contacts-v1.md` — SoSafe, G DATA, KnowBe4, Proofpoint, Hoxhunt, Sophos, msecure, synaforce, IT-Seal are **excluded**).
- **German Impressum rule (TMG §5 / DDG §5):** every German domain above is legally required to publish contact data on an Impressum page — this is the compliance-safe public source class for collection (`leads/tool-stack.md` §3).
- **Anti-scraping caveat:** several hosters/telecoms obfuscate emails (`info [at] domain.de`) or use contact forms; regex extraction handles both plain and `[at]`/`(at)` forms.
- **UWG note:** publishing an email in an Impressum is *not* consent to advertising (`leads/compliance.md`); collected rows are for qualified-outreach targeting, not mailing lists.

---

## Verified contact pages — Austria & Switzerland (added 2026-08-10)

Contact-page URLs live-verified HTTP 200 on 2026-08-10 (curl, follow-redirects). Same sourcing rule as the DE list: contact info only from the company's own site. Feeds `leads/discovery.py` (domains above) and human/AI enrichment.

### IT Services / System Houses (5)
| Company | Website | Contact page (verified) |
|---|---|---|
| base-it GmbH (Ansfelden, AT) | https://baseit.at/ | https://baseit.at/kontakt/ |
| techbold GmbH (Wien, AT) | https://www.techbold.at/ | https://www.techbold.at/kontakt |
| SYSco EDV GmbH (OÖ, AT) | https://www.sysco.at/ | https://www.sysco.at/kontakt/ |
| Intecso AG (Glattbrugg, CH) | https://www.intecso.ch/ | https://www.intecso.ch/kontakt/ |
| SEP IT AG (St. Gallen/Winterthur, CH) | https://www.sep.ch/ | https://www.sep.ch/kontakt |

### Finance / Insurance Brokers (5)
| Company | Website | Contact page (verified) |
|---|---|---|
| RVM Versicherungsmakler GmbH (Linz, AT) | https://rvm.at/ | https://rvm.at/de/ueber-uns/kontakt.html |
| Leading Brokers United Austria (AT) | https://lbua.at/ | https://lbua.at/kontakt |
| Schinner Versicherungsmaklerkanzlei GmbH (Wien, AT) | https://schinner.at/ | https://schinner.at/kontakt/ |
| ASSEPRO (CH) | https://assepro.com/ | https://assepro.com/ueber-assepro/kontakt/ |
| ARTUS Unicon AG (Reinach, CH) | https://www.unicon.ch/ | https://www.unicon.ch/firmenportrait/kontakt |

### Healthcare / MedTech (5)
| Company | Website | Contact page (verified) |
|---|---|---|
| HABEL Medizintechnik (Wien, AT) | https://www.habel-medizintechnik.at/ | https://www.habel-medizintechnik.at/kontakt/ |
| ASKIN&CO (Wien, AT) | https://askin.co.at/ | https://askin.co.at/de_AT/kontakt/ |
| Kerkoc GmbH (Wien, AT) | https://kerkoc.com/ | https://kerkoc.com/kontakt/ |
| Biomed AG (Dübendorf, CH) | https://biomed.ch/ | https://biomed.ch/unternehmen/#kontakt |
| Anandic AG (Feuerthalen, CH) | https://www.anandic.com/ | https://www.anandic.com/kontakt/ |

### Manufacturing (5)
| Company | Website | Contact page (verified) |
|---|---|---|
| Hierzer GmbH (Wilhering, AT) | https://www.hierzer.at/ | https://www.hierzer.at/kontakt.html |
| Rottmund Maschinenbau (Wien, AT) | https://www.rottmund.at/ | https://www.rottmund.at/kontakt |
| Müller Martini Manufacturing (Hasle, CH) | https://mullermartini-manufacturing.ch/ | https://mullermartini-manufacturing.ch/kontakt |
| Robert Ott AG (CH) | https://robertottag.ch/ | https://robertottag.ch/kontakt/ |
| Sumec AG (Biberist, CH) | https://www.sumec.ch/ | https://sumec.ch/kontakt/ |

---

## Verified contact pages — Logistics (added 2026-08-10)

Contact-page URLs live-verified HTTP 200 on 2026-08-10 (curl, follow-redirects). Transport/logistics vertical (NIS2 scope: transport sector). 10 targets — 5 DE, 3 AT, 2 CH.

| Company | Website | Contact page (verified) |
|---|---|---|
| Gericke Spedition (Hohenstein-Ernstthal, DE, ~150 emp.) | https://www.gericke-spedition.de/ | https://www.gericke-spedition.de/kontakt.html |
| TTM GmbH (Mannheim/Leipzig, DE, ~160 emp.) | https://www.ttm.de/ | https://www.ttm.de/kontakt.aspx |
| Transport Betz Gruppe (Malsch/Baden, DE, ~99 emp.) | https://transport-betz.de/ | https://transport-betz.de/kontakt.html |
| Meidel-Gruppe (Markt Einersheim, DE, ~200 emp.) | https://www.meidel-gruppe.de/ | https://www.meidel-gruppe.de/kontakt/ |
| Eggers Spedition GmbH (Lebensmittel-Logistik, DE, ~150 emp.) | https://www.spedition-eggers.de/ | https://www.spedition-eggers.de/kontakt/ |
| Ritter Trans GmbH (Loipersdorf/Theresienfeld, AT, ~125 emp.) | https://www.ritter-trans.at/ | https://www.ritter-trans.at/kontakt |
| K-Logistics (AT, 100+ emp.) | https://www.k-logistics.at/ | https://www.k-logistics.at/kontakt/ |
| Saexinger Gefahrgutlogistik (Wien/Ennsdorf, AT) | https://www.saexinger.at/ | https://www.saexinger.at/kontakt |
| TISA Speditions AG (St. Margrethen, CH, ~100 emp.) | https://www.tisa.ch/ | https://www.tisa.ch/kontakt |
| Schneider Gruppe (Basel, CH) | https://schneider-transport.com/ | https://schneider-transport.com/kontakt/ |

---

## Verified contact pages — Legal (added 2026-08-10)

Contact-page URLs live-verified HTTP 200 on 2026-08-10 (curl, follow-redirects). Legal vertical (mid-size DACH law firms — M365 / client-data / NIS2-adjacent exposure). 10 targets — 4 DE, 3 AT, 3 CH.

| Company | Website | Contact page (verified) |
|---|---|---|
| Oppenländer Rechtsanwälte (Stuttgart, DE, ~90 lawyers) | https://www.oppenlaender.de/ | https://oppenlaender.de/kontakt/ |
| SZA Schilling Zutt & Anschütz (Mannheim, DE, ~60 lawyers) | https://www.sza.de/ | https://www.sza.de/de/anfahrt-kontakt |
| ARQIS Rechtsanwälte (Düsseldorf/München/Tokio, DE, ~80 lawyers) | https://arqis.com/ | https://arqis.com/impressum |
| CBH Rechtsanwälte (Köln, DE, ~100 lawyers) | https://www.cbh.de/ | https://www.cbh.de/impressum |
| Pitkowitz & Partners (Wien, AT, ~30 lawyers) | https://www.pitkowitz.com/ | https://www.pitkowitz.com/kontakt/ |
| Metzler Rechtsanwälte (Linz, AT, ~25 lawyers) | https://metzler.law/ | https://metzler.law/kontakt/ |
| Binder Grösswang (Wien/Innsbruck, AT, ~125 lawyers) | https://www.bindergroesswang.at/ | https://www.bindergroesswang.at/impressum |
| Bratschi AG (7 Standorte, CH, ~120 lawyers) | https://www.bratschi.ch/ | https://www.bratschi.ch/kontakt |
| Wenger Plattner (Basel/Zürich/Bern, CH, ~100 staff) | https://wenger-plattner.ch/ | https://wenger-plattner.ch/de/kontakt/form/67900/ |
| Lenz Caemmerer (Basel/Karlsruhe, CH, ~45 lawyers) | https://www.lclaw.ch/ | https://www.lclaw.ch/kontakt/ |

> Note: ARQIS, CBH und Binder Grösswang veröffentlichen keine dedizierte /kontakt-Seite (404); die kontaktrechtlich maßgebliche Seite ist das (verifizierte) Impressum. `discovery.py` crawlt je Domain automatisch beide (`/kontakt` und `/impressum`).

---

## Verified contact pages — Netherlands & Belgium (added 2026-08-10)

Contact-page URLs live-verified HTTP 200 on 2026-08-10 (curl, follow-redirects). NIS2-EU-Region (Wbni NL / NIS2-Gesetz BE): transport, digital providers, manufacturing supply chain. 10 targets — 5 NL, 5 BE.

| Company | Website | Contact page (verified) |
|---|---|---|
| KEMBIT (Wijnandsrade/Eindhoven, NL, ~101 emp.) | https://kembit.nl/ | https://kembit.nl/contact/ |
| Itility (Eindhoven, NL, ~201 emp.) | https://itility.nl/ | https://itility.nl/#contact |
| AppSys ICT Group (Houthalen/Peer, BE + Eindhoven, NL, ~70 emp.) | https://www.appsysictgroup.com/ | https://www.appsysictgroup.com/en/contact |
| AXI Group (BE/NL, ~300 emp.) | https://www.axi.be/ | https://www.axi.be/nl/contacteer-ons |
| Bauwens Logistics (BE/NL, ~200 emp.) | https://bauwens-logistics.be/ | https://bauwens-logistics.be/contact/ |
| Dilissen Logistics (Pelt, BE, ~140 emp.) | https://www.dilissen-logistics.com/ | https://www.dilissen-logistics.com/contact/ |
| Dobbe Transport (Roelofarendsveen, NL, ~200 emp.) | https://www.dobbetransport.nl/ | https://www.dobbetransport.nl/contact/ |
| DLG Daily Logistics Group (Maasdijk, NL, ~108 emp.) | https://dlg-logistics.com/ | https://dlg-logistics.com/nl/contact |
| AVR (Roeselare, BE + Veendam, NL, ~120 emp.) | https://avr.be/ | https://avr.be/en/page/contact |
| HVL (machinebouw, NL, ~100 emp.) | https://www.hvlmetaal.nl/ | https://www.hvlmetaal.nl/contact/ |

> Note: Itility hat keine dedizierte Kontaktseite (404) — Kontakt über Homepage-Anker `#contact` + `mailto:contact@itility.nl`; Homepage ist HTTP 200.

---

## Verified contact pages — Nordics (Sweden & Denmark, added 2026-08-10)

Contact-page URLs live-verified HTTP 200 on 2026-08-10 (curl, follow-redirects). Nordic region — NIS2-EU (SE: NIS2-lagen, DK: lov om cybersikkerhed): IT/transport/manufacturing. 10 targets — 5 SE, 5 DK.

| Company | Website | Contact page (verified) |
|---|---|---|
| IT-Total Sweden AB (Stockholm/Solna, SE, ~107 emp.) | https://it-total.se/ | https://www.it-total.se/kontakt/ |
| Basalt AB (Stockholm/Enköping, SE, ~108 emp.) | https://basalt.se/ | https://basalt.se/kontakt/ |
| immeo (København/Aalborg/Aarhus, DK, ~139 emp.) | https://immeo.dk/ | https://immeo.dk/kontakt-os/ |
| KOLLAB (Kolding + 8 DK offices, DK, ~118 emp.) | https://kollab.dk/ | https://kollab.dk/kontakt/ |
| Best Transport Group (Stockholm, SE, ~115 emp.) | https://besttransport.se/ | https://besttransport.se/om-best/kontakta-best/ |
| ÖGS Örebro Göteborg Samverkan (Örebro, SE, ~130 emp.) | https://ogs.se/ | https://ogs.se/kontakt/ |
| Thurah Transport A/S (Ishøj, DK, ~90 emp.) | https://thurah.dk/ | https://thurah.dk/kontakt/ |
| Dania Connect / Dania Group (DK + Helsingborg/Katrineholm, SE, ~179 emp.) | https://www.daniaconnect.dk/ | https://www.daniaconnect.dk/kontakt/ |
| Willo (Växjö, SE, ~140 emp.) | https://www.willo.se/ | https://www.willo.se/kontakt/kontakta-oss/ |
| Sterke A/S (Aalborg, DK, ~150 emp.) | https://sterke.dk/ | https://sterke.dk/kontakt/ |
