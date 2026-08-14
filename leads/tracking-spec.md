# tracking.py — Implementation Spec

Implementation spec for the `leads/tracking.py` module referenced by `leads/reply-handling.md` (§3). It records send events, inbound replies, outcomes, suppression, and parking for **batch 1** (41 leads / 123 touches) and feeds the funnel mirror in `leads/progress.md`.

**Inputs:** `leads/send-attribution.csv` (authoritative touch registry, 123 rows) · **Store:** `leads/tracking.csv` (append-only) · **Funnel:** `leads/progress.md`.

---

## 1. Data contract — join key with `send-attribution.csv`

| tracking.py concept | Source of truth |
|---|---|
| `touch_id` (int 1..123) | `send-attribution.csv` → column `id` (unique, 1..123, verified) |
| `email` | `send-attribution.csv` → `email` (one per touch, normalized lowercase) |
| `send_at` | `send-attribution.csv` → `send_at` (ISO-8601 `+02:00`) |
| consent linkage | `send-attribution.csv` → `consent_lead_key` (== email) |
| opt-out URL | `send-attribution.csv` → `unsubscribe_url` (per-lead token) |

Invariants enforced by `tracking.py`:
- Every `touch_id` passed to a tracking function must exist in `send-attribution.csv` and the `email` must match the attribution row for that `id` — otherwise **raise** (no silent writes).
- One tracking row **per touch_id per send attempt** (append); replies upsert per lead+thread (see §3).

## 2. Module API

```python
# leads/tracking.py
def append_send_log(email: str, touch_id: int, status: str, send_at: str) -> dict
def record_reply(email: str, touch_id: int, classification: str, reply_id: str = "") -> dict
def update_outcome(email: str, outcome: str, action_taken: str = "", owner: str = "") -> dict
def set_suppression(email: str, source: str = "reply_unsubscribe") -> dict
def mark_parked(email: str, date: str) -> dict
def funnel_counts() -> dict  # aggregates for progress.md mirror
```

| Function | Behavior | Side effects |
|---|---|---|
| `append_send_log` | Writes a `send` row (`status`: `sent`/`blocked`/`skipped_suppressed`/`dry_run`). Idempotent per (email, touch_id). | tracking.csv |
| `record_reply` | Upserts the lead's reply record (`classification` from §4 of `reply-handling.md`; `reply_id` = inbound Message-ID for dedupe). | tracking.csv |
| `update_outcome` | Sets terminal/state outcome: `qualified`, `nurture`, `opted_out`, `spam_complaint`, `unresponsive`, `re_mapped`, `parked`. | tracking.csv; mirrors to `progress.md` counters |
| `set_suppression` | Writes suppression event; mirrors to the suppression store (`unsubscribe-spec.md` §3) and `consent-log.md` REVOCATION block. | tracking.csv + suppression store + consent-log |
| `mark_parked` | Records the D+14 park date; moves lead to `nurture` if no other outcome. | tracking.csv + progress.md |
| `funnel_counts` | Aggregates `Outreach (sent)`, `Replies`, `Qualified`, `Nurture`, `Opted out`, `Unresponsive` for `progress.md`. | read-only |

## 3. `tracking.csv` schema

```csv
email,touch_id,send_at,event_type,reply_at,classification,outcome,reply_summary,action_taken,owner,notes
```

| Column | Type | Values / notes |
|---|---|---|
| `email` | str | lowercase, must match attribution |
| `touch_id` | int | 1..123, must exist in attribution |
| `send_at` | str | ISO-8601 `+02:00` from attribution |
| `event_type` | str | `send` · `reply` · `outcome` · `suppression` · `park` |
| `reply_at` | datetime | inbound reply timestamp (empty for send events) |
| `classification` | str | from `reply-handling.md` §2: `demo_request` · `pricing` · `unsubscribe` · `spam_complaint` · `negative_qualified` · `out_of_scope` |
| `outcome` | str | `qualified` · `nurture` · `opted_out` · `spam_complaint` · `unresponsive` · `re_mapped` · `parked` |
| `reply_summary` | str | short body excerpt (GDPR-retained with lead record) |
| `action_taken` | str | e.g. `trial_created`, `demo_scheduled`, `suppressed`, `pricing_sent` |
| `owner` | str | outreach lead / rep handling the thread |
| `notes` | str | free text |

Send event example: `n.siebertz@cbh.de,119,2026-08-25T09:30:00+02:00,send,,,sent,,,,`
Reply event example: `n.siebertz@cbh.de,119,2026-08-25T09:30:00+02:00,reply,2026-08-26T10:05:00+02:00,demo_request,,,trial_created,Outreach lead,`

## 4. `progress.md` funnel mirror

`funnel_counts()` updates the `## Funnel counts` table (keys from `leads/progress.md`):

| progress.md field | derived from tracking.csv |
|---|---|
| `Outreach (sent)` | count of `event_type=send` with status `sent` (unique touch_id) |
| `Replies` | count of unique leads with `event_type=reply` |
| `Qualified` | count of unique leads with `outcome=qualified` |
| `Nurture` | count of unique leads with `outcome in {nurture, parked, negative_qualified}` |
| `Opted out` | count of unique leads with `outcome in {opted_out, spam_complaint}` |
| `Unresponsive` | count of unique leads with `outcome=unresponsive` (after D+14 park) |

Update rule: after every `record_reply` / `update_outcome` / `mark_parked`, recompute and write the six counters. Never hand-edit the counters separately (single source = `tracking.csv`).

## 5. Verification vs `send-attribution.csv`

Run after building the spec / before first use:

```python
import csv
attr = {r['id']: r for r in csv.DictReader(open('leads/send-attribution.csv', encoding='utf-8-sig'))}
assert sorted(int(k) for k in attr) == list(range(1, 124))       # touch ids 1..123 complete
assert len({r['email'] for r in attr.values()}) == 41             # 41 unique leads
assert all(r['unsubscribe_url'].startswith('https://phishdefend-ai.vercel.app/unsubscribe?token=') for r in attr.values())
print('PASS: attribution schema matches tracking contract (touch_id 1..123, 41 leads, tokenized URLs)')
```

Status: **verified 2026-08-10** — `send-attribution.csv` contains ids 1..123 (complete), 41 unique `email` values, per-lead `unsubscribe_url` tokens, `send_at` ISO-8601 with `+02:00`, and `consent_lead_key == email`. No schema changes needed to implement this spec.

## 6. Guardrails

- **No fabricated rows:** every `email`/`touch_id` pair must trace to `send-attribution.csv`; unknown `touch_id` → raise.
- **Append-only:** `tracking.csv` rows are never edited in place; corrections are new rows with `notes=correction:<id>`.
- **Suppression is absolute:** `set_suppression` removes the lead from all future sends (checks at load time; `dry-run-batch1.md` Step 3 re-confirms no suppressed lead is queued).
- **Consent mirror:** every `opted_out`/`spam_complaint` also writes the `consent-log.md` REVOCATION block (`consent-log.md` §2) — tracking.py never silences without it.
