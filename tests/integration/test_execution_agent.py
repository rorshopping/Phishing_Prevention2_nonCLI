from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
import pytest_asyncio

from src.database.models import (
    Campaign, CampaignStatus, Employee, EmployeeGroup,
    CampaignResult, AuditLog,
)
from src.agents.execution_agent import ExecutionAgent


MOCK_GOPHISH_RESPONSES = {
    "create_template": {"id": 101, "name": "TPL-Test"},
    "create_group": {"id": 201, "name": "GRP-Test"},
    "create_page": {"id": 301, "name": "PAGE-Test"},
    "create_smtp_profile": {"id": 401, "name": "SMTP-Test"},
    "launch_campaign": {"id": 501, "name": "CAMP-Test"},
}


@pytest_asyncio.fixture
async def execution_setup(patched_db_session, sample_client):
    async with patched_db_session() as db:
        employees = [
            Employee(
                id=uuid4(), client_id=sample_client.id,
                email_hash="alice@test.de", name="Alice",
                role="CFO", department="Finance",
                group=EmployeeGroup.finance,
            ),
            Employee(
                id=uuid4(), client_id=sample_client.id,
                email_hash="bob@test.de", name="Bob",
                role="Engineer", department="Engineering",
                group=EmployeeGroup.engineering,
            ),
        ]
        for e in employees:
            db.add(e)
        await db.flush()

        campaign = Campaign(
            id=uuid4(), client_id=sample_client.id,
            name="Execution Test", status=CampaignStatus.draft,
        )
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        for e in employees:
            await db.refresh(e)

        return campaign, employees


class TestExecutionAgent:
    @pytest.mark.asyncio
    async def test_execute_campaign_success(self, execution_setup, db_engine):
        campaign, employees = execution_setup
        plan = {
            "employee_assignments": [
                {"employee_id": str(employees[0].id), "group": "finance", "scenario_type": "invoice_fraud"},
                {"employee_id": str(employees[1].id), "group": "engineering", "scenario_type": "cloud_notification"},
            ],
        }

        mock_gophish = AsyncMock()
        async def mock_create_template(template):
            return {"id": 101, "name": template["name"]}
        async def mock_create_group(group):
            return {"id": 201, "name": group["name"]}
        async def mock_create_page(page):
            return {"id": 301, "name": page["name"]}
        async def mock_create_smtp(smtp):
            return {"id": 401}
        async def mock_launch_campaign(payload):
            return {"id": 501, "name": payload["name"]}

        mock_gophish.create_template.side_effect = mock_create_template
        mock_gophish.create_group.side_effect = mock_create_group
        mock_gophish.create_page.side_effect = mock_create_page
        mock_gophish.create_smtp_profile.side_effect = mock_create_smtp
        mock_gophish.launch_campaign.side_effect = mock_launch_campaign

        agent = ExecutionAgent(gophish=mock_gophish)

        with patch("src.agents.execution_agent.generate_email", new=AsyncMock(return_value={
            "subject": "Test Subject",
            "body_html": "<p>Test body with {{.URL}}</p>",
        })):
            success = await agent.execute_campaign(campaign.id, plan)

        assert success is True

        import src.database.session as db_module
        async with db_module.async_session() as db:
            from sqlalchemy import select
            result = await db.execute(select(Campaign).where(Campaign.id == campaign.id))
            updated = result.scalar_one()
            assert updated.status == CampaignStatus.running
            assert updated.gophish_campaign_id is not None
            assert updated.gophish_page_id is not None

            result = await db.execute(
                select(CampaignResult).where(CampaignResult.campaign_id == campaign.id)
            )
            results = result.scalars().all()
            assert len(results) == 2

    @pytest.mark.asyncio
    async def test_execute_campaign_no_employees(self, execution_setup, db_engine):
        campaign, _ = execution_setup

        import src.database.session as db_module
        async with db_module.async_session() as db:
            from sqlalchemy import select, delete
            await db.execute(delete(Employee).where(Employee.client_id == campaign.client_id))
            await db.commit()

        mock_gophish = AsyncMock()
        agent = ExecutionAgent(gophish=mock_gophish)
        success = await agent.execute_campaign(campaign.id, None)
        assert success is True

    @pytest.mark.asyncio
    async def test_execute_campaign_unknown_campaign(self):
        mock_gophish = AsyncMock()
        agent = ExecutionAgent(gophish=mock_gophish)
        success = await agent.execute_campaign(uuid4(), None)
        assert success is False

    @pytest.mark.asyncio
    async def test_execute_campaign_creates_audit_log(self, execution_setup, db_engine):
        campaign, employees = execution_setup
        plan = {
            "employee_assignments": [
                {"employee_id": str(employees[0].id), "group": "finance", "scenario_type": "invoice_fraud"},
            ],
        }

        mock_gophish = AsyncMock()
        mock_gophish.create_template.return_value = {"id": 101}
        mock_gophish.create_group.return_value = {"id": 201}
        mock_gophish.create_page.return_value = {"id": 301}
        mock_gophish.create_smtp_profile.side_effect = Exception("already exists")
        mock_gophish.launch_campaign.return_value = {"id": 501}

        agent = ExecutionAgent(gophish=mock_gophish)
        with patch("src.agents.execution_agent.generate_email", new=AsyncMock(return_value={
            "subject": "Test", "body_html": "<p>{{.URL}}</p>",
        })):
            success = await agent.execute_campaign(campaign.id, plan)

        assert success is True

        import src.database.session as db_module
        async with db_module.async_session() as db:
            from sqlalchemy import select
            result = await db.execute(
                select(AuditLog).order_by(AuditLog.created_at.desc()).limit(1)
            )
            log = result.scalar_one()
            assert log.action == "campaign_executed"
            assert log.details["employee_count"] == 2
