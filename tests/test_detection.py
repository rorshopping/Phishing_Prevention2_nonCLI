"""Unit tests for monitoring_agent detection/completion logic.

The primary detection logic in this phishing simulation platform lives in
MonitoringAgent: _detect_completion() and _build_summary() determine when
a campaign is finished and compute aggregate statistics.
"""

from unittest.mock import MagicMock
import uuid

from src.agents.monitoring_agent import MonitoringAgent
from src.database.models import Campaign


def make_campaign(**kwargs):
    defaults = {
        "id": uuid.uuid4(),
        "client_id": uuid.uuid4(),
        "name": "Test Campaign",
        "gophish_campaign_id": "1",
    }
    defaults.update(kwargs)
    return MagicMock(spec=Campaign, **defaults)


def make_result(status="", email="a@b.com", data=None):
    r = {"email": email, "status": status}
    if data is not None:
        r["data"] = data
    return r


class TestDetectCompletion:
    def test_empty_results_returns_false(self):
        agent = MonitoringAgent(gophish=MagicMock())
        assert agent._detect_completion(make_campaign(), []) is False

    def test_all_sent_is_complete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Email Sent"), make_result("Email Sent")]
        assert agent._detect_completion(make_campaign(), results) is True

    def test_mixed_statuses_incomplete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Email Sent"), make_result("Sending")]
        assert agent._detect_completion(make_campaign(), results) is False

    def test_empty_status_incomplete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result(""), make_result("Email Sent")]
        assert agent._detect_completion(make_campaign(), results) is False

    def test_opened_is_complete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Opened"), make_result("Email Sent")]
        assert agent._detect_completion(make_campaign(), results) is True

    def test_clicked_link_is_complete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Clicked Link"), make_result("Clicked")]
        assert agent._detect_completion(make_campaign(), results) is True

    def test_email_opened_is_complete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Email Opened")]
        assert agent._detect_completion(make_campaign(), results) is True

    def test_link_clicked_is_complete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Link Clicked")]
        assert agent._detect_completion(make_campaign(), results) is True

    def test_sending_status_incomplete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Sending"), make_result("Sending")]
        assert agent._detect_completion(make_campaign(), results) is False

    def test_unknown_status_incomplete(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Error"), make_result("Email Sent")]
        assert agent._detect_completion(make_campaign(), results) is False


class TestBuildSummary:
    def test_empty_results(self):
        agent = MonitoringAgent(gophish=MagicMock())
        camp = make_campaign()
        s = agent._build_summary(camp, [])
        assert s["sent"] == 0
        assert s["opened"] == 0
        assert s["clicked"] == 0
        assert s["credentials_submitted"] == 0
        assert s["phish_prone_percentage"] == 0.0
        assert s["is_complete"] is False

    def test_sent_only(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Email Sent"), make_result("Email Sent")]
        s = agent._build_summary(make_campaign(), results)
        assert s["sent"] == 2
        assert s["opened"] == 0
        assert s["clicked"] == 0
        assert s["phish_prone_percentage"] == 0.0
        assert s["is_complete"] is True

    def test_opened_counts(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [
            make_result("Opened"),
            make_result("Email Opened"),
            make_result("Email Sent"),
        ]
        s = agent._build_summary(make_campaign(), results)
        assert s["sent"] == 3
        assert s["opened"] == 2
        assert s["clicked"] == 0

    def test_clicked_counts(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [
            make_result("Clicked"),
            make_result("Link Clicked"),
            make_result("Clicked Link"),
            make_result("Email Sent"),
        ]
        s = agent._build_summary(make_campaign(), results)
        assert s["sent"] == 4
        assert s["opened"] == 3
        assert s["clicked"] == 3

    def test_credentials_submitted(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [
            make_result("Clicked", data=[{"value": "password123"}]),
            make_result("Clicked", data=[{"value": "topsecret"}]),
            make_result("Email Sent"),
        ]
        s = agent._build_summary(make_campaign(), results)
        assert s["credentials_submitted"] == 1
        assert s["sent"] == 3

    def test_phish_prone_percentage(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Clicked"), make_result("Email Sent")]
        s = agent._build_summary(make_campaign(), results)
        assert s["phish_prone_percentage"] == 50.0

    def test_phish_prone_percentage_no_sent(self):
        agent = MonitoringAgent(gophish=MagicMock())
        s = agent._build_summary(make_campaign(), [])
        assert s["phish_prone_percentage"] == 0.0

    def test_phish_prone_percentage_all_clicked(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Clicked"), make_result("Clicked Link")]
        s = agent._build_summary(make_campaign(), results)
        assert s["phish_prone_percentage"] == 100.0

    def test_phish_prone_percentage_rounded(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [make_result("Clicked") for _ in range(1)] + [make_result("Email Sent") for _ in range(3)]
        s = agent._build_summary(make_campaign(), results)
        assert s["phish_prone_percentage"] == 25.0

    def test_credentials_with_password_variants(self):
        agent = MonitoringAgent(gophish=MagicMock())
        results = [
            make_result("Clicked", data=[{"value": "MyP@ssw0rd!"}]),
            make_result("Clicked", data=[{"value": "not a password"}]),
            make_result("Clicked", data=[{"value": "password"}]),
            make_result("Clicked", data=[{"value": ""}]),
        ]
        s = agent._build_summary(make_campaign(), results)
        assert s["credentials_submitted"] == 2

    def test_is_complete_in_summary(self):
        agent = MonitoringAgent(gophish=MagicMock())
        all_sent = [make_result("Email Sent"), make_result("Clicked")]
        s = agent._build_summary(make_campaign(), all_sent)
        assert s["is_complete"] is True

        with_sending = all_sent + [make_result("Sending")]
        s2 = agent._build_summary(make_campaign(), with_sending)
        assert s2["is_complete"] is False

    def test_campaign_id_in_summary(self):
        agent = MonitoringAgent(gophish=MagicMock())
        cid = uuid.uuid4()
        camp = make_campaign(id=cid)
        s = agent._build_summary(camp, [make_result("Email Sent")])
        assert s["campaign_id"] == str(cid)
