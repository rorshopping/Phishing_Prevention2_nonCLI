# AGENTS.md - Phishing Prevention Platform

## Scope Guide for AI Agents
When asked to work on this project, explore ONLY the relevant files. Do not explore the entire codebase.

| Task Type | Relevant Files |
|---|---|
| **Website / SEO / frontend** | `static/index.html`, `static/impressum.html`, `static/privacy.html`, `static/dpa.html`, `static/404.html`, `static/style.css`, `static/script.js`, `static/analytics.js`, `static/robots.txt`, `static/sitemap.xml`, `src/main.py` (routes for legal/SEO pages only) |
| **Operations console** | `static/console.html`, `static/console.css`, `static/console.js`, `src/api/ops.py` (`/ops/*`), `src/agents/orchestrator.py`, `src/config.py` (`OPS_TOKEN`) |
| **API / backend** | `src/api/*.py`, `src/engine/*.py`, `src/database/*.py`, `src/services/*.py`, `src/config.py` |
| **Agents / pipeline** | `src/agents/*.py`, `src/engine/email_builder.py`, `src/engine/personalizer.py` |
| **Tests** | `tests/` |
| **Gophish binary** `gophish/` | **Do not explore** — separate embedded Go app, irrelevant to Python code |
| **Root mirror files** | **Vercel serves the repo root** (verified live 2026-08-10: deployed bytes == root index.html). Root must mirror `static/` byte-for-byte. Sync list (**21 files**): `index.html`, `privacy.html`, `impressum.html`, `data-processing-agreement.html`←`static/dpa.html`, `404.html`, `robots.txt`, `sitemap.xml`, `llms.txt`, `llms-full.txt`, `style.css`, `style.min.css`, `script.js`, `script.min.js`, `analytics.js`, `og-image.png`, `logo.svg`, `fonts/inter-variable.woff2`←`static/fonts/`, `fonts/jetbrains-mono-variable.woff2`←`static/fonts/`, `console.html`, `console.css`, `console.js`. After any `static/` edit, copy the affected file(s) to root before `vercel --prod` (see `docs/seo-audit.md` §Root-Duplicate Fix). |

## Quick Start

### Start Gophish
```powershell
.\start_gophish.ps1
```

### Run a test campaign
```powershell
$env:PYTHONPATH = "C:\Users\Richard\Documents\Projects\Phishing_Prevention2_nonCLI"
python debug_execution2.py
```
Or use the full orchestrator flow:
```powershell
python debug_execution.py
```

### Environment
- `.env` contains all config (DB, Gophish API key, LLM settings)
- Gophish API URL: `https://127.0.0.1:3333/api`
- Gophish admin UI: `https://127.0.0.1:3333`
- LLM: OpenRouter free model (`inclusionai/ling-3.0-flash:free`)

### Test Emails
- `rorshopping@gmail.com` - uses Gmail SMTP via Gophish
- Test aliases: `rorshopping+{alice,bob,carol}@gmail.com`

## Architecture
- `src/agents/orchestrator.py` - runs the 4-agent pipeline
- `src/agents/execution_agent.py` - creates Gophish resources, grouped by scenario
- `src/engine/email_builder.py` - LLM + fallback email generation
- `src/engine/risk_engine.py` - weighted risk scoring per employee, trend analytics, dashboard data
- `src/engine/report_engine.py` - HTML report generation (client + campaign), JSON dashboard API
- `src/engine/training_engine.py` - training assignment, bulk campaign assignment, completion tracking, content generation
- `src/services/gophish_service.py` - wraps Gophish API client
- `src/database/models.py` - SQLAlchemy ORM (Campaign stores comma-separated Gophish IDs)

## API Endpoints

### Risk Scoring (`/risk`)
| Endpoint | Description |
|---|---|
| `GET /risk/employee/{id}` | Compute & store risk score for an employee |
| `GET /risk/employee/{id}/trend` | Risk score history with trend direction (`improving`/`stable`/`worsening`) |
| `GET /risk/employee/{id}/predict` | Predicted next score (EMA), trend direction, confidence score |
| `GET /risk/client/{id}` | Client-level risk summary (avg, distribution, top 5 with trend) |
| `GET /risk/client/{id}/trend` | Monthly aggregated avg risk scores (chart-ready) |
| `GET /risk/client/{id}/dashboard` | Full dashboard payload (summary + trend + coverage) |

### Reports (`/reports`)
| Endpoint | Description |
|---|---|
| `GET /reports/client/{id}?days=365` | HTML client report (overview, risk, campaign history) |
| `GET /reports/client/{id}/json?days=365` | JSON version for interactive dashboards |
| `GET /reports/campaign/{id}` | HTML per-campaign report (results, employee details) |

### Training (`/training`)
| Endpoint | Description |
|---|---|
| `POST /training/assign` | Assign training to an employee |
| `POST /training/campaign/{id}/assign-all` | Bulk-assign training for all failures in a campaign |
| `POST /training/{id}/complete` | Mark training as completed |
| `GET /training/pending?client_id=` | List pending training assignments |
| `GET /training/content/{type}` | Training HTML content |

### Operations Console (`/console`)
Web console for demos/control: system health, global stats, running campaigns, per-client dashboards, training, vishing, audit log + manual triggers. Auto-refreshes every 10s ("Live" toggle).
- Protected by `OPS_TOKEN` in `.env` (sent as `Authorization: Bearer <token>`). Empty = open (dev only).
- Console trigger endpoints require the orchestrator flow: `POST /ops/clients/{id}/campaign` with `{difficulty, email_mode: test|prod, vishing_enabled}` — **default email_mode is `test`** (aliases).
- Background scheduler task status is reported via `src/api/ops.py::scheduler_task` (set in `main.py` startup).

| Endpoint | Description |
|---|---|
| `GET /ops/config` | Public: `{auth_required, version}` — console uses this before auth |
| `GET /ops/status` | System health + global counts + risk distribution + running campaigns + recent activity |
| `GET /ops/campaigns` / `GET /ops/vishing` / `GET /ops/training` | Cross-client lists (filter by `status`, `client_id`) |
| `GET /ops/activity?limit=` | Audit log feed with client names |
| `POST /ops/monitor` | Manually run `monitor_all_active_campaigns()` (pull results from Gophish now) |
| `POST /ops/campaigns/{id}/monitor` | Force-monitor a single campaign |
| `POST /ops/run-scheduler` | Manually run `run_scheduled_campaigns()` (launches any due campaigns) |
| `POST /ops/clients/{id}/campaign` | Manually trigger a full campaign via the orchestrator |

## Risk Scoring Model
- `credentials_submitted` = +100, `link_clicked` = +60, `email_opened` = +20, `reported_phishing` = -30
- Score capped at 0–100. Levels: low (<15), medium (15–40), high (40–70), critical (≥70)
- Risk trend endpoint returns monthly-aggregated averages for charting (Chart.js, etc.)

## Key Fixes (July 2026)
1. **Identical emails fix**: `execution_agent.py` now accepts `plan` dict, groups employees by scenario, and creates separate Gophish campaigns per scenario group
2. **Company name fix**: `_generate_single_template()` queries the Client table for company name instead of parsing campaign name
3. **Mapping**: `PLANNER_TO_EMAIL_SCENARIO` in `email_builder.py` maps planner scenario names to `ScenarioType` enums
4. **Duplicate code removed**: `risk_scoring.py` (duplicate of `risk_engine.py`) removed. All risk scoring flows through `risk_engine.py`.
5. **Dashboard JSON endpoint**: New `GET /reports/client/{id}/json` returns structured JSON (summary, risk trend, campaign list) for frontend charting.

## Common Commands

### Check Gophish running
```powershell
Get-Process -Name "gophish"
```

### Reset test database
```powershell
Remove-Item phishguard_test.db -Force
```

### Clean Gophish campaigns
```powershell
python test_cleanup_gophish.py
```
