"""Security-layer tests: data-API auth, production guard, rate limiting,
security headers, and CLI token attachment.

Auth policy (see AGENTS.md): every data endpoint (clients, campaigns,
reports, risk, training, templates, ops) requires the ops token; the
public surface is the static marketing pages, the SEO files, the contact
form (rate-limited), and Twilio webhooks (HMAC-validated in webhooks.py).
"""
import uuid

import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app
from src.utils import rate_limit


@pytest.fixture
def client():
    # No lifespan: startup would create tables in the real DB and start the
    # background scheduler (see tests/test_api.py).
    return TestClient(app)


@pytest.fixture(autouse=True)
def _clear_limiters():
    rate_limit.contact_limiter._events.clear()
    rate_limit.ops_failure_limiter._events.clear()


def _auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


# ---------- data routers require the ops token ----------

_PROTECTED_PATHS = [
    "/clients",
    f"/clients/{uuid.uuid4()}",
    f"/campaigns/{uuid.uuid4()}",
    f"/campaigns/{uuid.uuid4()}/results",
    f"/reports/client/{uuid.uuid4()}",
    f"/reports/campaign/{uuid.uuid4()}",
    f"/risk/employee/{uuid.uuid4()}",
    f"/risk/client/{uuid.uuid4()}",
    "/training/pending",
    "/templates",
    "/ops/status",
]


@pytest.mark.parametrize("path", _PROTECTED_PATHS)
def test_data_endpoints_reject_anonymous_requests(client, monkeypatch, path):
    monkeypatch.setattr(settings, "ops_token", "secret-token")
    assert client.get(path).status_code == 401


@pytest.mark.parametrize("path", _PROTECTED_PATHS)
def test_data_endpoints_reject_wrong_token(client, monkeypatch, path):
    monkeypatch.setattr(settings, "ops_token", "secret-token")
    assert client.get(path, headers=_auth_headers("nope")).status_code == 401


def test_valid_token_reaches_handler(client, monkeypatch, patched_db_session):
    """A correct token passes the auth layer and the handler runs (empty DB)."""
    monkeypatch.setattr(settings, "ops_token", "secret-token")
    resp = client.get("/templates", headers=_auth_headers("secret-token"))
    assert resp.status_code == 200
    assert resp.json() == []


# ---------- production guard on empty OPS_TOKEN ----------

def test_production_blocks_open_console(client, monkeypatch):
    monkeypatch.setattr(settings, "ops_token", "")
    monkeypatch.setattr(settings, "environment", "production")
    resp = client.get("/ops/status")
    assert resp.status_code == 503
    assert "OPS_TOKEN" in resp.json()["detail"]


def test_production_blocks_open_data_api(client, monkeypatch):
    monkeypatch.setattr(settings, "ops_token", "")
    monkeypatch.setattr(settings, "environment", "production")
    assert client.get("/clients").status_code == 503


def test_development_allows_open_console(client, monkeypatch):
    monkeypatch.setattr(settings, "ops_token", "")
    monkeypatch.setattr(settings, "environment", "development")
    # Auth disabled -> request proceeds to the DB layer. The in-memory test
    # DB has no matching campaign; 404 (not 401/503) proves auth passed.
    resp = client.get(f"/campaigns/{uuid.uuid4()}")
    assert resp.status_code == 404


# ---------- ops-token brute-force throttle ----------

def test_failed_ops_attempts_are_rate_limited(client, monkeypatch):
    monkeypatch.setattr(settings, "ops_token", "secret-token")
    monkeypatch.setattr(rate_limit.ops_failure_limiter, "max_events", 3)
    for _ in range(3):
        assert client.get("/ops/status").status_code == 401
    # Limit tripped: even requests without the auth check outcome stay blocked.
    assert client.get("/ops/status").status_code == 429
    # A correct token is also blocked while the failure window is active.
    assert client.get("/ops/status", headers=_auth_headers("secret-token")).status_code == 429


# ---------- contact form throttle ----------

def test_contact_form_is_rate_limited(client, monkeypatch):
    monkeypatch.setattr(settings, "gmail_user", "")  # never touch SMTP
    monkeypatch.setattr(settings, "gmail_app_password", "")
    monkeypatch.setattr(rate_limit.contact_limiter, "max_events", 2)
    form = {
        "company_name": "ACME", "email": "a@b.de",
        "employees": "50", "interest": "demo",
    }
    assert client.post("/api/contact", json=form).status_code == 500  # SMTP off
    assert client.post("/api/contact", json=form).status_code == 500
    assert client.post("/api/contact", json=form).status_code == 429


# ---------- security headers ----------

def test_security_headers_on_html(client):
    resp = client.get("/")
    assert resp.headers["X-Content-Type-Options"] == "nosniff"
    assert resp.headers["X-Frame-Options"] == "DENY"
    assert resp.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    csp = resp.headers["Content-Security-Policy"]
    assert "script-src 'self' https://www.googletagmanager.com" in csp
    assert "frame-ancestors 'none'" in csp
    assert "default-src 'self'" in csp


def test_csp_not_applied_to_non_html(client):
    resp = client.get("/ops/config")
    assert "Content-Security-Policy" not in resp.headers
    assert resp.headers["X-Content-Type-Options"] == "nosniff"


def test_hsts_only_when_https_base_url(client, monkeypatch):
    monkeypatch.setattr(settings, "app_base_url", "")
    assert "Strict-Transport-Security" not in client.get("/ops/config").headers
    monkeypatch.setattr(settings, "app_base_url", "https://phishdefend.ai")
    hsts = client.get("/ops/config").headers["Strict-Transport-Security"]
    assert "max-age=31536000" in hsts


def test_no_cors_wildcard(client):
    resp = client.get("/ops/config", headers={"Origin": "https://evil.example"})
    assert "access-control-allow-origin" not in resp.headers


# ---------- CLI token attachment ----------

def test_cli_sends_bearer_token(monkeypatch):
    import src.cli.main as cli_mod
    from unittest.mock import MagicMock

    monkeypatch.setenv("OPS_TOKEN", "cli-secret")
    captured = {}

    def fake_get(url, **kwargs):
        captured["headers"] = kwargs.get("headers")
        return MagicMock(status_code=200, json=lambda: [])

    monkeypatch.setattr(cli_mod.httpx, "get", fake_get)
    cli_mod._api("GET", "/templates")
    assert captured["headers"]["Authorization"] == "Bearer cli-secret"


def test_cli_omits_header_without_token(monkeypatch):
    import src.cli.main as cli_mod
    from unittest.mock import MagicMock

    monkeypatch.setenv("OPS_TOKEN", "")
    captured = {}

    def fake_get(url, **kwargs):
        captured["headers"] = kwargs.get("headers")
        return MagicMock(status_code=200, json=lambda: [])

    monkeypatch.setattr(cli_mod.httpx, "get", fake_get)
    cli_mod._api("GET", "/templates")
    assert "Authorization" not in captured["headers"]
