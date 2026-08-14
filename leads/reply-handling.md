# Reply-Handling Spec — Blocker B9

Defines inbound-reply handling for `send-batch-1.csv` (123 touches, 41 leads). Clears blocker **B9** in `leads/launch-readiness.md`. Grounded in `leads/pipeline.md` §Stage 4 (reply routing) and `leads/outreach-plan.md` §2–§3 (cadence, windows, parking).

---

## 1. Inbound reply tracking

- **Monitor mailbox:** a dedicated reply inbox (or the ESP's thread/`Reply-To` inbox) that receives replies to all batch-1 touches. The `From`/`Reply-To` identity of every touch must point at this inbox.
- **Thread matching:** link each inbound reply to its touch via `In-Reply-To`/`References`/`Message-ID` → resolve to `send_at` and touch `id` in `send-attribution.csv` (email + Day 0/3/7). Unresolvable replies match by sender email.
- **Dedupe:** one reply per lead per thread = one tracking event; subsequent replies in the same thread update the record, they don't create new leads.
- **Capture:** sender email, touch id, timestamp, subject, classification, full body (retained for consent/audit per GDPR).

## 2. Classification & per-persona outcome routing

Classify the reply, then route by persona (SMB Owner / IT Manager / HR Lead template used for that touch).

| Classification | Detection (subject/body keywords, DE+EN) | SMB Owner (Template 1) | IT Manager (Template 2) | HR Lead (Template 3) |
|---|---|---|---|---|
| **Demo request** | `demo`, `termin`, `walkthrough`, `kennenlernen`, `call`, `anrufen`, `yes`, `ja` | Free sample campaign → schedule; if qualified → trial client | Live demo vs own test group → schedule 30-min | 15-min walkthrough w/ HR head → schedule |
| **Pricing question** | `preis`, `kosten`, `price`, `cost`, `paket`, `plan`, `offer` | Qualify (size, NIS2) → pricing sheet → nurture or handoff | Qualify (users, infra) → pricing + demo offer | Pricing + compliance-evidence angle → nurture |
| **Unsubscribe** | `unsubscribe`, `abmelden`, `keine werbung`, `entfernen`, `stop` | → `opted_out`, permanent suppression, never contact again | same | same |
| **Spam complaint** | `spam`, `missbrauch`, `abuse`, `beschwerde`, `ungesetzlich`, feedback-loop header | Immediate suppression + escalation + content review | same | same |
| **Negative but qualified** | `not interested`, `kein bedarf`, `später`, `budget` | Nurture → re-sequence in **90 days** | same | same |
| **Out of scope / wrong person** | `wrong person`, `falsche person`, `kollege`, `zuständig` | Re-map to correct persona/contact or park | same | same |

**Common flow:** classify → route → log outcome (`tracking.py`) → if positive, create trial client (`PhishGuard client add`, `pipeline.md` §Stage 4) and hand to onboarding.

## 3. Logging — `leads/tracking.py` (new module) / tracking store

Create `leads/tracking.py` (Python) exposing:

```python
record_reply(email, touch_id, classification, outcome, reply_id)   # upsert per lead
update_outcome(email, outcome)                                     # qualified/nurture/opted_out/spam
set_suppression(email, source="reply_unsubscribe")                 # permanent, consent-log REVOCATION
append_send_log(email, touch, send_at, status)                     # per-touch send status
mark_parked(email, date)                                           # D+14 nurture park
```

Store: `leads/tracking.csv` (append-only) + `leads/progress.md` funnel counts (Outreach/Replies/Qualified/Opted out/Nurture — `progress.md` schema). Columns for `tracking.csv`:

`email, touch_id, send_at, reply_at, classification, outcome, reply_summary, action_taken, owner, notes`

- Every touch is appended at send time; every reply updates the row via `update_outcome`.
- `opted_out` / `spam` writes are mirrored to the suppression store (`unsubscribe-spec.md` §3) and `consent-log.md` REVOCATION block.
- GDPR: store reply text with the lead record; retention per `consent-log.md` (§3.10, ≥ 3 years); no reply text shipped to third parties.

## 4. Reply SLA

- **No numeric reply SLA is stated in `outreach-plan.md`**; this spec adopts its window conventions (§3): reply **within 1 business day** of the inbound, sent inside **Tue–Thu 09:30–16:00 CEST** windows.
- Same-day replies received in-window get a same-day response; out-of-window replies (Fri–Mon, after 16:00) are answered on the next allowed send day.
- **Strict-zero cases (no SLA, immediate action):** unsubscribe and spam complaints — suppress instantly, no waiting for a send window.
- **No-reply handling:** no reply after Day-7 FU2 → **park at D+14** to nurture (quarterly newsletter) or disqualify per `outreach-plan.md` §2; never add a 4th touch.

## 5. Escalation & audit

| Trigger | Escalation |
|---|---|
| Spam complaint | Immediate suppression; pause remaining touches from the same sender IP/domain if complaints ≥ 0.3% (`sender-infra-check.md` §7); content + consent review; record in feedback loop |
| Legal threat / Abmahnung | Stop all sends, freeze batch, route to legal counsel (DE UWG / AT TKG exposure) |
| Reply mentions consent complaint | Verify the lead's `consent-log.md` record; if missing, treat as violation → stop that lead + review capture process |
| Demo/pricing request unanswered > 1 business day | Escalate to outreach lead (missed-SLA log) |

**B9 sign-off:** monitor mailbox live → thread matching to `send-attribution.csv` → classification per §2 → `tracking.py`/`tracking.csv` logging → outcomes routed (trial / nurture / opted_out / park) → SLA met per §4.
