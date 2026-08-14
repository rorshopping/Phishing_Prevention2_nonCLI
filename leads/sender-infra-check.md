# Sender Infrastructure Check — Blocker B6

Pre-launch checklist for the sending identity behind `send-batch-1.csv` / `send-config-final.csv` (123 touches, 41 leads). Covers **SPF / DKIM / DMARC** configuration and the **volume guardrails** from `leads/outreach-plan.md` §3 and `leads/tool-stack.md` §4. Clears blocker **B6** in `leads/launch-readiness.md`.

> ⚠️ **Sending domain:** the batch's `From` must use a domain you own and control DNS for. `phishdefend-ai.vercel.app` is a Vercel subdomain — you cannot publish SPF/DKIM/DMARC there. Register/use a real apex (e.g. `phishdefend.ai`) and configure it before any send.

---

## 1. DNS records to publish (per sending domain)

| Record | Type | Example value | Purpose |
|---|---|---|---|
| SPF | TXT `@` | `v=spf1 include:<esp_spf_include> -all` | Which hosts may send for the domain |
| DKIM | TXT `<selector>._domainkey` | `v=DKIM1; k=rsa; p=<public-key>` | Signs each message; verifies domain+selector |
| DMARC | TXT `_dmarc` | `v=DMARC1; p=none; rua=mailto:dmarc@<domain>; fo=1` | Policy + alignment + forensic reports |
| MX | MX `@` | existing MX (deliverability) | Not strictly a sender record; verify present |

## 2. SPF checklist

- [ ] SPF published on the apex (`@`), single record, ≤ 10 lookup limit (keep `include:` chains shallow).
- [ ] Covers **only** the ESP's sending infrastructure (`include:<esp>`), no stray third-party includes.
- [ ] Hard-fail `-all` once stable; `~all` acceptable during ramp.
- [ ] From-domain matches the envelope domain used by the ESP (SPF alignment for DMARC).
- [ ] Verified: `Resolve-DnsName -Type TXT <domain>` shows exactly one `v=spf1` record; `nslookup -type=txt` too.

## 3. DKIM checklist

- [ ] Keypair generated in the ESP; **public** key published as `<selector>._domainkey.<sending-domain>` TXT.
- [ ] Private key never leaves the ESP; selector name stable (don't rotate mid-campaign without re-signing).
- [ ] DKIM signing **enabled for the sending identity** used in the batch.
- [ ] `From:` domain = DKIM domain (aligns for DMARC).
- [ ] Verified: send a test email → header shows `dkim=pass` (e.g. `mail-tester.com` score ≥ 9/10; `MXToolbox`/`GoogleAdminToolbox` checkers).

## 4. DMARC checklist

- [ ] Published: `v=DMARC1; p=none; rua=mailto:dmarc@<domain>; pct=100`.
- [ ] **Ramp policy only after proof:** `p=none` (collect) → `p=quarantine` → `p=reject`; wait ≥ 2–4 weeks at each step on 100% reporting.
- [ ] `adkim`/`aspf` relaxed (`r`) initially, tighten to strict (`s`) only when both pass consistently.
- [ ] `rua` mailbox monitored; review reports weekly during the campaign window.
- [ ] All three alignment checks green for a test send: SPF pass + DKIM pass + DMARC `align` (verify via a DMARC report or checker).

## 5. Sending-volume guardrails (from `leads/outreach-plan.md` §3, `leads/tool-stack.md` §4)

| Guardrail | Value | Source | Batch-1 actual |
|---|---|---|---|
| Daily cap per inbox | **≤ 20–30 sends/inbox/day** | outreach-plan §3; tool-stack §4 | Max day = **27** ✅ (2026-08-18) |
| Monthly cap per inbox | **≤ ~1,000 sends/inbox/month** | tool-stack §4 | Total = **123** ✅ |
| Bounce rate | **< 2%** | tool-stack §4 (Gmail/Yahoo 2024 sender rules); outreach-plan KPI | 0 (none sent) |
| Hard-bounce handling | Remove/block address within **24 h**; no re-send | tool-stack §4 + outreach-plan gate | — |
| Spam-complaint rate | **≤ 0.3%** (Gmail/Yahoo 2024 bulk-sender guidance); target < 0.1% | *not specified in repo docs — industry standard adopted* | — |
| Warm-up | Ramp into the 30/day cap, not straight to it | tool-stack §4 ("warmed inbox") | ramp plan below |

### Warm-up ramp (suggested, per inbox)

| Week | Sends/day (max) | Cumulative ~/week | Notes |
|---|---|---|---|
| 1 | 5–10 | ~50 | small, high-quality sends; monitor opens/complaints |
| 2 | 15 | ~105 | add the Day-0 cohort volume (7–13/day in batch-1 fits) |
| 3 | 20–25 | ~155 | — |
| 4 | **30** | ~210 | full cap; campaign max day 27 fits |

Rules: no warm-up to a cold address; only reach the 30 cap after 3+ weeks of clean metrics; if bounce ≥ 2% or complaints ≥ 0.3% at any step, **hold volume, fix root cause, resume lower**.

## 6. Pre-launch verification sequence

1. DNS records published and propagated (48 h for full propagation; verify TTL/`Resolve-DnsName`).
2. `mail-tester.com` score ≥ 9/10 from each inbox identity.
3. SPF/DKIM/DMARC checkers all green for the exact `From` identity used in the batch.
4. Send 2–3 sandbox test emails (dry-run `send-config-final.csv` Step 4) → `dkim=pass`, `spf=pass`, DMARC aligned, landing in inbox (not spam).
5. Confirm the calendar's per-day totals (max 27) fit the per-inbox cap — if more inboxes are added, re-balance so **each** inbox stays ≤ 30/day.
6. If any inbox is used for follow-ups on the same day as Day-0 sends from another, sum per-inbox — never exceed 30/inbox/day regardless of batch.

## 7. Thresholds & actions during the campaign

| Metric | Threshold | Action |
|---|---|---|
| Bounce rate | ≥ 2% | Pause; verify addresses (pass-2, B7); block hard bounces ≤ 24 h |
| Spam complaints | ≥ 0.3% | Pause; review content/consent; fix then resume lower volume |
| Deliverability (opens/sent) | < 85% (KPI, outreach-plan) | Diagnose SPF/DKIM/DMARC + content; hold remaining touches |
| DMARC failures | > 5% of sent | Tighten config before continuing |

**B6 sign-off:** publish DNS → verify SPF/DKIM/DMARC → run warm-up ramp → pass mail-tester ≥ 9 → confirm max-day 27 ≤ 30/inbox cap → monitor bounce < 2% / complaints < 0.3% throughout. Only then proceed to `dry-run-batch1.md` Step 3–5 and, after B1/B2/B3/B5, to load.
