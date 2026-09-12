"""PII data-minimization: POST /ops/privacy/purge-emails.

Nulls plaintext employee emails once campaigns are terminal, keeping the
hashed identity columns intact (see docs/gdpr-pii.md).
"""
import uuid
from unittest.mock import MagicMock

import pytest

from src.cli import main as cli_mod
from src.config import settings
from src.database import models as m
from tests.test_api_data import client as authed_client  # shared client helper


def _employee_with_email(client_id, address):
    return m.Employee(
        id=uuid.uuid4(),
        client_id=client_id,
        email=address,
        email_hash=f"hash-{address}",
        name="Test",
        department="IT",
    )


async def _seed(patched_db_session, sample_client, status, n=2):
    """n employees with plaintext email + a campaign in `status` + results."""
    campaign = m.Campaign(
        id=uuid.uuid4(), client_id=sample_client.id,
        name="Purge Test", status=status,
    )
    employees = [_employee_with_email(sample_client.id, f"e{i}@test.de") for i in range(n)]
    async with patched_db_session() as s:
        s.add(campaign)
        s.add_all(employees)
        await s.flush()
        for emp in employees:
            s.add(m.CampaignResult(campaign_id=campaign.id, employee_id=emp.id))
        await s.commit()
        await s.refresh(campaign)
    return campaign, employees


@pytest.fixture
def token(monkeypatch):
    monkeypatch.setattr(settings, "ops_token", "test-token")
    return "test-token"


@pytest.mark.asyncio
async def test_purge_via_completed_campaign(
    patched_db_session, sample_client, token,
):
    campaign, employees = await _seed(
        patched_db_session, sample_client, m.CampaignStatus.completed,
    )
    async with authed_client(token) as c:
        resp = await c.post(
            "/ops/privacy/purge-emails", json={"campaign_id": str(campaign.id)}
        )
    assert resp.status_code == 200
    assert resp.json()["purged"] == 2

    async with patched_db_session() as s:
        for emp in employees:
            stored = await s.get(m.Employee, emp.id)
            assert stored.email is None          # plaintext gone
            assert stored.email_hash.startswith("hash-")  # hash kept


@pytest.mark.asyncio
async def test_purge_refuses_running_campaign(
    patched_db_session, sample_client, token,
):
    campaign, _ = await _seed(
        patched_db_session, sample_client, m.CampaignStatus.running,
    )
    async with authed_client(token) as c:
        resp = await c.post(
            "/ops/privacy/purge-emails", json={"campaign_id": str(campaign.id)}
        )
    assert resp.status_code == 409


@pytest.mark.asyncio
async def test_client_purge_keeps_employees_in_running_campaigns(
    patched_db_session, sample_client, token,
):
    done, _ = await _seed(patched_db_session, sample_client, m.CampaignStatus.completed)
    active, active_emps = await _seed(
        patched_db_session, sample_client, m.CampaignStatus.running,
    )
    async with authed_client(token) as c:
        resp = await c.post(
            "/ops/privacy/purge-emails", json={"client_id": str(sample_client.id)}
        )
    assert resp.status_code == 200
    async with patched_db_session() as s:
        for emp in active_emps:
            stored = await s.get(m.Employee, emp.id)
            assert stored.email is not None  # still needed for the running campaign


@pytest.mark.asyncio
async def test_purge_requires_an_id(patched_db_session, token):
    async with authed_client(token) as c:
        resp = await c.post("/ops/privacy/purge-emails", json={})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_purge_unknown_campaign_404(patched_db_session, token):
    async with authed_client(token) as c:
        resp = await c.post(
            "/ops/privacy/purge-emails", json={"campaign_id": str(uuid.uuid4())}
        )
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_purge_requires_token(patched_db_session, monkeypatch):
    import httpx as _httpx
    from httpx import ASGITransport, AsyncClient

    from src.main import app

    monkeypatch.setattr(settings, "ops_token", "test-token")  # auth enforced...
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://t") as c:
        resp = await c.post(  # ...but this request sends no Authorization header
            "/ops/privacy/purge-emails", json={"client_id": str(uuid.uuid4())}
        )
    assert resp.status_code == 401


def test_cli_purge_emails_sends_token_and_payload(monkeypatch):
    captured = {}

    def fake_post(url, **kwargs):
        captured["url"] = url
        captured["headers"] = kwargs.get("headers")
        captured["json"] = kwargs.get("json")
        resp = MagicMock(status_code=200)
        resp.json.return_value = {"purged": 3, "client_id": "x", "campaign_id": None}
        return resp

    monkeypatch.setenv("OPS_TOKEN", "cli-token")
    monkeypatch.setattr(cli_mod.httpx, "post", fake_post)
    from click.testing import CliRunner

    result = CliRunner().invoke(
        cli_mod.privacy_purge_emails,
        ["--client-id", str(uuid.uuid4())],
    )
    assert result.exit_code == 0, result.output
    assert captured["url"].endswith("/ops/privacy/purge-emails")
    assert captured["headers"]["Authorization"] == "Bearer cli-token"
