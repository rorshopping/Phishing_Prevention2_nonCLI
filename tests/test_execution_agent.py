"""Unit tests for execution_agent pure logic — employee assignment, scenario grouping, and LLM context sanitization."""

from unittest.mock import MagicMock
import uuid

from src.agents.execution_agent import ExecutionAgent
from src.engine.email_builder import ScenarioType


def make_emp(id_=None, group="general"):
    emp = MagicMock()
    emp.id = id_ or uuid.uuid4()
    emp.group = type("G", (), {"value": group})()
    emp.name = "Test User"
    emp.name_hash = "hashed_name"
    emp.role = "Engineer"
    emp.department = "Engineering"
    emp.linkedin_url = ""
    emp.public_data = {}
    emp.email = "test@example.com"
    emp.email_hash = "hashed_email"
    return emp


class TestGetEmployeeAssignments:
    def test_no_plan_uses_default_scenario(self):
        emp = make_emp()
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._get_employee_assignments(None, [emp])
        assert result[emp.id] == ScenarioType.bank_transfer

    def test_empty_plan_uses_default_scenario(self):
        emp = make_emp()
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._get_employee_assignments({"employee_assignments": []}, [emp])
        assert result[emp.id] == ScenarioType.bank_transfer

    def test_maps_planner_scenario_to_email_scenario(self):
        emp = make_emp()
        plan = {
            "employee_assignments": [
                {"employee_id": str(emp.id), "group": "finance", "scenario_type": "ceo_fraud"}
            ]
        }
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._get_employee_assignments(plan, [emp])
        assert result[emp.id] == ScenarioType.bank_transfer

    def test_credential_harvest_maps_to_password_reset(self):
        emp = make_emp()
        plan = {
            "employee_assignments": [
                {"employee_id": str(emp.id), "group": "it", "scenario_type": "credential_harvest"}
            ]
        }
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._get_employee_assignments(plan, [emp])
        assert result[emp.id] == ScenarioType.password_reset

    def test_unknown_planner_scenario_falls_back(self):
        emp = make_emp()
        plan = {
            "employee_assignments": [
                {"employee_id": str(emp.id), "group": "it", "scenario_type": "nonexistent_scenario"}
            ]
        }
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._get_employee_assignments(plan, [emp])
        assert result[emp.id] == ScenarioType.bank_transfer

    def test_multiple_employees(self):
        emp1 = make_emp(group="finance")
        emp2 = make_emp(group="engineering")
        plan = {
            "employee_assignments": [
                {"employee_id": str(emp1.id), "group": "finance", "scenario_type": "invoice_fraud"},
                {"employee_id": str(emp2.id), "group": "engineering", "scenario_type": "cloud_notification"},
            ]
        }
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._get_employee_assignments(plan, [emp1, emp2])
        assert result[emp1.id] == ScenarioType.invoice
        assert result[emp2.id] == ScenarioType.security_alert

    def test_unassigned_employee_gets_default(self):
        emp1 = make_emp()
        emp2 = make_emp()
        plan = {
            "employee_assignments": [
                {"employee_id": str(emp1.id), "group": "general", "scenario_type": "urgency_alert"}
            ]
        }
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._get_employee_assignments(plan, [emp1, emp2])
        assert result[emp1.id] == ScenarioType.urgent_review
        assert result[emp2.id] == ScenarioType.bank_transfer


class TestGroupEmployeesByScenario:
    def test_groups_by_scenario(self):
        emp1 = make_emp()
        emp2 = make_emp()
        assignments = {emp1.id: ScenarioType.bank_transfer, emp2.id: ScenarioType.password_reset}
        agent = ExecutionAgent(gophish=MagicMock())
        groups = agent._group_employees_by_scenario(assignments, [emp1, emp2])
        assert len(groups) == 2
        assert groups[ScenarioType.bank_transfer] == [emp1]
        assert groups[ScenarioType.password_reset] == [emp2]

    def test_multiple_employees_same_scenario(self):
        emp1 = make_emp()
        emp2 = make_emp()
        assignments = {emp1.id: ScenarioType.bank_transfer, emp2.id: ScenarioType.bank_transfer}
        agent = ExecutionAgent(gophish=MagicMock())
        groups = agent._group_employees_by_scenario(assignments, [emp1, emp2])
        assert len(groups[ScenarioType.bank_transfer]) == 2

    def test_employee_not_in_list_skipped(self):
        emp1 = make_emp()
        orphan_id = uuid.uuid4()
        assignments = {emp1.id: ScenarioType.invoice, orphan_id: ScenarioType.bank_transfer}
        agent = ExecutionAgent(gophish=MagicMock())
        groups = agent._group_employees_by_scenario(assignments, [emp1])
        assert orphan_id not in groups
        assert len(groups[ScenarioType.invoice]) == 1

    def test_empty_assignments(self):
        agent = ExecutionAgent(gophish=MagicMock())
        groups = agent._group_employees_by_scenario({}, [])
        assert groups == {}


class TestSanitizeForLlm:
    def test_extracts_first_name(self):
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._sanitize_for_llm({"name": "Max Mustermann", "role": "CEO"})
        assert result["name"] == "Max"

    def test_single_name_used_as_is(self):
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._sanitize_for_llm({"name": "Employee", "role": "dev"})
        assert result["name"] == "Employee"

    def test_empty_name_defaults(self):
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._sanitize_for_llm({"name": "", "role": ""})
        assert result["name"] == "Employee"
        assert result["role"] == ""

    def test_preserves_department(self):
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._sanitize_for_llm({"name": "Anna", "role": "HR", "department": "Human Resources"})
        assert result["department"] == "Human Resources"

    def test_preserves_group(self):
        agent = ExecutionAgent(gophish=MagicMock())
        result = agent._sanitize_for_llm({"name": "Tom", "role": "dev", "group": "engineering"})
        assert result["group"] == "engineering"
