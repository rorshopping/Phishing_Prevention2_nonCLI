import pytest
from unittest.mock import AsyncMock, patch

from src.engine.email_builder import (
    ScenarioType, generate_email, _fallback_email,
    _clean_subject, PLANNER_TO_EMAIL_SCENARIO,
)


MOCK_LLM_RESPONSE = '''{
    "subject": "Dringend: Zahlung freigeben",
    "body_html": "<p>Hallo {{.FirstName}}, bitte <a href='{{.URL}}'>hier klicken</a>.</p>"
}'''


class TestScenarioMapping:
    def test_all_planner_scenarios_map_to_valid_scenario_types(self):
        for planner_key, scenario in PLANNER_TO_EMAIL_SCENARIO.items():
            assert isinstance(scenario, ScenarioType), f"{planner_key} -> {scenario}"

    def test_scenario_types_have_fallback(self):
        for scenario in ScenarioType:
            result = _fallback_email(scenario, {"name": "Test"}, {"name": "Company"})
            assert "subject" in result
            assert "body_html" in result
            assert len(result["subject"]) > 0
            assert "{{.URL}}" in result["body_html"]


class TestCleanSubject:
    def test_removes_unicode_dashes(self):
        assert _clean_subject("Test \u2013 Dash") == "Test - Dash"

    def test_removes_unicode_quotes(self):
        assert _clean_subject("\u2018Hello\u2019") == "'Hello'"

    def test_removes_ellipsis(self):
        assert _clean_subject("More\u2026") == "More..."

    def test_passes_through_ascii(self):
        assert _clean_subject("Normal Subject") == "Normal Subject"


class TestFallbackEmail:
    def test_fallback_returns_valid_structure(self):
        result = _fallback_email(
            ScenarioType.bank_transfer,
            {"name": "Anna"},
            {"name": "TestCorp"},
        )
        assert "subject" in result
        assert "body_html" in result
        assert "{{.FirstName}}" in result["body_html"]
        assert "{{.URL}}" in result["body_html"]

    def test_fallback_includes_company_name(self):
        result = _fallback_email(
            ScenarioType.security_alert,
            {"name": "Bob"},
            {"name": "SecureCorp"},
        )
        assert "SecureCorp" in result["body_html"]

    def test_fallback_html_is_well_formed(self):
        result = _fallback_email(
            ScenarioType.invoice,
            {"name": "Claire"},
            {"name": "BizCo"},
        )
        html = result["body_html"]
        assert html.startswith("<!DOCTYPE html>")
        assert "</html>" in html


class TestGenerateEmail:
    @pytest.mark.asyncio
    async def test_generate_email_llm_success(self):
        with patch("src.engine.email_builder._try_provider", new=AsyncMock(return_value=MOCK_LLM_RESPONSE)):
            result = await generate_email(
                ScenarioType.bank_transfer,
                {"name": "Richard", "role": "Developer"},
                {"name": "Acme Corp", "industry": "Tech"},
            )
            assert result["subject"] == "Dringend: Zahlung freigeben"
            assert "{{.URL}}" in result["body_html"]
            assert "{{.FirstName}}" in result["body_html"]

    @pytest.mark.asyncio
    async def test_generate_email_fallback_on_llm_failure(self):
        with patch("src.engine.email_builder._try_provider", new=AsyncMock(return_value="")):
            result = await generate_email(
                ScenarioType.password_reset,
                {"name": "Alice"},
                {"name": "Company"},
            )
            assert "subject" in result
            assert "{{.URL}}" in result["body_html"]

    @pytest.mark.asyncio
    async def test_generate_email_invalid_json_falls_back(self):
        with patch("src.engine.email_builder._try_provider", new=AsyncMock(return_value="not valid json")):
            result = await generate_email(
                ScenarioType.shared_doc,
                {"name": "Bob"},
                {"name": "Company"},
            )
            assert "subject" in result
            assert "{{.URL}}" in result["body_html"]

    @pytest.mark.asyncio
    async def test_generate_email_strips_code_fences(self):
        fenced = f"```json\n{MOCK_LLM_RESPONSE}\n```"
        with patch("src.engine.email_builder._try_provider", new=AsyncMock(return_value=fenced)):
            result = await generate_email(
                ScenarioType.voicemail,
                {"name": "Claire"},
                {"name": "Company"},
            )
            assert result["subject"] == "Dringend: Zahlung freigeben"
