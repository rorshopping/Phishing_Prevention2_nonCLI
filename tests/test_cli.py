"""Tests for the CLI dispatch layer (src/cli/main.py).

Each command is invoked through click's CliRunner with the HTTP boundary
(_api) mocked, exercising command dispatch, request building, and output
rendering without a live server.
"""

from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner
from httpx import Response

import src.cli.main as cli_mod
from src.cli.main import cli


class _ApiStub:
    def __init__(self):
        self.calls = []
        self.response = Response(200, json={})

    def __call__(self, method, path, **kwargs):
        self.calls.append({"method": method, "path": path, "kwargs": kwargs})
        return self.response


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def api_stub(monkeypatch):
    stub = _ApiStub()
    monkeypatch.setattr(cli_mod, "_api", stub)
    return stub


def invoke(runner, *args):
    return runner.invoke(cli, args)


def last_call(api_stub):
    return api_stub.calls[-1]


def last_json(api_stub):
    return last_call(api_stub)["kwargs"].get("json")


# ── client ───────────────────────────────────────────────────────────────────


class TestClientAdd:
    def test_posts_payload(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "cl_1", "company_name": "Acme"})
        result = invoke(runner, "client", "add", "--name", "Acme", "--email", "a@acme.com")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert call["path"] == "/clients"
        assert last_json(api_stub) == {
            "company_name": "Acme",
            "contact_email": "a@acme.com",
            "industry": None,
            "employee_count": 0,
        }

    def test_optional_fields(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "cl_1", "company_name": "Acme"})
        invoke(runner, "client", "add", "--name", "Acme", "--email", "a@acme.com",
               "--industry", "Tech", "--employees", "25")
        assert last_json(api_stub)["industry"] == "Tech"
        assert last_json(api_stub)["employee_count"] == 25

    def test_requires_name_and_email(self, runner, api_stub):
        result = invoke(runner, "client", "add")
        assert result.exit_code != 0
        assert api_stub.calls == []


class TestClientList:
    def test_lists_clients(self, runner, api_stub):
        api_stub.response = Response(200, json=[{
            "id": "cl_1", "company_name": "Acme", "contact_email": "a@acme.com",
            "industry": "Tech", "employee_count": 25, "is_active": True,
        }])
        result = invoke(runner, "client", "list")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/clients"
        assert call["kwargs"]["params"] == {"active_only": False}
        assert "Acme" in result.output
        assert "a@acme.com" in result.output

    def test_handles_missing_industry(self, runner, api_stub):
        api_stub.response = Response(200, json=[{
            "id": "cl_1", "company_name": "Acme", "contact_email": "a@acme.com",
            "employee_count": 0, "is_active": False,
        }])
        result = invoke(runner, "client", "list")
        assert result.exit_code == 0

    def test_empty_list(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "client", "list")
        assert result.exit_code == 0
        assert "No clients found" in result.output


class TestClientShow:
    def test_shows_client(self, runner, api_stub):
        api_stub.response = Response(200, json={"company_name": "Acme", "id": "cl_1"})
        result = invoke(runner, "client", "show", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/clients/cl_1"
        assert "Acme" in result.output


class TestEmployeesImport:
    CSV = "email_hash,name_hash,role,department,group\n" \
          "h1,n1,CEO,Exec,executive\n" \
          "h2,n2,CFO,Fin,finance\n"

    def test_imports_csv(self, runner, api_stub):
        api_stub.response = Response(200, json=[{"ok": True}, {"ok": True}])
        with runner.isolated_filesystem():
            with open("emps.csv", "w", encoding="utf-8-sig") as f:
                f.write(self.CSV)
            result = invoke(runner, "client", "employees", "import", "cl_1", "emps.csv")
        assert result.exit_code == 0
        assert "Imported 2 employees for client cl_1" in result.output
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert call["path"] == "/clients/cl_1/employees"
        assert last_json(api_stub) == [
            {"email_hash": "h1", "name_hash": "n1", "role": "CEO",
             "department": "Exec", "group": "executive"},
            {"email_hash": "h2", "name_hash": "n2", "role": "CFO",
             "department": "Fin", "group": "finance"},
        ]

    def test_defaults_when_columns_missing(self, runner, api_stub):
        api_stub.response = Response(200, json=[{"ok": True}])
        with runner.isolated_filesystem():
            with open("emps.csv", "w", encoding="utf-8") as f:
                f.write("name_hash,role\nx,CEO\n")
            result = invoke(runner, "client", "employees", "import", "cl_1", "emps.csv")
        assert result.exit_code == 0
        assert last_json(api_stub) == [
            {"email_hash": "", "name_hash": "x", "role": "CEO",
             "department": None, "group": "general"},
        ]

    def test_empty_csv_reports_error(self, runner, api_stub):
        with runner.isolated_filesystem():
            with open("emps.csv", "w", encoding="utf-8") as f:
                f.write("email_hash\n")
            result = invoke(runner, "client", "employees", "import", "cl_1", "emps.csv")
        assert result.exit_code == 0
        assert "No employees found in CSV" in result.output
        assert api_stub.calls == []


# ── campaign ─────────────────────────────────────────────────────────────────


class TestCampaignRun:
    def test_run_prod(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "camp_1", "status": "running"})
        result = invoke(runner, "campaign", "run", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert call["path"] == "/clients/cl_1/campaigns"
        assert call["kwargs"]["params"] == {"email_mode": "prod"}
        assert last_json(api_stub) == {"difficulty": "medium"}
        assert "prod emails" in result.output

    def test_run_test_mode(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "camp_1", "status": "running"})
        result = invoke(runner, "campaign", "run-test", "cl_1", "--difficulty", "hard")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["kwargs"]["params"] == {"email_mode": "test"}
        assert last_json(api_stub) == {"difficulty": "hard"}
        assert "test emails" in result.output

    def test_rejects_invalid_difficulty(self, runner, api_stub):
        result = invoke(runner, "campaign", "run", "cl_1", "--difficulty", "extreme")
        assert result.exit_code != 0
        assert api_stub.calls == []


class TestCampaignList:
    def test_lists_with_client_id(self, runner, api_stub):
        api_stub.response = Response(200, json=[{
            "id": "camp_1", "client_id": "cl_1", "name": "Phish",
            "status": "running", "difficulty": "easy",
            "sent_count": 10, "click_count": 2,
        }])
        result = invoke(runner, "campaign", "list", "--client-id", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/clients/cl_1/campaigns"
        assert "Phish" in result.output

    def test_requires_client_id(self, runner, api_stub):
        result = invoke(runner, "campaign", "list")
        assert result.exit_code == 0
        assert "Provide --client-id" in result.output
        assert api_stub.calls == []

    def test_empty_list(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "campaign", "list", "--client-id", "cl_1")
        assert result.exit_code == 0
        assert "No campaigns found" in result.output


def _results_payload():
    return {
        "campaign": {"name": "Phish", "status": "running", "difficulty": "easy"},
        "results": [
            {"employee_id": "emp_1", "email_opened": True, "link_clicked": True,
             "credentials_submitted": False, "reported_phishing": False,
             "training_completed": True},
            {"employee_id": "emp_2", "email_opened": True, "link_clicked": False,
             "credentials_submitted": True, "reported_phishing": False,
             "training_completed": False},
        ],
    }


class TestCampaignResults:
    def test_prints_table(self, runner, api_stub):
        api_stub.response = Response(200, json=_results_payload())
        result = invoke(runner, "campaign", "results", "camp_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/campaigns/camp_1/results"
        assert "Phish" in result.output

    def test_empty_results(self, runner, api_stub):
        api_stub.response = Response(200, json={"campaign": {"name": "Phish", "status": "draft"}, "results": []})
        result = invoke(runner, "campaign", "results", "camp_1")
        assert result.exit_code == 0
        assert "No results yet" in result.output

    def test_falls_back_to_employee_id(self, runner, api_stub):
        api_stub.response = Response(200, json=_results_payload())
        result = invoke(runner, "campaign", "results", "camp_1")
        assert result.exit_code == 0
        assert "emp_1" in result.output


class TestCampaignMonitor:
    def test_by_campaign_id_with_vulnerable(self, runner, api_stub):
        api_stub.response = Response(200, json=_results_payload())
        result = invoke(runner, "campaign", "monitor", "--campaign-id", "camp_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/campaigns/camp_1/results"
        assert "Sent: 2" in result.output
        assert "Opened: 2 (100.0%)" in result.output
        assert "Clicked: 1 (50.0%)" in result.output
        assert "Employees who need attention" in result.output

    def test_by_campaign_id_empty_results(self, runner, api_stub):
        api_stub.response = Response(200, json={"campaign": {"name": "Phish", "status": "draft", "difficulty": "easy"}, "results": []})
        result = invoke(runner, "campaign", "monitor", "--campaign-id", "camp_1")
        assert result.exit_code == 0
        assert "Sent: 0" in result.output
        assert "(0.0%)" in result.output

    def test_by_client_id(self, runner, api_stub):
        api_stub.response = Response(200, json=[{
            "id": "camp_1", "name": "Phish", "difficulty": "easy",
            "sent_count": 5, "click_count": 1, "fail_count": 0,
        }])
        result = invoke(runner, "campaign", "monitor", "--client-id", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/clients/cl_1/campaigns"
        assert call["kwargs"]["params"] == {"status": "running"}
        assert "Phish" in result.output

    def test_by_client_id_none_running(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "campaign", "monitor", "--client-id", "cl_1")
        assert result.exit_code == 0
        assert "No running campaigns" in result.output

    def test_no_arguments(self, runner, api_stub):
        result = invoke(runner, "campaign", "monitor")
        assert result.exit_code == 0
        assert "--campaign-id" in result.output
        assert api_stub.calls == []


class TestCampaignSchedule:
    def test_schedules(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "camp_1", "scheduled_date": "2026-08-15T10:00:00", "status": "scheduled"})
        result = invoke(runner, "campaign", "schedule", "camp_1", "--date", "2026-08-15T10:00:00")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert call["path"] == "/campaigns/camp_1/schedule"
        assert last_json(api_stub) == {"scheduled_date": "2026-08-15T10:00:00"}
        assert "scheduled" in result.output


# ── vishing ──────────────────────────────────────────────────────────────────


class TestVishingTrigger:
    def test_triggers(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "vs_1"})
        result = invoke(runner, "vishing", "trigger", "emp_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert call["path"] == "/vishing/trigger"
        assert last_json(api_stub) == {"employee_id": "emp_1"}

    def test_with_campaign_id(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "vs_1"})
        invoke(runner, "vishing", "trigger", "emp_1", "--campaign-id", "camp_1")
        assert last_json(api_stub) == {"employee_id": "emp_1", "campaign_id": "camp_1"}


# ── stats / dashboard ────────────────────────────────────────────────────────


class TestStats:
    def test_stats(self, runner, api_stub):
        api_stub.response = Response(200, json={"company_name": "Acme", "total_employees": 10})
        result = invoke(runner, "stats", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/clients/cl_1/stats"
        assert "Acme" in result.output
        assert "Total Employees" in result.output


class TestDashboard:
    def test_dashboard(self, runner, api_stub):
        api_stub.response = Response(200, json={
            "company_name": "Acme",
            "summary": {"total_employees": 50, "total_campaigns": 3, "active_campaigns": 1,
                        "pending_training": 2, "click_rate": 10.0, "fail_rate": 5.0,
                        "vishing_sessions": 4},
            "risk": {"average_risk_score": 22.0, "total_employees_scored": 30,
                     "total_employees": 50,
                     "risk_distribution": {"low": 10, "medium": 5, "high": 2, "critical": 1}},
            "recent_campaigns": [{"name": "Phish", "status": "completed", "difficulty": "easy",
                                  "sent_count": 10, "click_count": 1, "click_rate": 10.0,
                                  "created_at": "2026-08-01T00:00:00"}],
        })
        result = invoke(runner, "dashboard", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/clients/cl_1/dashboard"
        assert "Acme" in result.output
        assert "Employees: 50" in result.output
        assert "Avg Risk Score: 22.0/100" in result.output
        assert "Phish" in result.output

    def test_dashboard_without_recent_campaigns(self, runner, api_stub):
        api_stub.response = Response(200, json={
            "company_name": "Acme",
            "summary": {"total_employees": 0, "total_campaigns": 0, "active_campaigns": 0,
                        "pending_training": 0, "click_rate": 0.0, "fail_rate": 0.0,
                        "vishing_sessions": 0},
            "risk": {},
        })
        result = invoke(runner, "dashboard", "cl_1")
        assert result.exit_code == 0


# ── risk ─────────────────────────────────────────────────────────────────────


class TestRiskEmployee:
    def test_shows_score(self, runner, api_stub):
        api_stub.response = Response(200, json={"score": 60, "risk_level": "high", "total_campaigns_attended": 3})
        result = invoke(runner, "risk", "employee", "emp_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/risk/employee/emp_1"
        assert "60/100" in result.output
        assert "high" in result.output


class TestRiskTrend:
    def test_shows_trend(self, runner, api_stub):
        api_stub.response = Response(200, json=[
            {"calculated_at": "2026-08-01T00:00:00", "score": 20, "risk_level": "medium"},
        ])
        result = invoke(runner, "risk", "trend", "emp_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/risk/employee/emp_1/trend"
        assert call["kwargs"]["params"] == {"limit": 12}

    def test_custom_limit(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        invoke(runner, "risk", "trend", "emp_1", "--limit", "5")
        assert last_call(api_stub)["kwargs"]["params"] == {"limit": 5}

    def test_empty(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "risk", "trend", "emp_1")
        assert result.exit_code == 0
        assert "No risk data yet" in result.output


class TestRiskClient:
    def test_summary(self, runner, api_stub):
        api_stub.response = Response(200, json={
            "average_risk_score": 30,
            "risk_distribution": {"low": 1, "medium": 2, "high": 3, "critical": 4},
            "highest_risk_employees": [{"employee_id": "emp_1", "score": 90, "risk_level": "critical"}],
        })
        result = invoke(runner, "risk", "client", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/risk/client/cl_1"
        assert "30/100" in result.output
        assert "emp_1" in result.output

    def test_without_highest_risk(self, runner, api_stub):
        api_stub.response = Response(200, json={"average_risk_score": 5, "risk_distribution": {}})
        result = invoke(runner, "risk", "client", "cl_1")
        assert result.exit_code == 0


class TestRiskSummary:
    def test_aliases_risk_client(self, runner, api_stub):
        api_stub.response = Response(200, json={"average_risk_score": 30, "risk_distribution": {}})
        result = invoke(runner, "risk", "summary", "cl_1")
        assert result.exit_code == 0
        assert last_call(api_stub)["path"] == "/risk/client/cl_1"


class TestRiskDepartments:
    def test_table(self, runner, api_stub):
        api_stub.response = Response(200, json=[{
            "department": "engineering", "employee_count": 10, "total_sent": 10,
            "click_rate": 20.0, "fail_rate": 5.0, "avg_risk_score": 15.0,
        }])
        result = invoke(runner, "risk", "departments", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/risk/client/cl_1/departments"
        assert "Engineering" in result.output

    def test_empty(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "risk", "departments", "cl_1")
        assert result.exit_code == 0
        assert "No department data yet" in result.output


class TestRiskHeatmap:
    def test_heatmap(self, runner, api_stub):
        api_stub.response = Response(200, json={
            "total_clicks": 5, "peak_day": "monday", "peak_hour": 14,
            "by_day_of_week": {"monday": 5},
            "by_hour": {"14": 3, "15": 2},
        })
        result = invoke(runner, "risk", "heatmap", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/risk/client/cl_1/heatmap"
        assert "5 total clicks" in result.output
        assert "Peak day: monday" in result.output
        assert "mon" in result.output


# ── feedback ─────────────────────────────────────────────────────────────────


def _feedback_payload():
    return [{
        "training_title": "Phishing 101", "score_before": 40,
        "feedback_sent_at": "2026-08-01T00:00:00",
        "feedback_html": "<h1>Great work</h1>" + "x" * 600,
    }]


class TestFeedbackList:
    def test_lists_feedback(self, runner, api_stub):
        api_stub.response = Response(200, json=_feedback_payload())
        result = invoke(runner, "feedback", "list", "emp_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/training/feedback/emp_1"
        assert call["kwargs"]["params"] == {}
        assert "Phishing 101" in result.output

    def test_filter_by_campaign(self, runner, api_stub):
        api_stub.response = Response(200, json=_feedback_payload())
        invoke(runner, "feedback", "list", "emp_1", "--campaign-id", "camp_1")
        assert last_call(api_stub)["kwargs"]["params"] == {"campaign_id": "camp_1"}

    def test_empty(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "feedback", "list", "emp_1")
        assert result.exit_code == 0
        assert "No feedback found" in result.output


class TestFeedbackShow:
    def test_prints_truncated_html(self, runner, api_stub):
        api_stub.response = Response(200, json=_feedback_payload())
        result = invoke(runner, "feedback", "show", "emp_1")
        assert result.exit_code == 0
        assert "--output" in result.output

    def test_writes_output_file(self, runner, api_stub):
        api_stub.response = Response(200, json=_feedback_payload())
        with runner.isolated_filesystem():
            result = invoke(runner, "feedback", "show", "emp_1", "--output", "feedback.html")
            with open("feedback.html", encoding="utf-8") as f:
                content = f.read()
        assert result.exit_code == 0
        assert "Feedback saved to feedback.html" in result.output
        assert content == "<h1>Great work</h1>" + "x" * 600


# ── training ─────────────────────────────────────────────────────────────────


class TestTrainingPending:
    def test_pending(self, runner, api_stub):
        api_stub.response = Response(200, json=[{
            "id": "t_1", "employee_id": "emp_1", "training_type": "phishing",
            "training_title": "Phishing 101", "score_before": 40,
            "assigned_at": "2026-08-01T00:00:00",
        }])
        result = invoke(runner, "training", "pending")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/training/pending"
        assert call["kwargs"]["params"] == {}
        assert "Phishing 101" in result.output

    def test_filter_by_client(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        invoke(runner, "training", "pending", "--client-id", "cl_1")
        assert last_call(api_stub)["kwargs"]["params"] == {"client_id": "cl_1"}

    def test_empty(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "training", "pending")
        assert result.exit_code == 0
        assert "No pending training assignments" in result.output


class TestTrainingAssign:
    def test_assign(self, runner, api_stub):
        api_stub.response = Response(200, json={"training_type": "phishing", "status": "pending"})
        result = invoke(runner, "training", "assign", "emp_1", "camp_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert "/training/assign?employee_id=emp_1&campaign_id=camp_1&failure_type=link_clicked" in call["path"]
        assert "phishing" in result.output

    def test_custom_failure_type(self, runner, api_stub):
        api_stub.response = Response(200, json={"training_type": "x", "status": "pending"})
        invoke(runner, "training", "assign", "emp_1", "camp_1", "--failure-type", "credentials_submitted")
        assert "failure_type=credentials_submitted" in last_call(api_stub)["path"]


class TestTrainingComplete:
    def test_without_score(self, runner, api_stub):
        api_stub.response = Response(200, json={"status": "completed"})
        result = invoke(runner, "training", "complete", "t_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert call["path"] == "/training/t_1/complete"
        assert last_json(api_stub) == {}

    def test_with_score(self, runner, api_stub):
        api_stub.response = Response(200, json={"status": "completed"})
        invoke(runner, "training", "complete", "t_1", "--score-after", "85.5")
        assert last_json(api_stub) == {"score_after": 85.5}


class TestTrainingContent:
    def test_content(self, runner, api_stub):
        api_stub.response = Response(200, json={"title": "Phishing 101", "html": "<p>Learn</p>"})
        result = invoke(runner, "training", "content", "phishing")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/training/content/phishing"
        assert "Phishing 101" in result.output


class TestTrainingRoi:
    def test_roi(self, runner, api_stub):
        api_stub.response = Response(200, json={
            "total_assignments": 10, "total_completed": 6, "total_pending": 4,
            "completion_rate": 60.0, "overall_avg_score_before": 30.0,
            "overall_avg_score_after": 55.0, "overall_score_improvement": 25.0,
            "improvement_percent": 83.3,
            "by_training_type": [{"title": "Phishing 101", "assigned": 5, "completed": 3,
                                  "completion_rate": 60.0, "avg_score_before": 20.0,
                                  "avg_score_after": 40.0, "score_improvement": 20.0,
                                  "improvement_percent": 100.0}],
        })
        result = invoke(runner, "training", "roi", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/training/client/cl_1/roi"
        assert "10 total assignments" in result.output
        assert "Phishing 101" in result.output

    def test_without_by_type(self, runner, api_stub):
        api_stub.response = Response(200, json={
            "total_assignments": 0, "total_completed": 0, "total_pending": 0,
            "completion_rate": 0.0, "overall_avg_score_before": 0.0,
            "overall_avg_score_after": 0.0, "overall_score_improvement": 0.0,
            "improvement_percent": 0.0,
        })
        result = invoke(runner, "training", "roi", "cl_1")
        assert result.exit_code == 0


# ── reports ──────────────────────────────────────────────────────────────────


class TestReportClient:
    def test_prints_truncated_html(self, runner, api_stub):
        api_stub.response = Response(200, text="<html>report</html>")
        result = invoke(runner, "reports", "client", "cl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/reports/client/cl_1"
        assert call["kwargs"]["params"] == {"days": 365}
        assert "use --output" in result.output

    def test_writes_output_file(self, runner, api_stub):
        api_stub.response = Response(200, text="<html>full report</html>")
        with runner.isolated_filesystem():
            result = invoke(runner, "reports", "client", "cl_1", "--output", "report.html")
            with open("report.html", encoding="utf-8") as f:
                content = f.read()
        assert result.exit_code == 0
        assert "Report saved to report.html" in result.output
        assert content == "<html>full report</html>"

    def test_custom_days(self, runner, api_stub):
        api_stub.response = Response(200, text="<html>r</html>")
        invoke(runner, "reports", "client", "cl_1", "--days", "90")
        assert last_call(api_stub)["kwargs"]["params"] == {"days": 90}


class TestReportCampaign:
    def test_writes_output_file(self, runner, api_stub):
        api_stub.response = Response(200, text="<html>camp report</html>")
        with runner.isolated_filesystem():
            result = invoke(runner, "reports", "campaign", "camp_1", "--output", "camp.html")
            with open("camp.html", encoding="utf-8") as f:
                content = f.read()
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/reports/campaign/camp_1"
        assert content == "<html>camp report</html>"


class TestReportCampaignCsv:
    def test_writes_csv(self, runner, api_stub):
        api_stub.response = Response(200, text="email,opened\nx,1\n")
        with runner.isolated_filesystem():
            result = invoke(runner, "reports", "campaign-csv", "camp_1", "--output", "out.csv")
            with open("out.csv", encoding="utf-8") as f:
                content = f.read()
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/reports/campaign/camp_1/csv"
        assert content == "email,opened\nx,1\n"
        assert "Campaign CSV saved" in result.output


class TestReportClientCsv:
    def test_writes_csv(self, runner, api_stub):
        api_stub.response = Response(200, text="name,clicks\nAcme,5\n")
        with runner.isolated_filesystem():
            result = invoke(runner, "reports", "client-csv", "cl_1", "--output", "out.csv")
            with open("out.csv", encoding="utf-8") as f:
                content = f.read()
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/reports/client/cl_1/csv"
        assert call["kwargs"]["params"] == {"days": 365}
        assert content == "name,clicks\nAcme,5\n"


# ── templates ────────────────────────────────────────────────────────────────


class TestTemplateCreate:
    def test_creates(self, runner, api_stub):
        api_stub.response = Response(200, json={"id": "tpl_1", "name": "Invoice"})
        result = invoke(runner, "template", "create", "cl_1", "Invoice",
                        "--description", "Invoice phish", "--difficulty", "hard")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "POST"
        assert call["path"] == "/templates"
        assert last_json(api_stub) == {
            "client_id": "cl_1", "name": "Invoice",
            "description": "Invoice phish", "difficulty": "hard",
        }
        assert "Invoice" in result.output


class TestTemplateList:
    def test_lists(self, runner, api_stub):
        api_stub.response = Response(200, json=[{
            "id": "tpl_1", "name": "Invoice", "client_id": "cl_1",
            "difficulty": "easy", "is_active": True, "created_at": "2026-08-01T00:00:00",
        }])
        result = invoke(runner, "template", "list")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/templates"
        assert call["kwargs"]["params"] == {}
        assert "Invoice" in result.output

    def test_filter_by_client(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        invoke(runner, "template", "list", "--client-id", "cl_1")
        assert last_call(api_stub)["kwargs"]["params"] == {"client_id": "cl_1"}

    def test_empty(self, runner, api_stub):
        api_stub.response = Response(200, json=[])
        result = invoke(runner, "template", "list")
        assert result.exit_code == 0
        assert "No templates found" in result.output


class TestTemplateGet:
    def test_gets(self, runner, api_stub):
        api_stub.response = Response(200, json={
            "name": "Invoice", "description": "Inv", "difficulty": "easy",
            "scenario_weights": {"x": 1}, "is_active": True,
        })
        result = invoke(runner, "template", "get", "tpl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "GET"
        assert call["path"] == "/templates/tpl_1"
        assert "Invoice" in result.output


class TestTemplateDelete:
    def test_deletes(self, runner, api_stub):
        result = invoke(runner, "template", "delete", "tpl_1")
        assert result.exit_code == 0
        call = last_call(api_stub)
        assert call["method"] == "DELETE"
        assert call["path"] == "/templates/tpl_1"
        assert "Template deactivated" in result.output


# ── _api helper ──────────────────────────────────────────────────────────────


class TestApiHelper:
    def test_get_dispatch(self, monkeypatch):
        resp = Response(200, json={"ok": True})
        fake_httpx = MagicMock()
        fake_httpx.get.return_value = resp
        monkeypatch.setattr(cli_mod, "httpx", fake_httpx)
        out = cli_mod._api("GET", "/x", params={"a": 1})
        assert out is resp
        fake_httpx.get.assert_called_once_with(f"{cli_mod.API_BASE}/x", params={"a": 1}, timeout=30)

    def test_post_dispatch(self, monkeypatch):
        resp = Response(200, json={})
        fake_httpx = MagicMock()
        fake_httpx.post.return_value = resp
        monkeypatch.setattr(cli_mod, "httpx", fake_httpx)
        cli_mod._api("POST", "/x", json={"a": 1})
        fake_httpx.post.assert_called_once_with(f"{cli_mod.API_BASE}/x", json={"a": 1}, params=None, timeout=30)

    def test_put_dispatch(self, monkeypatch):
        resp = Response(200, json={})
        fake_httpx = MagicMock()
        fake_httpx.put.return_value = resp
        monkeypatch.setattr(cli_mod, "httpx", fake_httpx)
        cli_mod._api("PUT", "/x", json={"a": 1})
        fake_httpx.put.assert_called_once_with(f"{cli_mod.API_BASE}/x", json={"a": 1}, params=None, timeout=30)

    def test_delete_dispatch(self, monkeypatch):
        resp = Response(200, json={})
        fake_httpx = MagicMock()
        fake_httpx.delete.return_value = resp
        monkeypatch.setattr(cli_mod, "httpx", fake_httpx)
        cli_mod._api("DELETE", "/x", params={"a": 1})
        fake_httpx.delete.assert_called_once_with(f"{cli_mod.API_BASE}/x", params={"a": 1}, timeout=30)

    def test_unsupported_method(self, monkeypatch):
        fake_httpx = MagicMock()
        monkeypatch.setattr(cli_mod, "httpx", fake_httpx)
        with pytest.raises(ValueError):
            cli_mod._api("PATCH", "/x")

    def test_connect_error_exits(self, monkeypatch, capsys):
        import httpx

        fake_get = MagicMock(side_effect=httpx.ConnectError("connection refused"))
        monkeypatch.setattr(cli_mod.httpx, "get", fake_get)
        with pytest.raises(SystemExit) as exc:
            cli_mod._api("GET", "/x")
        assert exc.value.code == 1
        assert "Could not connect to API" in capsys.readouterr().out
