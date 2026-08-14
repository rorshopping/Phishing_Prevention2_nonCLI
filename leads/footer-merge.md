# Footer Merge Procedure — `send-footer-values.csv` → `send-batch-1.csv`

Procedure for inlining the Compliance Footer values into all **117 bodies** of `leads/send-batch-1.csv` (and the derived `leads/send-config-final.csv`) once the org entity is filled. Unblocks `leads/launch-readiness.md` **B5** and turns the audit check **C6** (`leads/send-config-audit.md`) green.

---

## 1. Preconditions (gate — do not start unless all pass)

| # | Gate | Where | Fails → |
|---|---|---|---|
| G1 | All 8 legal-entity fields filled (LegalEntityName, StreetAddress, PostalCode, City, RegisterCourt, RegisterNo, VATId, ManagingDirector) | `leads/send-footer-values.csv` | Abort — complete `leads/org-entity-form.md` first |
| G2 | Country / ImpressumURL / PrivacyURL present (already prefilled) | `leads/send-footer-values.csv` | Abort |
| G3 | A consent-log record exists for **every DE/AT lead** (C5), incl. exact consent source string | `leads/consent-log.md` | Abort for those leads; do not inject a fake source |
| G4 | `/unsubscribe` endpoint live + one token per lead generated (`leads/unsubscribe-spec.md` §1, §3) | suppression store | Abort — B3 must be done first |
| G5 | Send-batch-1.csv untouched by other processes (117 rows) | `leads/send-batch-1.csv` | Regenerate first |

---

## 2. Merge steps

### Step A — Org-level placeholder replacement (11 values × 117 bodies)

Source row: the single record in `leads/send-footer-values.csv`.

Replace in **every body** (`body` column, all 117 rows):

| Placeholder | Source column |
|---|---|
| `{{LegalEntityName}}` | `LegalEntityName` |
| `{{StreetAddress}}` | `StreetAddress` |
| `{{PostalCode}}` | `PostalCode` |
| `{{City}}` | `City` |
| `{{Country}}` | `Country` |
| `{{RegisterCourt}}` | `RegisterCourt` |
| `{{RegisterNo}}` | `RegisterNo` |
| `{{VATId}}` | `VATId` |
| `{{ManagingDirector}}` | `ManagingDirector` |
| `{{ImpressumURL}}` | `ImpressumURL` |
| `{{PrivacyURL}}` | `PrivacyURL` |

Rule: replace only if the source value is non-empty; if any of the 11 is empty → **abort with G1/G2 error** (never emit a half-filled footer).

### Step B — Per-lead `{{UnsubscribeURL}}` (token per lead)

Do **not** use one org-wide URL. Generate one tokenized URL per unique lead email (from the suppression store, `leads/unsubscribe-spec.md` §1):

```
https://phishdefend-ai.vercel.app/unsubscribe?token=<uuid4>
```

Replace `{{UnsubscribeURL}}` in that lead's 3 rows (Day 0 / Day 3 / Day 7 share the token). Also replace it in the **reply-line fallback** occurrences (195 → 117 after merge; each body has 2 footer references + 1 inline opt-out link).

### Step C — Per-lead `{{ConsentSource}}` (from consent log)

| Recipient country | ConsentSource value |
|---|---|
| DE / AT | The logged consent source from the lead's `consent-log.md` record, e.g. `phone consent, 2026-08-04, S. Weber` or `double opt-in, 2026-08-04` |
| CH | `targeted outreach relevant to your role at <Company>` (role-relevance note, outreach-plan §4 #10) |
| US | (none in this batch) — omit/adjective-free |

- Look up per lead email → consent record (G3). Missing record for a DE/AT lead → **abort for that lead** (do not merge, do not send).
- Replace `{{ConsentSource}}` (117 occurrences) with the per-lead string.

### Step D — Write outputs

Regenerate both files with the merged bodies:
- `leads/send-batch-1.csv` (same 12 columns)
- `leads/send-config-final.csv` (same 14 columns incl. `country`, `werbung_prefix_required`, `rules_flag`)

---

## 3. Post-merge validation (must pass before loading)

```python
import csv, re

def load(p):
    with open(p, encoding='utf-8-sig') as f:
        return list(csv.DictReader(f))

rows = load('leads/send-config-final.csv')

# 1) zero placeholders anywhere in body/subject
hits = [(r['id'], m) for r in rows for m in re.findall(r'\{\{[A-Za-z]+\}\}', r['body'])]
assert not hits, f'{len(hits)} placeholders remain: {hits[:5]}'

# 2) counts intact
assert len(rows) == 117
assert all(r['email'] for r in rows)

# 3) AT leads keep [Werbung]; no spurious prefix elsewhere
for r in rows:
    if r['country'] == 'Austria':
        assert r['subject'].startswith('[Werbung] '), r['id']
    else:
        assert not r['subject'].startswith('[Werbung] '), r['id']

# 4) UnsubscribeURL unique per lead, points at /unsubscribe, token non-empty
urls = {r['email']: r['body'].split('?token=')[1][:36] for r in rows}
assert all(u.startswith('https://phishdefend-ai.vercel.app/unsubscribe?token=') for u in urls.values())

print('PASS: 117 rows, 0 placeholders, counts & prefixes intact')
```

Manual spot-checks: render one DE, one AT, one CH body; confirm footer shows full legal entity + working unsubscribe link + per-lead consent source; re-run `leads/send-config-audit.md` — **C6 must be green** (C5 still depends on the consent gate being fully logged).

---

## 4. Idempotency & rollback

- **Idempotent:** re-running on an already-merged file finds no `{{...}}` and is a no-op (validation #1 protects).
- **Rollback:** keep a pre-merge copy of `send-batch-1.csv` (e.g. `send-batch-1.premerge.csv`) until the first Day-0 send; `git` history is the fallback.
- **Drift guard:** if any concurrent agent regenerates `send-batch-1.csv` from templates (it carries unresolved placeholders by design), re-run this merge after that regeneration — never merge onto a stale copy.

## 5. Done criteria

- [ ] G1–G5 passed; merge executed (Step A–D)
- [ ] Validation script prints `PASS`; 0 placeholders across 117 bodies
- [ ] Audit C6 green; C5 green only when consent records exist for all 39 leads
- [ ] Batch loaded into the sending tool per `leads/send-calendar.csv` windows
