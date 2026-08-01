"""Unit tests for risk_engine — risk scoring, classification, and analytics."""

from unittest.mock import MagicMock, AsyncMock
import uuid
import pytest

from src.engine.risk_engine import _calculate_score, _classify, _compute_trend, _predict_next_score, predict_employee_risk


def make_cr(credentials=False, clicked=False, opened=False, reported=False):
    cr = MagicMock()
    cr.credentials_submitted = credentials
    cr.link_clicked = clicked
    cr.email_opened = opened
    cr.reported_phishing = reported
    return cr


class TestClassify:
    def test_score_0_is_low(self):
        assert _classify(0) == "low"

    def test_score_14_is_low(self):
        assert _classify(14) == "low"

    def test_score_15_is_medium(self):
        assert _classify(15) == "medium"

    def test_score_39_is_medium(self):
        assert _classify(39) == "medium"

    def test_score_40_is_high(self):
        assert _classify(40) == "high"

    def test_score_69_is_high(self):
        assert _classify(69) == "high"

    def test_score_70_is_critical(self):
        assert _classify(70) == "critical"

    def test_score_100_is_critical(self):
        assert _classify(100) == "critical"


class TestCalculateScore:
    def test_empty_results_zero(self):
        score, level = _calculate_score([])
        assert score == 0.0
        assert level == "low"

    def test_credentials_submitted(self):
        score, level = _calculate_score([make_cr(credentials=True)])
        assert score == 100.0
        assert level == "critical"

    def test_link_clicked(self):
        score, level = _calculate_score([make_cr(clicked=True)])
        assert score == 60.0
        assert level == "high"

    def test_email_opened(self):
        score, level = _calculate_score([make_cr(opened=True)])
        assert score == 20.0
        assert level == "medium"

    def test_reported_phishing_reduces_score(self):
        score, level = _calculate_score([make_cr(clicked=True, reported=True)])
        assert score == 30.0
        assert level == "medium"

    def test_multiple_actions_accumulate(self):
        score, level = _calculate_score([make_cr(credentials=True, clicked=True, opened=True)])
        assert score == 100.0
        assert level == "critical"

    def test_score_capped_at_100(self):
        score, level = _calculate_score([
            make_cr(credentials=True),
            make_cr(credentials=True),
        ])
        assert score == 100.0

    def test_score_floor_at_0(self):
        score, level = _calculate_score([make_cr(reported=True)])
        assert score == 0.0
        assert level == "low"


class TestComputeTrend:
    def test_insufficient_data_returns_stable(self):
        assert _compute_trend([]) == "stable"
        assert _compute_trend([50]) == "stable"

    def test_improving_scores_return_improving(self):
        assert _compute_trend([80, 70, 60, 50]) == "improving"

    def test_worsening_scores_return_worsening(self):
        assert _compute_trend([20, 40, 60, 80]) == "worsening"

    def test_flat_scores_return_stable(self):
        assert _compute_trend([50, 51, 49, 50]) == "stable"

    def test_small_fluctuation_is_stable(self):
        assert _compute_trend([30, 32, 31, 33]) == "stable"


class TestPredictNextScore:
    def test_empty_returns_zero(self):
        assert _predict_next_score([]) == 0.0

    def test_single_value_returns_itself(self):
        assert _predict_next_score([42]) == 42.0

    def test_two_scores_weighted(self):
        result = _predict_next_score([100, 0])
        assert result == 60.0

    def test_exponential_weighting(self):
        scores = [10, 20, 30, 40]
        result = _predict_next_score(scores)
        assert result > 20


class TestPredictEmployeeRisk:
    @staticmethod
    def _make_risk_score(score: float, calculated_at):
        rs = MagicMock()
        rs.score = score
        rs.calculated_at = calculated_at
        return rs

    @staticmethod
    def _make_execute_mock(rows):
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = rows
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        return mock_result

    @pytest.mark.asyncio
    async def test_empty_scores(self):
        db = AsyncMock()
        db.execute.return_value = self._make_execute_mock([])
        result = await predict_employee_risk(db, uuid.uuid4(), limit=10)
        assert result["predicted_next_score"] is None
        assert result["trend_direction"] == "insufficient_data"
        assert result["data_points"] == 0

    @pytest.mark.asyncio
    async def test_single_score(self):
        db = AsyncMock()
        rs = self._make_risk_score(75, "2026-06-01")
        db.execute.return_value = self._make_execute_mock([rs])
        result = await predict_employee_risk(db, uuid.uuid4(), limit=10)
        assert result["predicted_next_score"] == 75.0
        assert result["trend_direction"] == "stable"
        assert result["data_points"] == 1

    @pytest.mark.asyncio
    async def test_worsening_trend(self):
        db = AsyncMock()
        scores_val = [10, 30, 50, 70]
        mock_scores = [self._make_risk_score(s, f"2026-0{i+1}-01") for i, s in enumerate(scores_val)]
        db.execute.return_value = self._make_execute_mock(mock_scores[::-1])
        result = await predict_employee_risk(db, uuid.uuid4(), limit=10)
        assert result["trend_direction"] == "worsening"
        assert result["data_points"] == 4

    @pytest.mark.asyncio
    async def test_improving_trend(self):
        db = AsyncMock()
        scores_val = [80, 65, 50, 35]
        mock_scores = [self._make_risk_score(s, f"2026-0{i+1}-01") for i, s in enumerate(scores_val)]
        db.execute.return_value = self._make_execute_mock(mock_scores[::-1])
        result = await predict_employee_risk(db, uuid.uuid4(), limit=10)
        assert result["trend_direction"] == "improving"
        assert result["data_points"] == 4

    @pytest.mark.asyncio
    async def test_confidence_bounds(self):
        db = AsyncMock()
        rs = self._make_risk_score(50, "2026-01-01")
        db.execute.return_value = self._make_execute_mock([rs])
        result = await predict_employee_risk(db, uuid.uuid4(), limit=10)
        assert 0.0 <= result["confidence"] <= 1.0

    @pytest.mark.asyncio
    async def test_prediction_within_bounds(self):
        db = AsyncMock()
        scores_val = [20, 40, 60]
        mock_scores = [self._make_risk_score(s, f"2026-0{i+1}-01") for i, s in enumerate(scores_val)]
        db.execute.return_value = self._make_execute_mock(mock_scores[::-1])
        result = await predict_employee_risk(db, uuid.uuid4(), limit=10)
        assert 0 <= result["predicted_next_score"] <= 100
