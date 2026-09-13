# Operator Guide — PhishDefend AI

How to run the platform day to day: start it, onboard customers, launch
simulations, read results, and deploy the public site. Written for the
person operating the product, not for developers. Everything here reflects
the code as of 2026-09; where behavior depends on configuration, it says so.

---

## 1. What the product does

PhishDefend AI runs **phishing simulations against a customer's employees**
and turns the results into risk scores, reports, and training assignments.
An AI pipeline plans scenarios per employee group, generates personalized
emails, sends them through an embedded **Gophish** server, and monitors
who opened/clicked/submitted credentials. A web console (`/console`) and a
CLI (`phishguard`, from `src/cli/main.py`) drive everything.

```
Orchestrator (scheduler or manual trigger)
  → Planner → Email Builder (LLM, template fallback)
  → Execution Agent → Gophish (SMTP + landing pages)
  → Monitoring Agent → Risk Engine → Reports / Training
```

## 2. Prerequisites & configuration

All configuration lives in `.env` (loaded via `src/config.py`). Key groups:

| Group | Variables | Needed for |
|---|---|---|
| Database | `DATABASE_URL` (default SQLite) | everything |
| Gophish | `GOPHISH_API_URL`, `GOPHISH_API_KEY`, `GOPHISH_PHISHING_SERVER_URL` | sending simulations; **the scheduler only starts if `GOPHISH_API_KEY` is set** |
| LLM | `LLM_API_KEY`, `LLM_MODEL`, `LLM_BASE_URL`, fallback `FALLBACK_LLM_*` | AI email personalization (falls back to static templates on error) |
| SMTP | `GMAIL_USER`, `GMAIL_APP_PASSWORD` | Gophish sending profile + the public contact form |
| Vishing (optional) | `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`, `AZURE_SPEECH_KEY`, `AZURE_SPEECH_REGION`, `APP_BASE_URL`, `VISHING_LIVE` | live voice-phishing calls; falls back to IVR, then simulation, when incomplete |
| Security | `OPS_TOKEN`, `ENVIRONMENT`, `APP_SECRET_KEY` (webhook HMAC), `GDPR_HASH_SALT` (min 16 chars, must stay stable) | see §4 |
| Ops tuning | `SCHEDULER_INTERVAL_SECONDS` (default 300), `ALERT_WEBHOOK_URL`, `ALERT_WEBHOOK_THRESHOLD` | background loop, alerts |

## 3. Starting the stack

```powershell
.\start_gophish.ps1                                  # embedded Gophish (admin UI: https://127.0.0.1:3333)
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000   # API + console
```

Verify: `GET /health` reports database and Gophish reachability;
`GET /ops/config` returns `{auth_required, version}`; the console at
`http://localhost:8000/console` shows its "Live" state (auto-refresh 10 s).

## 4. Security setup

- **`OPS_TOKEN`** — required in production. All data endpoints
  (`/clients`, `/campaigns`, `/reports`, `/risk`, `/training`, `/templates`,
  `/ops/*`, `POST /vishing/trigger`) reject requests without
  `Authorization: Bearer <OPS_TOKEN>`. The console asks for the token once
  (stored in `sessionStorage`); the CLI reads it from the `OPS_TOKEN` env var.
- **`ENVIRONMENT=production`** — with an empty `OPS_TOKEN`, protected
  endpoints return 503 instead of running wide open.
- **Rate limits** — contact form 5/hour/IP; 10 failed token attempts per IP
  trigger a 5-minute 429 lockout (in-memory; per process instance).
- Optional: set `REDIS_URL` for shared rate-limit state across replicas (if configured).
- Failed logins, purges, and campaign launches are written to the `audit_logs` table (`/ops/activity` shows them).

## 5. Onboarding a client

```powershell
phishguard client add --name "Dresdner Feinmechanik GmbH" --email admin@kunde.de --employees 50
phishguard client list
```

Employees (name, role, department, group) are added under the client —
`scripts/update_emails.py` bulk-sets/updates addresses in the dev database.
**Groups matter**: the planner picks scenarios per employee group (executive,
finance, engineering, hr, it, sales, general). `client_onboarding_template.xlsx`
is the bulk-import sheet used during manual onboarding.

## 6. Running campaigns

```powershell
# full run against live targets (prod mode strips the test aliases)
phishguard campaign run --client-id <uuid> --difficulty medium
# safe rehearsal: rorshopping+alias@gmail.com inboxes only
phishguard campaign run-test --client-id <uuid>
```

From the console: **Setup** launches a client campaign choosing
`difficulty` (`easy|medium|hard`) and `email_mode` (`test` default, `prod`);
same via `POST /ops/clients/{id}/campaign`.

Scheduling: the background loop (every `SCHEDULER_INTERVAL_SECONDS`) pulls
results from Gophish and launches due scheduled campaigns — **but only when
Gophish is healthy** (the guard avoids burning LLM calls and piling up
zombie campaigns while Gophish is down; you'll see
"Skipping scheduled-campaign pass" in the log). `campaign schedule` sets a
date manually; **Run scheduler now** / **Monitor running** buttons and
`POST /ops/run-scheduler`, `POST /ops/monitor` trigger a pass immediately.

## 7. Monitoring & reports

- Console **Dashboard**: global counts (clients, employees, campaigns by
  status, sends/clicks/credentials), risk distribution, running campaigns,
  recent activity feed. **Clients** tab: per-client risk dashboards.
- CLI: `phishguard reports client <id>`, `reports campaign <id>`,
  `reports campaign-csv <id>` / `client-csv <id>` (CSV export),
  `risk client/summary/departments/heatmap`.
- Risk model: `credentials_submitted` +100, `link_clicked` +60,
  `email_opened` +20, `reported_phishing` −30, capped 0–100
  (low <15, medium 15–40, high 40–70, critical ≥70). Trend + EMA
  prediction per employee under `risk trend` / `/risk/employee/{id}/predict`.

## 8. Training

Bulk-assign after a campaign:
`POST /training/campaign/{id}/assign-all` targets employees whose results
show failures (e.g. clicked). Track and close the loop with
`phishguard training pending / complete / roi`. Five content modules ship
in `src/engine/training_engine.py` (`TRAINING_TYPES`).

## 9. Vishing (voice phishing)

`phishguard vishing trigger` starts a call. Fallback chain: **live
conversational** (Twilio + Azure Speech, all vars from §2 set) → **IVR**
(DTMF) → **simulation**. The Twilio webhooks under `/webhooks/vishing/*`
are HMAC-validated (`APP_SECRET_KEY`) and the audio WebSocket is
session-scoped.

## 10. Deploying the public website

Vercel serves the **repo root**, which must mirror `static/` byte-for-byte:

```powershell
# after editing anything in static/:
python scripts/sync_mirror.py          # copy changed mirrors
python scripts/sync_mirror.py --check  # must pass right before deploying
vercel --prod
```

`tests/test_root_mirror.py` fails the suite when mirrors drift; the sync
list lives in `src/root_mirror.py`.

## 11. Routine operations & troubleshooting

| Symptom / task | Action |
|---|---|
| Scheduler inactive | Log says "No GOPHISH_API_KEY set — scheduler disabled"; set the key and restart |
| Campaigns stuck while Gophish down | Expected guard behavior; fix Gophish, then **Run scheduler now** |
| Leftover Gophish campaigns from tests | `python scripts/cleanup_gophish.py` |
| Reset dev database | delete `phishguard_test.db`; tables are recreated at startup (prod schema changes: `alembic upgrade head`, new revisions via `alembic revision --autogenerate`) |
| Contact form broken | `GMAIL_USER`/`GMAIL_APP_PASSWORD` unset or Gmail blocking SMTP; form is rate-limited to 5/hour/IP |
| PII cleanup after a customer ends | `phishguard privacy purge-emails --client-id <uuid>` (see `docs/gdpr-pii.md`) |
| Schema drift between models and DB | `python -m pytest tests/test_migrations.py` fails — create a migration |

## 12. Quick reference

CLI groups: `client`, `campaign`, `vishing`, `risk`, `feedback`,
`training`, `reports`, `template`, `privacy` — each with `--help`.
Interactive API docs: `http://localhost:8000/docs`.
Auth for scripts: `Authorization: Bearer $OPS_TOKEN` on every data call.
