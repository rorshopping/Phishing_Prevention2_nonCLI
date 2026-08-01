from uuid import uuid4
from datetime import datetime, timezone

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.database.models import (
    Client, Employee, EmployeeGroup, Campaign, CampaignStatus,
    CampaignResult, VishingSession, AuditLog,
)


class TestClient:
    @pytest.mark.asyncio
    async def test_create_client(self, db_session):
        client = Client(
            id=uuid4(),
            company_name="Test AG",
            contact_email="admin@test.ag",
            industry="Finance",
            employee_count=100,
            country="DE",
            campaigns_per_year=25,
            vishing_enabled=True,
        )
        db_session.add(client)
        await db_session.commit()

        result = await db_session.execute(
            select(Client).where(Client.company_name == "Test AG")
        )
        saved = result.scalar_one()
        assert saved.contact_email == "admin@test.ag"
        assert saved.industry == "Finance"
        assert saved.employee_count == 100
        assert saved.is_active is True

    @pytest.mark.asyncio
    async def test_client_defaults(self, db_session):
        client = Client(
            id=uuid4(), company_name="DefaultCo",
            contact_email="d@d.com",
        )
        db_session.add(client)
        await db_session.commit()

        assert client.is_active is True
        assert client.country == "DE"
        assert client.campaigns_per_year == 25
        assert client.vishing_enabled is False

    @pytest.mark.asyncio
    async def test_client_cascade_delete_employees(self, db_session):
        client = Client(
            id=uuid4(), company_name="CascadeCo",
            contact_email="c@c.com",
        )
        db_session.add(client)
        await db_session.flush()

        emp = Employee(
            id=uuid4(), client_id=client.id,
            email_hash="emp@c.com", name="Test Emp",
        )
        db_session.add(emp)
        await db_session.commit()

        await db_session.delete(client)
        await db_session.commit()

        result = await db_session.execute(
            select(Employee).where(Employee.client_id == client.id)
        )
        assert result.scalar_one_or_none() is None


class TestEmployee:
    @pytest.mark.asyncio
    async def test_create_employee(self, sample_client, db_session):
        emp = Employee(
            id=uuid4(),
            client_id=sample_client.id,
            email_hash="alice@test.de",
            name="Alice Schmidt",
            role="Developer",
            department="Engineering",
            group=EmployeeGroup.engineering,
        )
        db_session.add(emp)
        await db_session.commit()

        result = await db_session.execute(
            select(Employee).where(Employee.email_hash == "alice@test.de")
        )
        saved = result.scalar_one()
        assert saved.name == "Alice Schmidt"
        assert saved.group == EmployeeGroup.engineering

    @pytest.mark.asyncio
    async def test_employee_default_group(self, sample_client, db_session):
        emp = Employee(
            id=uuid4(), client_id=sample_client.id,
            email_hash="new@test.de",
        )
        db_session.add(emp)
        await db_session.commit()

        assert emp.group == EmployeeGroup.general


class TestCampaign:
    @pytest.mark.asyncio
    async def test_create_campaign(self, sample_client, db_session):
        campaign = Campaign(
            id=uuid4(),
            client_id=sample_client.id,
            name="Q1 Phishing Test",
            status=CampaignStatus.draft,
            difficulty="medium",
        )
        db_session.add(campaign)
        await db_session.commit()

        result = await db_session.execute(
            select(Campaign).where(Campaign.name == "Q1 Phishing Test")
        )
        saved = result.scalar_one()
        assert saved.status == CampaignStatus.draft
        assert saved.difficulty == "medium"

    @pytest.mark.asyncio
    async def test_campaign_status_transitions(self, sample_client, db_session):
        campaign = Campaign(
            id=uuid4(), client_id=sample_client.id,
            name="Status Test", status=CampaignStatus.draft,
        )
        db_session.add(campaign)
        await db_session.commit()

        campaign.status = CampaignStatus.running
        await db_session.commit()

        result = await db_session.execute(
            select(Campaign).where(Campaign.id == campaign.id)
        )
        updated = result.scalar_one()
        assert updated.status == CampaignStatus.running

        campaign.status = CampaignStatus.completed
        campaign.completed_at = datetime.now(timezone.utc)
        await db_session.commit()

        result = await db_session.execute(
            select(Campaign).where(Campaign.id == campaign.id)
        )
        completed = result.scalar_one()
        assert completed.status == CampaignStatus.completed
        assert completed.completed_at is not None

    @pytest.mark.asyncio
    async def test_gophish_id_storage(self, sample_client, db_session):
        campaign = Campaign(
            id=uuid4(), client_id=sample_client.id,
            name="Gophish IDs",
        )
        db_session.add(campaign)
        await db_session.commit()

        campaign.gophish_campaign_id = "42,43,44"
        campaign.gophish_group_id = "10,11,12"
        campaign.gophish_template_id = "5,6,7"
        campaign.gophish_page_id = 1
        await db_session.commit()

        result = await db_session.execute(
            select(Campaign).where(Campaign.id == campaign.id)
        )
        saved = result.scalar_one()
        assert saved.gophish_campaign_id == "42,43,44"
        assert saved.gophish_page_id == 1


class TestRelationships:
    @pytest.mark.asyncio
    async def test_client_campaigns_relationship(self, sample_client, db_session):
        campaigns = [
            Campaign(id=uuid4(), client_id=sample_client.id, name=f"Camp {i}")
            for i in range(3)
        ]
        for c in campaigns:
            db_session.add(c)
        await db_session.commit()

        result = await db_session.execute(
            select(Client)
            .where(Client.id == sample_client.id)
            .options(selectinload(Client.campaigns))
        )
        client = result.scalar_one()
        assert len(client.campaigns) == 3

    @pytest.mark.asyncio
    async def test_employee_results_relationship(self, sample_client, sample_campaign, db_session):
        emp = Employee(
            id=uuid4(), client_id=sample_client.id,
            email_hash="emp@test.de",
        )
        db_session.add(emp)
        await db_session.flush()

        result = CampaignResult(
            id=uuid4(), campaign_id=sample_campaign.id,
            employee_id=emp.id,
        )
        db_session.add(result)
        await db_session.commit()

        result = await db_session.execute(
            select(Employee)
            .where(Employee.id == emp.id)
            .options(selectinload(Employee.results))
        )
        loaded_emp = result.scalar_one()
        assert len(loaded_emp.results) == 1
        assert loaded_emp.results[0].campaign_id == sample_campaign.id
