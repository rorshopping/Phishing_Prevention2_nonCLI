# Current Reporting Suite — Review

## Overview

The PhishGuard reporting system lives in `src/engine/report_engine.py` and serves three endpoints via `src/api/reports.py`. Reports are generated server-side as styled HTML or structured JSON, drawing from the `Campaign`, `CampaignResult`, `RiskScore`, and `TrainingAssignment` tables.

---

## 1. Client Report — HTML (`GET /reports/client/{id}?days=365`)

### Visual Design
- **Gradient header**: Dark navy `linear-gradient(135deg, #1a1a2e, #16213e)` with white text — company name, date range, generation timestamp
- **White content area**: `max-width: 1000px`, centered, padded
- **Footer**: Confidentiality notice

### Sections

#### a) Übersicht (Overview) — 4 metric cards
| Metric | Source | Color Logic |
|---|---|---|
| Mitarbeiter (Employees) | `Employee.count(is_active)` | Neutral |
| Kampagnen (Campaigns) | `Campaign.count(in date range)` | Neutral |
| E-Mails gesendet | `SUM(sent_count)` | Neutral |
| Risikoscore Ø | `AVG(RiskScore.score)` | Green (<15), Yellow (15–39), Red (≥40) |

#### b) Klick- & Failraten (Click & Fail Rates) — 4 metric cards
| Metric | Calculation | Color |
|---|---|---|
| Klickrate | `total_clicks / total_sent * 100` | Red (danger) |
| Failrate (Credentials) | `total_fails / total_sent * 100` | Red (danger) |
| Ausstehende Schulungen | `TrainingAssignment.count(pending)` | Yellow (warning) |
| Abgeschlossene Schulungen | `TrainingAssignment.count(completed)` | Green (success) |

#### c) Risikoverteilung (Risk Distribution) — Bar + table
- **Horizontal bar**: 4 segments (critical/red, high/yellow, medium/blue, low/green) with proportional widths and count labels
- **Detail table**: Rows per risk level with badge styling, count, and percentage

#### d) Kampagnenverlauf (Campaign History) — Table
8 columns: Name, Status, Difficulty, Sent, Clicks, Fails, Click Rate, Date
Rows sorted by `created_at DESC`. Hover highlighting on rows.

### Data Sources Queried
| Query | Tables |
|---|---|
| Client metadata | `clients` |
| Employee count | `employees` (active) |
| Campaign aggregates | `campaigns` (SUM sent/click/fail, COUNT) |
| Campaign detail rows | `campaigns` |
| Avg risk score | `risk_scores` (all-time for client) |
| Risk distribution | `risk_scores` (latest per employee) |
| Training counts | `training_assignments` (pending/completed) |

---

## 2. Client Report — JSON (`GET /reports/client/{id}/json?days=365`)

Same data as the HTML report, returned as structured JSON:

```json
{
  "client_id": "uuid",
  "company_name": "string",
  "period": { "from": "ISO", "to": "ISO" },
  "summary": {
    "total_employees": int,
    "total_campaigns": int,
    "total_emails_sent": int,
    "total_clicks": int,
    "total_fails": int,
    "click_rate": float,
    "fail_rate": float
  },
  "risk": { /* from risk_engine.get_client_risk_summary */ },
  "risk_trend": [ /* monthly averages from risk_engine.get_client_risk_trend */ ],
  "campaigns": [
    {
      "id", "name", "status", "difficulty",
      "sent_count", "click_count", "fail_count",
      "click_rate", "created_at"
    }
  ]
}
```

This is the only endpoint returning data suitable for interactive charting.

---

## 3. Campaign Report — HTML (`GET /reports/campaign/{id}`)

### Sections

#### a) Ergebnisse (Results) — 5 metric cards
| Metric | Calculation | Color |
|---|---|---|
| Gesendet | `len(results)` | Neutral |
| Öffnungsrate | `opened / sent * 100` | Yellow |
| Klickrate | `clicked / sent * 100` | Red |
| Failrate | `submitted / sent * 100` | Red |
| Meldungen | `reported / sent * 100` | Green |

#### b) Mitarbeiter-Details (Employee Detail) — Table
6 columns: Employee (hashed name), Geöffnet, Geklickt, Credentials, Gemeldet, Training
Each cell shows ✅ or —. Rows map to `CampaignResult` records.

### Limitations
- Employee names are truncated to 12 chars of `name_hash` — no way to identify specific users
- No per-employee risk score in campaign context
- No comparison to previous campaign results

---

## 4. Gaps & Weaknesses

| Area | Current State |
|---|---|
| **Trend visualization** | Only available via JSON endpoint — HTML reports are static snapshots |
| **Benchmarking** | None — no industry comparison, no peer group comparison |
| **Predictive analytics** | None — scores are purely historical |
| **Employee-level drill-down** | Campaign report shows hashed names only; no way to see individual risk trajectory |
| **Training impact** | Training counts shown but no correlation with risk score improvement |
| **Export** | HTML only; no PDF, CSV, or scheduled email delivery |
| **Filtering** | Date range only; no scenario type, difficulty, or department filters |
| **Multi-language** | German only; no English fallback |

---

## 5. Suggested Premium Enhancements (3 Ideas)

### 5.1 Industry Benchmarking

**What:** Compare the client's key metrics (click rate, fail rate, avg risk score, training completion rate) against anonymized aggregates from all clients in the same industry/size band.

**Implementation sketch:**
- Background task computes industry percentiles (p25, p50, p75) from `clients.industry`
- Store in an `IndustryBenchmark` table keyed by `(industry, employee_count_band, month)`
- Report displays: "Your click rate of 23% is in the 65th percentile — higher than average for Finance (median: 14%)"
- Visual: gauge chart or percentile marker on the distribution bar

**Value prop for premium:** "Know where you stand — are your employees more or less vulnerable than peers?"

### 5.2 Predictive Risk Scoring

**What:** Forecast an employee's future risk score based on historical trend, training completion, and campaign frequency. Flag employees whose trajectory is worsening before they click a real phishing email.

**Implementation sketch:**
- Compute weighted moving average of `RiskScore` per employee over last N campaigns
- Apply linear or exponential smoothing to predict next-period score
- Add a `risk_trend_direction` field: `improving`, `stable`, `worsening`
- Report section: "3 employees on a worsening trajectory — prioritize training"
- Dashboard widget: trend arrows (↑ → ↓) next to each employee's score

**Value prop for premium:** "Stop reacting. Start predicting which employees need intervention before the next breach."

### 5.3 Automated Executive Summaries with Scheduled Delivery

**What:** Generate a concise PDF/HTML executive brief (1-page, C-suite ready) on a configurable schedule (weekly, monthly) and email it to stakeholders.

**Implementation sketch:**
- Background scheduler generates report snapshot via existing `generate_client_report_json()`
- Render to a clean executive template: top 3 metrics, trend sparkline, 2-sentence AI-generated narrative ("This month your click rate dropped 12% — likely driven by training completion in Finance")
- Use `playwright` or `weasyprint` for PDF conversion
- Send via SMTP to configurable distribution list
- Archive past summaries for year-over-year comparison

**Value prop for premium:** "Security metrics in your inbox every Monday morning — zero effort from your team."

---

## Summary

The current suite provides solid foundation HTML reports and a JSON API for custom dashboards. It covers the basics: aggregate metrics, risk distribution, campaign history, and per-employee detail. The three proposed premium features — benchmarking, predictive scoring, and scheduled executive summaries — each add a distinct layer of value: **context** (where you stand), **foresight** (where you're heading), and **automation** (zero-touch reporting).
