"""DB-backed endpoint tests: reports, risk scoring, training, ops status.

Runs the app in-process on the test event loop via httpx's ASGI transport
(TestClient's portal loop would break the loop-bound aiosqlite connections
used by the patched session fixture).
"""
import uuid
from datetime import datetime, timezone

import httpx
import pytest
from httpx import ASGITransport, AsyncClient

from src.config import settings
from src.database import models as m
from src.main import app

COMPANY = "Dresdner Feinmechanik GmbH"


@pytest.fixture
def ops_env(monkeypatch):
    """Valid ops token + fast/deterministic health checks."""
    monkeypatch.setattr(settings, "ops_token", "test-token")
    async def fake_health():
        return {"database": "ok", "gophish": "unreachable"}
    monkeypatch.setattr("src.api.ops._health_check", fake_health)
    return "test-token"


def bearer(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def client(token: str) -> AsyncClient:
    return AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers=bearer(token),
    )


async def seed_results(patched_db_session, campaign, employees, **flags):
    """Attach one CampaignResult per employee to the campaign."""
    async with patched_db_session() as s:
        for emp in employees:
            s.add(m.CampaignResult(
                campaign_id=campaign.id,
                employee_id=emp.id,
                **flags,
            ))
        await s.commit()


# ---------- reports ----------

@pytest.mark.asyncio
async def test_client_report_html(patched_db_session, sample_client, ops_env):
    async with client(ops_env) as c:
        resp = await c.get(f"/reports/client/{sample_client.id}")
    assert resp.status_code == 200
    assert "text/html" in resp.headers["content-type"]
    assert COMPANY in resp.text


@pytest.mark.asyncio
async def test_client_report_html_unknown_client_404(patched_db_session, ops_env):
    async with client(ops_env) as c:
        resp = await c.get(f"/reports/client/{uuid.uuid4()}")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Client not found"


@pytest.mark.asyncio
async def test_client_report_json_shape(patched_db_session, sample_client, ops_env):
    async with client(ops_env) as c:
        resp = await c.get(f"/reports/client/{sample_client.id}/json")
    assert resp.status_code == 200
    body = resp.json()
    assert body["client_id"] == str(sample_client.id)
    assert body["company_name"] == COMPANY
    assert "period" in body and "campaigns" in body


@pytest.mark.asyncio
async def test_campaign_report_html_and_csv(
    patched_db_session, sample_campaign, ops_env,
):
    async with client(ops_env) as c:
        html = await c.get(f"/reports/campaign/{sample_campaign.id}")
        csv = await c.get(f"/reports/campaign/{sample_campaign.id}/csv")
    assert html.status_code == 200
    assert "text/html" in html.headers["content-type"]
    assert csv.status_code == 200
    assert "attachment" in csv.headers.get("content-disposition", "")


@pytest.mark.asyncio
async def test_campaign_report_unknown_404(patched_db_session, ops_env):
    async with client(ops_env) as c:
        resp = await c.get(f"/reports/campaign/{uuid.uuid4()}")
    assert resp.status_code == 404


# ---------- risk scoring ----------

@pytest.mark.asyncio
async def test_employee_risk_reflects_click_weight(
    patched_db_session, sample_client, sample_employees, sample_campaign, ops_env,
):
    emp = sample_employees[0]
    await seed_results(
        patched_db_session, sample_campaign, [emp],
        email_opened=True, link_clicked=True,
    )
    async with client(ops_env) as c:
        resp = await c.get(f"/risk/employee/{emp.id}")
    assert resp.status_code == 200
    body = resp.json()
    # email_opened (+20) + link_clicked (+60) = 80 -> critical threshold < 100
    assert body["score"] == 80.0
    assert body["risk_level"] in ("high", "critical")
    assert body["total_campaigns_attended"] == 1


@pytest.mark.asyncio
async def test_employee_risk_caps_at_100(
    patched_db_session, sample_client, sample_employees, sample_campaign, ops_env,
):
    emp = sample_employees[0]
    async with patched_db_session() as s:
        for _ in range(3):
            s.add(m.CampaignResult(
                campaign_id=sample_campaign.id,
                employee_id=emp.id,
                credentials_submitted=True,  # +100 each, capped at 100
            ))
        await s.commit()
    async with client(ops_env) as c:
        resp = await c.get(f"/risk/employee/{emp.id}")
    assert resp.status_code == 200
    assert resp.json()["score"] == 100.0


@pytest.mark.asyncio
async def test_client_risk_summary_shape(
    patched_db_session, sample_client, sample_employees, ops_env,
):
    async with client(ops_env) as c:
        resp = await c.get(f"/risk/client/{sample_client.id}")
    assert resp.status_code == 200
    body = resp.json()
    assert body["client_id"] == str(sample_client.id)
    assert body["total_employees"] == 4
    for level in ("low", "medium", "high", "critical"):
        assert level in body["risk_distribution"]


@pytest.mark.asyncio
async def test_client_dashboard_combines_summary_and_trend(
    patched_db_session, sample_client, ops_env,
):
    async with client(ops_env) as c:
        resp = await c.get(f"/risk/client/{sample_client.id}/dashboard")
    assert resp.status_code == 200
    body = resp.json()
    assert "summary" in body and "risk_trend" in body
    assert "coverage" in body


@pytest.mark.asyncio
async def test_employee_risk_unknown_404(patched_db_session, ops_env):
    async with client(ops_env) as c:
        resp = await c.get(f"/risk/employee/{uuid.uuid4()}")
    assert resp.status_code == 404


# ---------- training ----------

@pytest.mark.asyncio
async def test_training_assign_pending_complete_cycle(
    patched_db_session, sample_employees, sample_campaign, ops_env,
):
    emp = sample_employees[1]
    async with client(ops_env) as c:
        assigned = await c.post(
            "/training/assign",
            params={
                "employee_id": str(emp.id),
                "campaign_id": str(sample_campaign.id),
                "failure_type": "link_clicked",
            },
        )
    assert assigned.status_code == 200, assigned.text
    body = assigned.json()
    assert body["employee_id"] == str(emp.id)
    assert body["status"] in ("pending", "assigned")

    async with client(ops_env) as c:
        pending = await c.get(
            "/training/pending", params={"client_id": str(sample_campaign.client_id)}
        )
        done = await c.post(
            f"/training/{body['assignment_id']}/complete", json={"score_after": 90.0}
        )
        pending_after = await c.get(
            "/training/pending", params={"client_id": str(sample_campaign.client_id)}
        )
    assert done.status_code == 200
    ids_before = {item["id"] for item in pending.json()}
    ids_after = {item["id"] for item in pending_after.json()}
    assert body["assignment_id"] in ids_before
    assert body["assignment_id"] not in ids_after


@pytest.mark.asyncio
async def test_bulk_assign_targets_only_failures(
    patched_db_session, sample_employees, sample_campaign, ops_env,
):
    # 2 of 4 employees clicked the link
    await seed_results(
        patched_db_session, sample_campaign, sample_employees[:2],
        email_opened=True, link_clicked=True,
    )
    async with client(ops_env) as c:
        resp = await c.post(f"/training/campaign/{sample_campaign.id}/assign-all")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


@pytest.mark.asyncio
async def test_training_content_catalog(patched_db_session, ops_env):
    async with client(ops_env) as c:
        resp = await c.get("/training/content/phishing_awareness")
    assert resp.status_code == 200
    body = resp.json()
    assert body["training_type"] == "phishing_awareness"
    assert len(body["html"]) > 0


# ---------- ops status ----------

@pytest.mark.asyncio
async def test_ops_status_shape_with_valid_token(
    patched_db_session, sample_client, sample_employees, ops_env,
):
    async with client(ops_env) as c:
        resp = await c.get("/ops/status")
    assert resp.status_code == 200
    body = resp.json()
    assert set(body) >= {"health", "scheduler", "counts", "risk"}
    assert body["counts"]["clients_total"] == 1
    assert body["counts"]["employees_total"] == 4
