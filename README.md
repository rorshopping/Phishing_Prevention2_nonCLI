# PhishGuard

AI-first phishing simulation platform for SMEs. Fully CLI-managed, GDPR-compliant, with automated campaign orchestration via 4 AI agents.

## Quick Test (2 steps)

Send 4 test emails with different phishing scenarios:

```bash
# 1. Set target emails (one-time)
python update_emails.py --old @gmail.com --new @yourdomain.com
python update_emails.py --old rorshopping --new bob

# 2. Launch test campaign (repeatable)
python run_test.py
```

Step 1 changes the delivery address for all employees. Step 2 creates a throwaway client with 4 employees (alice/bob/carol/dave), assigns each a different scenario (`bank_transfer`, `security_alert`, `shared_doc`, `password_reset`), creates all Gophish resources, and launches the campaigns. Check your inboxes for results.

**How this differs from production runs:**

| | Quick Test | Production |
|---|---|---|
| Trigger | Manual `python run_test.py` | Scheduler (every 5 min), API, or CLI |
| AI | Execution agent only | Full 4-agent pipeline (planner + execution + monitoring + vishing) |
| Data | Throwaway client + 4 hardcoded employees | Real clients/employees from DB or template import |
| Setup | Auto-creates Gophish page, SMTP profile, resources | Same auto-creation, plus webhook listeners |
| Lifecycle | Single shot — no monitoring | Tracks opens/clicks, reports results, triggers vishing |

## Architecture

```
CLI (Click)  ──►  FastAPI REST API  ──►  Gophish (phishing engine)
                      │
                 ┌─────┴─────┐
          AI Agents     GDPR Module
  (planner, execution,   (HMAC-SHA256
   monitoring, vishing)    hashing, retention, DPA)
```

## Quick Start

```bash
# Install
pip install -e .

# Copy and edit env
cp .env.example .env
# Required: GOPHISH_API_KEY, LLM_API_KEY, GDPR_HASH_SALT

# Start API server (runs on port 8000)
python -m uvicorn src.main:app --host 0.0.0.0 --port 8000

# In another terminal, use the CLI
python -m src.cli.main --help
```

## CLI Reference

```bash
# --- Clients ---
python -m src.cli.main client add --name "Acme Corp" --email admin@acme.com \
  --industry Technology --country DE --campaigns-per-year 25
python -m src.cli.main client list
python -m src.cli.main client show <client-id>

# --- Employees ---
python -m src.cli.main client employees import --client-id <id> --file employees.csv
# CSV format: email, name, role, department, group, phone_number
# Groups: executive, finance, hr, it_management, it_staff, sales, engineering, general

# --- Campaigns ---
python -m src.cli.main campaign run --client-id <id>
python -m src.cli.main campaign list --client-id <id>
python -m src.cli.main campaign results <campaign-id>

# --- Risk Scoring ---
python -m src.cli.main risk employee <employee-id>
python -m src.cli.main risk trend <employee-id>
python -m src.cli.main risk client <client-id>
python -m src.cli.main risk departments <client-id>    # ⭐ PREMIUM
python -m src.cli.main risk heatmap <client-id>        # ⭐ PREMIUM
python -m src.cli.main dashboard <client-id>

# --- Training & Feedback ---
python -m src.cli.main training pending --client-id <id>
python -m src.cli.main training assign <employee-id> <campaign-id>
python -m src.cli.main training complete <assignment-id>
python -m src.cli.main training content <training-type>
python -m src.cli.main training roi <client-id>        # ⭐ PREMIUM
python -m src.cli.main feedback list <employee-id>
python -m src.cli.main feedback show <employee-id> --output feedback.html

# --- Reports ---
python -m src.cli.main reports client <client-id> --output report.html
python -m src.cli.main reports campaign <campaign-id> --output report.html

# --- Vishing ---
python -m src.cli.main vishing trigger <employee-id>

# --- Stats ---
python -m src.cli.main stats <client-id>
```

Training types: `phishing_awareness`, `password_security`, `social_engineering`, `safe_browsing`, `data_protection`

## API (Swagger UI at http://localhost:8000/docs)

### Clients
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/clients` | List clients |
| POST | `/clients` | Create client |
| GET | `/clients/{id}` | Client details |
| PUT | `/clients/{id}` | Update client |
| DELETE | `/clients/{id}` | Deactivate client |
| GET | `/clients/{id}/employees` | List employees |
| POST | `/clients/{id}/employees` | Upload employees (CSV batch) |
| POST | `/clients/{id}/campaigns` | Trigger campaign (AI-planned) |
| GET | `/clients/{id}/campaigns` | List campaigns for client |
| GET | `/clients/{id}/stats` | Aggregate stats |
| GET | `/clients/{id}/dashboard` | **Consolidated dashboard** (summary, risk, trend, recent campaigns) |

### Campaigns
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/campaigns/{id}` | Campaign status |
| GET | `/campaigns/{id}/results` | Detailed results |
| POST | `/campaigns/{id}/cancel` | Cancel campaign |

### Risk Scoring
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/risk/employee/{id}` | Compute & return employee risk score |
| GET | `/risk/employee/{id}/trend` | Risk score history (paginated) |
| GET | `/risk/client/{id}` | Client-level risk summary (avg, distribution, top 5) |
| GET | `/risk/client/{id}/trend` | Monthly aggregated avg risk scores |
| GET | `/risk/client/{id}/dashboard` | Full dashboard (summary + trend + coverage) |
| GET | `/risk/client/{id}/departments` | ⭐ **PREMIUM** Department-level benchmarking (click rates, risk by EmployeeGroup) |
| GET | `/risk/client/{id}/heatmap` | ⭐ **PREMIUM** Click timing heatmap (peak day/hour, temporal distribution) |

### Training & Feedback
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/training/assign` | Assign training to an employee |
| POST | `/training/campaign/{id}/assign-all` | Bulk-assign training for all failures |
| POST | `/training/{id}/complete` | Mark training completed |
| GET | `/training/pending` | List pending training |
| GET | `/training/content/{type}` | Training HTML content |
| GET | `/training/feedback/{employee_id}` | Personalized feedback HTML per employee |
| GET | `/training/client/{id}/roi` | ⭐ **PREMIUM** Training ROI (pre/post score improvement by type) |

### Reports
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/reports/client/{id}?days=` | HTML client security report |
| GET | `/reports/client/{id}/json?days=` | JSON version for dashboards |
| GET | `/reports/campaign/{id}` | HTML per-campaign report |

### Webhooks
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/webhooks/gophish` | Gophish event webhook |
| POST | `/webhooks/twilio` | Twilio status callback |

### Other
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/vishing/trigger` | Trigger vishing call |
| GET | `/health` | Health check (DB + Gophish + scheduler) |

### Health Endpoint

```json
GET /health
{
  "status": "ok",
  "service": "phishguard",
  "database": "connected",
  "gophish": "reachable",
  "scheduler": true
}
```

## Automated Campaign Execution

No manual intervention needed day-to-day. The **background scheduler** starts automatically with the server and runs every 5 minutes:

1. **Monitoring** — polls Gophish for all active campaigns, updates click/open counts, finalizes completed campaigns
2. **Scheduling** — checks each client's `campaigns_per_year` pacing, launches new campaigns when due
3. **AI campaign planner** selects difficulty and scenario mix per employee group
4. **Execution agent** creates Gophish resources (group/template/page) and launches the campaign
5. **Vishing follow-up** calls triggered for clickers (if client has vishing enabled)

The scheduler runs in a background `asyncio` task. It is enabled automatically when `GOPHISH_API_KEY` is set.

## Risk Scoring Model

Each employee is scored after every campaign. Scores persist and power the trend analysis.

| Event | Weight |
|-------|--------|
| Credentials submitted | +100 |
| Link clicked | +60 |
| Email opened | +20 |
| Reported phishing | -30 |

Score capped at 0–100. Levels:
- **Low** (<15) — safe behavior
- **Medium** (15–40) — needs awareness
- **High** (40–70) — elevated risk
- **Critical** (≥70) — immediate action required

The campaign planner uses average risk scores to adjust difficulty: avg≥60 → hard, ≥30 → medium, else → easy.

## Training & Feedback Loop

When a campaign completes, employees who clicked or submitted credentials automatically receive:
1. A **risk score update** (via `risk_engine.py`)
2. A **training assignment** matched to their failure type (password_security, phishing_awareness, etc.)
3. **Personalized feedback HTML** with the training content, their score, and actionable tips

Feedback can be retrieved via API (`GET /training/feedback/{employee_id}`) or CLI (`feedback list/show`), and can be saved as HTML for distribution.

## Alert Webhook Integration

Configure a webhook URL in `ALERT_WEBHOOK_URL` to receive real-time campaign completion alerts. The payload includes:
- Campaign name and status
- Sent/opened/clicked/credential counts
- Phish-prone percentage
- Severity level (based on `ALERT_WEBHOOK_THRESHOLD`)

The webhook fires automatically when the monitoring agent finalizes a campaign. Compatible with Slack, Microsoft Teams, or any HTTP endpoint.

## Consolidated Dashboard

The `GET /clients/{id}/dashboard` endpoint returns all client KPIs in a single call:
- Summary stats (employees, campaigns, sent, clicks, fails)
- Risk summary + 12-month trend
- Pending training count
- 5 most recent campaigns with click rates
- Vishing session count

This is designed for frontend dashboards and is accessible via the `dashboard` CLI command.

## ⭐ Premium Features

The following Enterprise-tier endpoints provide advanced analytics beyond the core platform. They are available via API and CLI.

### Departmental Benchmarking (`GET /risk/client/{id}/departments`)

Breaks down risk and phishing susceptibility by EmployeeGroup (executive, finance, IT, HR, etc.). Returns per-department: employee count, emails sent, click rate, fail rate, and average risk score. Departments are sorted by click rate descending.

**CLI:** `risk departments <client-id>`

### Click Heatmap (`GET /risk/client/{id}/heatmap`)

Analyzes all historical click timestamps to reveal temporal patterns. Returns:
- Total clicks analyzed
- Distribution by day of week (Monday–Sunday)
- Distribution by hour of day (0–23)
- Peak click day and peak click hour

This data is chart-ready for building visual heatmaps in a frontend.

**CLI:** `risk heatmap <client-id>`

### Training ROI (`GET /training/client/{id}/roi`)

Measures the effectiveness of security awareness training by comparing risk scores before and after completion. Returns:
- Total assignments, completed, pending, completion rate
- Overall average score before/after training with improvement points and %
- Breakdown by training type (phishing_awareness, password_security, etc.) with individual before/after scores

This directly answers: "Is our training program actually reducing risk?"

**CLI:** `training roi <client-id>`

## Docker Deployment

```bash
# Build and run
docker compose up -d

# Or build standalone
docker build -t phishguard .
docker run -p 8000:8000 --env-file .env phishguard
```

The Dockerfile uses multi-stage builds, runs as a non-root user, and includes a `HEALTHCHECK`.

## Gophish Setup

1. Download and run [Gophish](https://github.com/gophish/gophish/releases) (runs on `:3333` admin, `:8080` phishing)
2. Copy the API key from the Gophish admin output or login at `https://localhost:3333`
3. Set `GOPHISH_API_KEY` and `GOPHISH_API_URL` in `.env`

The platform creates/cleans up all Gophish resources (groups, templates, pages, SMTP profiles) automatically.

## SMTP Configuration

Credentials are configured via environment variables — never hardcoded:

```
GMAIL_USER=your_email@gmail.com
GMAIL_APP_PASSWORD=your_app_password
GMAIL_FROM=your_email@gmail.com
```

The SMTP profile is created in Gophish automatically on each campaign execution.

## Vishing Upsell

When a campaign completes, trigger vishing calls to employees who clicked:

```bash
python -m src.cli.main vishing trigger --campaign-id <id>
```

Each call uses AI-generated scripts (tech support, bank fraud, HR, vendor, CEO fraud scenarios) with optional ElevenLabs voice synthesis.

## GDPR Compliance

- All PII hashed with **HMAC-SHA256** using a dedicated secret salt before storage
- `GDPR_HASH_SALT` must be set to a cryptographically random value (min 16 chars, recommended 64 hex chars)
- Data retention: campaigns 365d, vishing 180d, audit logs 730d
- `cleanup_expired_data()` removes expired records on demand
- `handle_data_subject_access_request()` returns all data for a given email hash
- `generate_data_processing_agreement()` outputs DPA document text
- Consent validation on all campaign operations

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | No | `sqlite+aiosqlite:///phishguard.db` | Database connection |
| `GOPHISH_API_URL` | No | `http://localhost:3333/api` | Gophish API endpoint |
| `GOPHISH_API_KEY` | **Yes** | — | Gophish admin API key |
| `LLM_API_KEY` | **Yes** | — | OpenAI / OpenRouter API key |
| `GDPR_HASH_SALT` | **Yes** | — | Secret salt for HMAC-SHA256 PII hashing (min 16 chars) |
| `LLM_MODEL` | No | `gpt-4o-mini` | Model identifier |
| `LLM_BASE_URL` | No | `https://api.openai.com/v1` | API base URL |
| `GMAIL_USER` | No | — | Gmail SMTP user |
| `GMAIL_APP_PASSWORD` | No | — | Gmail app password |
| `GMAIL_FROM` | No | — | Envelope sender address |
| `EMAIL_SOURCE` | No | `simulation@yourdomain.com` | Fallback sender |
| `TWILIO_ACCOUNT_SID` | No | — | Twilio SID (vishing) |
| `TWILIO_AUTH_TOKEN` | No | — | Twilio auth token |
| `TWILIO_PHONE_NUMBER` | No | — | Outbound caller ID |
| `SERPAPI_API_KEY` | No | — | SerpAPI key (personalization) |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `OPENAI_API_KEY` | No | — | Separate key for OpenAI TTS (falls back to LLM_API_KEY) |
| `ALERT_WEBHOOK_URL` | No | — | **Webhook URL** for campaign completion alerts (Slack, Teams) |
| `ALERT_WEBHOOK_THRESHOLD` | No | `0` | Min clicks to trigger webhook (0 = always) |

## Test Email Setup

To receive test phishing emails, you need an inbox you can access. Any email address works — Gmail, iCloud, Outlook, or a custom domain.

### Using a new email address (e.g. `bob+xyz@icloud.com`)

1. **Create the inbox** — sign up at iCloud (or any provider) to get an address you can log into
2. **Update the database** — change the target email for test employees:

```bash
# Replace all @gmail.com with your domain
python update_emails.py --old @gmail.com --new @icloud.com

# Or set a specific employee
python update_emails.py --name "Alice Smith" --email alice@icloud.com
```

The `email_hash` column is what the execution agent uses (`emp.email or emp.email_hash`). The `update_emails.py` script sets both columns.

```bash
# Bulk replace: swap any substring across all employees
python update_emails.py --old @gmail.com --new @company.com
python update_emails.py --old rorshopping --new bob

# Single employee: set one address by name_hash
python update_emails.py --name "Alice Smith" --email alice@company.com
```

### Quick Test (1-step send)

After setting target emails, run the test campaign:

```bash
python run_test.py
```

This creates 4 employees (alice/bob/carol/dave) with different scenarios (`bank_transfer`, `security_alert`, `shared_doc`, `password_reset`), creates Gophish resources, and launches the campaigns. No other steps needed — Gophish page, SMTP profile, and DB records are all handled automatically.

### SMTP sending

The Gmail SMTP in `.env` can send to **any** recipient — Gmail does not restrict outbound delivery. You only need access to the receiving inbox to check results.

### Database

Employee emails live in `phishguard_test.db` (SQLite):
- `employees.email_hash` — the delivery address used by Gophish
- `employees.email` — alternate column (typically NULL; script sets both)

## Free Tier / OpenRouter

Use free models from OpenRouter:

```
LLM_API_KEY=sk-or-v1-...
LLM_BASE_URL=https://openrouter.ai/api/v1
LLM_MODEL=openrouter/free
```

The auto-router `openrouter/free` spreads requests across all available free models to avoid single-model rate limits.

### Fallback: Groq (free, no credit card)

When OpenRouter is rate-limited, the system falls back to Groq's free tier. Sign up at [console.groq.com](https://console.groq.com), get an API key, and add it to `.env`:

```
FALLBACK_LLM_API_KEY=gsk_your_groq_key
FALLBACK_LLM_BASE_URL=https://api.groq.com/openai/v1
FALLBACK_LLM_MODEL=llama-3.3-70b-versatile
```

If `FALLBACK_LLM_API_KEY` is empty, fallback is skipped and the built-in template fallbacks are used instead.
