# PII Handling: Employee Email — Design & Data Minimization

How this platform handles employee email addresses (GDPR-relevant; the
product's legal pages are in `static/privacy.html` / `dpa.html`).

## The two fields

| Column | Content | Purpose |
|---|---|---|
| `employees.email` | Plaintext address (nullable) | **Campaign targeting only**: Gophish needs a deliverable address when launching a campaign (`src/agents/execution_agent.py::_resolve_target_email` resolves `emp.email or emp.email_hash`). |
| `employees.email_hash` | HMAC-SHA256(salt, address) — non-null | Pseudonymized identity for analytics: monitoring matches webhook results back to employees (`src/agents/monitoring_agent.py`), risk scoring, reports, training. Salt comes from `GDPR_HASH_SALT` (see `src/utils/gdpr.py::hash_pii`). |

Development nuance: in the local test setup the hash column has sometimes
been filled with the plaintext address itself (see `scripts/update_emails.py`),
because the send path falls back to it. That is acceptable only for the
test alias inbox — production data must always contain a real HMAC hash.

## Data minimization (Art. 5(1)(c) GDPR)

Plaintext addresses exist only as long as campaigns can still be launched.
`POST /ops/privacy/purge-emails` (ops-token protected) nulls `email` for:

- all employees of a `client_id`, or the participants of one `campaign_id`,
- **excluding** anyone with participation in a draft/scheduled/running
  campaign of the same client (their address is still needed for sending),
- refusing campaigns that are not yet terminal (HTTP 409).

Hashed columns are never removed, so risk scores, reports, and training
histories remain fully functional after a purge. Each purge writes an
`pii_emails_purged` entry to the audit log.

CLI equivalent:

```powershell
$env:OPS_TOKEN = "<your ops token>"
phishguard privacy purge-emails --client-id <uuid>
phishguard privacy purge-emails --client-id <uuid> --campaign-id <uuid>
```

## Retention targets (from src/utils/gdpr.py)

| Data | Retention |
|---|---|
| Campaign results | 365 days |
| Campaign data | 365 days |
| Vishing sessions | 180 days |
| Audit logs | 730 days |

## Remaining operator obligations (cannot be automated away)

- Keep `GDPR_HASH_SALT` secret and stable — rotating it breaks the link
  between hashes and historical analytics.
- Run the purge (or a full client deletion) as part of offboarding a
  customer; the endpoint is per-client, not global, by design.
- The DPA (`static/dpa.html`) and privacy policy must reflect this
  processing; update them if retention changes.
