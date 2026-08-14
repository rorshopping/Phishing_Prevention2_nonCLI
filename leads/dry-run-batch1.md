# Dry-Run Procedure — send-config-final.csv (123 rows)

Validates the sending tool end-to-end in **dry-run mode (zero emails sent)** before the consent gate clears (B2) and before the footer merge (B5). The dry run proves the file loads, parses, flags unresolved placeholders, and renders a correct delivery preview — so launch isn't blocked on tooling once consent exists.

**Input:** `leads/send-config-final.csv` (123 rows / 41 leads × 3 touches) · **Reference checks:** `leads/send-config-audit.md` (C1–C6) · **Tool:** the ESP configured per `leads/tool-stack.md` §4 (B6).

---

## 1. Preconditions

- [ ] `send-config-final.csv` present with **123 rows**, 12 expected columns, UTF-8 (BOM allowed).
- [ ] Sending tool installed, configured with sender identity + SPF/DKIM/DMARC, **dry-run/preview mode enabled**.
- [ ] A sandbox/test inbox is available for delivery previews (previews go here, not to real recipients).
- [ ] No real sends are scheduled — the dry run must leave the outbox and SMTP queue empty.

## 2. Steps

### Step 1 — Static parse validation (local, no tool)

```python
import csv, re
with open('leads/send-config-final.csv', encoding='utf-8-sig') as f:
    rows = list(csv.DictReader(f))
EXPECTED = {'id','company','lead_name','email','touch','send_at','template',
            'subject','body','country','werbung_prefix_required','rules_flag'}
assert len(rows) == 123, len(rows)
assert set(rows[0]) == EXPECTED
assert len(set(r['email'] for r in rows)) == 41
assert all(r['id'] and r['email'] and r['send_at'] and r['subject'] and r['body'] for r in rows)
print('PASS: 123 rows parse, columns complete, 41 unique leads')
```

**Expected:** `PASS`. **Fail →** fix the file (regenerate from `send-batch-1.csv` + `country-rules.csv`), do not load.

### Step 2 — Placeholder scan (expected FLAGS, not errors, pre-merge)

```python
ph = {}
for r in rows:
    for m in re.findall(r'\{\{[A-Za-z]+\}\}', r['body']):
        ph[m] = ph.get(m, 0) + 1
print('placeholder fields:', len(ph), ph)
```

**Expected (current state, B5 pending):** **13 placeholder fields** present in every body — they must be **flagged by the dry run** (audit C6 🔴), confirming the tool surfaces unresolved placeholders instead of silently sending garbage. **Expected after footer merge:** 0 (dry run then reports clean).

### Step 3 — Load into tool (dry-run mode)

1. Import `send-config-final.csv` via the tool's CSV importer (or API batch endpoint) with `dry_run=true`.
2. Confirm the tool accepts `send_at` ISO-8601 (`+02:00`) and maps columns to recipient / subject / body / schedule.
3. Confirm the schedule respects `send_at`; no touch is pulled forward or re-timestamped.

**Expected:** import succeeds; 123 scheduled slots shown as **drafts/queued**, none sent.

### Step 4 — Delivery preview (per lead, 41 × 3)

- [ ] Render Day-0/FU1/FU2 for all 41 leads; subject + body render without template syntax leaking.
- [ ] AT leads (`markus.schrott@tisa.at`, `p.wurm@sysco.at`): subject starts `[Werbung] `.
- [ ] `{{UnsubscribeURL}}` and `{{ConsentSource}}` visibly unresolved (flagged) until B5.
- [ ] Compliance Footer block visible in each preview with Impressum placeholders flagged.
- [ ] Delivery preview (spam score, preheader, link check) produced per message — no exceptions.
- [ ] Send address is a sandbox inbox, not the real recipient.

### Step 5 — Prove nothing was sent

- [ ] Tool outbox / sent folder: **empty**.
- [ ] SMTP/API send log: **zero** send events (dry-run flag honored).
- [ ] No bounce/feedback loop activity for the test inbox.

## 3. Pass / fail criteria

| Check | Criterion | Current expected |
|---|---|---|
| Parse (Step 1) | 123 rows, 41 unique leads, columns complete | ✅ PASS |
| Placeholder flagging (Step 2) | Tool flags unresolved `{{...}}` | ✅ FLAGGED (13 fields × 123 bodies) |
| Import + schedule (Step 3) | 123 drafts, none sent | ✅ PASS (drafts only) |
| Preview (Step 4) | Subjects/bodies render; `[Werbung]` correct; footer visible | ✅ PASS (with expected flags) |
| No sends (Step 5) | outbox/SMTP empty | ✅ PASS |

**Overall dry run: PASS** once 1, 3, 4, 5 are green and Step 2 flags exactly the 13 expected placeholder fields. The dry run is **not** a consent substitute — it validates tooling only.

## 4. Failure handling

- **Parse/import error** → fix CSV encoding/columns; never auto-fix inside the tool.
- **Placeholders NOT flagged** → the tool is unsafe to use after merge too — block, investigate tool config, or switch tool.
- **Any send executed during dry run** → stop immediately, quarantine, review tool's dry-run flag, escalate (a sent email without consent is a UWG/TKG violation).
- **Preview shows `[Werbung]` missing or wrong country flags** → regenerate `send-config-final.csv` (country/rules join), re-run audit C3/C4.

## 5. Sign-off

- [ ] Dry run executed against `send-config-final.csv` (123 rows), Steps 1–5 documented.
- [ ] Output (import log + 123 previews) archived for the launch record.
- [ ] Tool dry-run validated → launch remains gated **only** on consent (B2/B4) + footer merge (B5) + endpoint (B3), per `launch-readiness.md`.
