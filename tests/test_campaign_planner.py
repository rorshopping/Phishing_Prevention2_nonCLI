from unittest.mock import AsyncMock, patch

import pytest
from uuid import uuid4

from src.database.models import Client, Employee, EmployeeGroup
from src.agents.campaign_planner import CampaignPlanner


@pytest.fixture
def mock_llm():
    mock = AsyncMock()
    mock.structured_generate.return_value = {
        "difficulty": "medium",
        "scenario_weights": {
            "credential_harvest": 50, "malware_attachment": 50,
            "urgency_alert": 50, "ceo_fraud": 50, "invoice_fraud": 50,
            "cloud_notification": 50, "calendar_invite": 50,
            "voicemail_phish": 50, "dropbox_share": 50, "linkedin_message": 50,
        },
        "rationale": "balanced test strategy",
    }
    return mock


@pytest.fixture
def planner(mock_llm):
    return CampaignPlanner(llm_service=mock_llm)


@pytest.fixture
def sample_client():
    return Client(
        id=uuid4(),
        company_name="TestCorp GmbH",
        industry="Technology",
        country="DE",
        employee_count=100,
        campaigns_per_year=25,
    )


@pytest.fixture
def sample_employees():
    return [
        Employee(
            id=uuid4(), name="Alice CFO", role="CFO",
            department="Finance", group=EmployeeGroup.finance,
        ),
        Employee(
            id=uuid4(), name="Bob Eng", role="Engineer",
            department="Engineering", group=EmployeeGroup.engineering,
        ),
        Employee(
            id=uuid4(), name="Carol Exec", role="CEO",
            department="Executive", group=EmployeeGroup.executive,
        ),
    ]


@pytest.mark.asyncio
async def test_plan_campaign_returns_expected_keys(planner, sample_client, sample_employees):
    plan = await planner.plan_campaign(sample_client, sample_employees)
    assert "client_id" in plan
    assert "name" in plan
    assert "scheduled_date" in plan
    assert "difficulty" in plan
    assert "monthly_budget" in plan
    assert "industry_context" in plan
    assert "llm_strategy" in plan
    assert "employee_assignments" in plan


@pytest.mark.asyncio
async def test_plan_campaign_assigns_all_employees(planner, sample_client, sample_employees):
    plan = await planner.plan_campaign(sample_client, sample_employees)
    assert len(plan["employee_assignments"]) == len(sample_employees)


@pytest.mark.asyncio
async def test_plan_campaign_difficulty_from_llm(planner, sample_client, sample_employees):
    plan = await planner.plan_campaign(sample_client, sample_employees)
    assert plan["difficulty"] == "medium"


@pytest.mark.asyncio
async def test_plan_campaign_monthly_budget(planner, sample_client, sample_employees):
    plan = await planner.plan_campaign(sample_client, sample_employees)
    expected = max(1, round(sample_client.campaigns_per_year / 12))
    assert plan["monthly_budget"] == expected


@pytest.mark.asyncio
async def test_plan_campaign_scenario_assignment_with_llm_weights(planner):
    planner.llm.structured_generate.return_value = {
        "difficulty": "medium",
        "scenario_weights": {
            "ceo_fraud": 100, "invoice_fraud": 0, "credential_harvest": 0,
            "malware_attachment": 0, "urgency_alert": 0, "cloud_notification": 0,
            "calendar_invite": 0, "voicemail_phish": 0, "dropbox_share": 0,
            "linkedin_message": 0,
        },
        "rationale": "focus ceo_fraud",
    }
    client = Client(
        id=uuid4(), company_name="FinanceCo",
        industry="Finance", country="DE", employee_count=50, campaigns_per_year=25,
    )
    emp = Employee(
        id=uuid4(), name="Anna CFO", role="CFO",
        department="Finance", group=EmployeeGroup.finance,
    )
    plan = await planner.plan_campaign(client, [emp])
    assignment = plan["employee_assignments"][0]
    assert assignment["group"] == "finance"
    assert assignment["scenario_type"] == "ceo_fraud"


@pytest.mark.asyncio
async def test_decide_scenario_falls_back_to_affinity():
    emp = Employee(
        id=uuid4(), name="Anna CFO", role="CFO",
        department="Finance", group=EmployeeGroup.finance,
    )
    planner = CampaignPlanner(llm_service=AsyncMock())
    scenario = await planner.decide_scenario_for_employee(emp, None)
    assert scenario in ("invoice_fraud", "credential_harvest", "ceo_fraud")


@pytest.mark.asyncio
async def test_plan_campaign_llm_fallback(planner, sample_client, sample_employees):
    planner.llm.structured_generate.side_effect = Exception("LLM unavailable")
    plan = await planner.plan_campaign(sample_client, sample_employees)
    assert plan["difficulty"] == "medium"
    assert len(plan["employee_assignments"]) == len(sample_employees)


@pytest.mark.asyncio
async def test_decide_scenario_for_executive():
    emp = Employee(
        id=uuid4(), name="CEO", role="CEO",
        department="Executive", group=EmployeeGroup.executive,
    )
    planner = CampaignPlanner(llm_service=AsyncMock())
    scenario = await planner.decide_scenario_for_employee(emp)
    assert scenario in ("ceo_fraud", "urgency_alert", "cloud_notification")


@pytest.mark.asyncio
async def test_decide_scenario_for_general():
    emp = Employee(
        id=uuid4(), name="Staff", role="Staff",
        department="General", group=EmployeeGroup.general,
    )
    planner = CampaignPlanner(llm_service=AsyncMock())
    scenario = await planner.decide_scenario_for_employee(emp)
    assert scenario in ("credential_harvest", "urgency_alert", "dropbox_share")
