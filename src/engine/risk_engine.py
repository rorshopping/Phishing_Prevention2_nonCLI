import uuid
import math
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, func, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Employee, EmployeeGroup, Campaign, CampaignResult, CampaignStatus, RiskScore, Client, AuditLog,
)

logger = logging.getLogger(__name__)

RISK_WEIGHTS = {
    "credentials_submitted": 100,
    "link_clicked": 60,
    "email_opened": 20,
    "reported_phishing": -30,
}

RISK_LEVELS = [
    (0, 15, "low"),
    (15, 40, "medium"),
    (40, 70, "high"),
    (70, 101, "critical"),
]


def _calculate_score(campaign_results: list[CampaignResult]) -> tuple[float, str]:
    total = 0.0
    for cr in campaign_results:
        if cr.credentials_submitted:
            total += RISK_WEIGHTS["credentials_submitted"]
        if cr.link_clicked:
            total += RISK_WEIGHTS["link_clicked"]
        if cr.email_opened:
            total += RISK_WEIGHTS["email_opened"]
        if cr.reported_phishing:
            total += RISK_WEIGHTS["reported_phishing"]
    score = max(0.0, min(100.0, total))
    for lo, hi, level in RISK_LEVELS:
        if lo <= score < hi:
            return round(score, 1), level
    return round(score, 1), "critical"


def _classify(score: float) -> str:
    if score >= 70:
        return "critical"
    if score >= 40:
        return "high"
    if score >= 15:
        return "medium"
    return "low"


def _compute_trend(scores: list[float]) -> str:
    if len(scores) < 2:
        return "stable"
    n = len(scores)
    xs = list(range(n))
    x_mean = sum(xs) / n
    y_mean = sum(scores) / n
    num = sum((xs[i] - x_mean) * (scores[i] - y_mean) for i in range(n))
    den = sum((xs[i] - x_mean) ** 2 for i in range(n))
    slope = num / den if den else 0.0
    if slope > 1.5:
        return "worsening"
    if slope < -1.5:
        return "improving"
    return "stable"


def _predict_next_score(scores: list[float]) -> float:
    if not scores:
        return 0.0
    if len(scores) == 1:
        return scores[0]
    n = len(scores)
    alpha = 0.4
    ema = scores[0]
    for i in range(1, n):
        ema = alpha * scores[i] + (1 - alpha) * ema
    return round(ema, 1)


async def predict_employee_risk(
    db: AsyncSession,
    employee_id: uuid.UUID,
    limit: int = 10,
) -> dict[str, Any]:
    scores_q = await db.execute(
        select(RiskScore)
        .where(RiskScore.employee_id == employee_id)
        .order_by(RiskScore.calculated_at.desc())
        .limit(limit)
    )
    scores = list(reversed(scores_q.scalars().all()))
    values = [s.score for s in scores]

    if not values:
        return {
            "employee_id": str(employee_id),
            "predicted_next_score": None,
            "trend_direction": "insufficient_data",
            "confidence": 0.0,
            "data_points": 0,
        }

    predicted = _predict_next_score(values)
    direction = _compute_trend(values)
    variance = sum((v - predicted) ** 2 for v in values) / max(len(values), 1)
    confidence = round(max(0.0, min(1.0, 1.0 - (variance / 2500))), 2)

    return {
        "employee_id": str(employee_id),
        "predicted_next_score": predicted,
        "risk_level": _classify(predicted),
        "trend_direction": direction,
        "confidence": confidence,
        "data_points": len(values),
        "current_score": values[-1] if values else None,
        "current_risk_level": _classify(values[-1]) if values else None,
    }


async def compute_employee_risk(
    db: AsyncSession,
    employee_id: uuid.UUID,
    client_id: uuid.UUID,
    campaign_id: uuid.UUID | None = None,
) -> dict[str, Any]:
    results_q = await db.execute(
        select(CampaignResult).where(
            CampaignResult.employee_id == employee_id,
        )
    )
    all_results = list(results_q.scalars().all())

    recent = [r for r in all_results if r.campaign_id == campaign_id] if campaign_id else all_results

    score, level = _calculate_score(recent)

    risk_entry = RiskScore(
        employee_id=employee_id,
        client_id=client_id,
        campaign_id=campaign_id,
        score=score,
        risk_level=level,
        email_opened=any(r.email_opened for r in recent),
        link_clicked=any(r.link_clicked for r in recent),
        credentials_submitted=any(r.credentials_submitted for r in recent),
        reported_phishing=any(r.reported_phishing for r in recent),
    )
    db.add(risk_entry)
    await db.flush()

    return {
        "risk_score_id": str(risk_entry.id),
        "employee_id": str(employee_id),
        "score": score,
        "risk_level": level,
        "total_campaigns_attended": len(all_results),
    }


async def get_employee_risk_trend(
    db: AsyncSession,
    employee_id: uuid.UUID,
    limit: int = 12,
) -> dict[str, Any]:
    scores_q = await db.execute(
        select(RiskScore)
        .where(RiskScore.employee_id == employee_id)
        .order_by(RiskScore.calculated_at.desc())
        .limit(limit)
    )
    scores = list(reversed(scores_q.scalars().all()))
    values = [s.score for s in scores]
    return {
        "employee_id": str(employee_id),
        "trend_direction": _compute_trend(values) if len(values) >= 2 else "stable",
        "history": [
            {
                "score": s.score,
                "risk_level": s.risk_level,
                "campaign_id": str(s.campaign_id) if s.campaign_id else None,
                "calculated_at": s.calculated_at.isoformat(),
            }
            for s in scores
        ],
    }


async def get_client_risk_summary(
    db: AsyncSession,
    client_id: uuid.UUID,
) -> dict[str, Any]:
    emp_q = await db.execute(
        select(Employee).where(
            Employee.client_id == client_id,
            Employee.is_active == True,
        )
    )
    employees = list(emp_q.scalars().all())

    latest_scores = []
    for emp in employees:
        score_q = await db.execute(
            select(RiskScore)
            .where(RiskScore.employee_id == emp.id)
            .order_by(RiskScore.calculated_at.desc())
            .limit(1)
        )
        latest = score_q.scalar_one_or_none()
        if latest:
            latest_scores.append(latest)

    if not latest_scores:
        return {
            "client_id": str(client_id),
            "average_risk_score": 0.0,
            "risk_distribution": {"low": 0, "medium": 0, "high": 0, "critical": 0},
            "total_employees_scored": 0,
        }

    avg = sum(s.score for s in latest_scores) / len(latest_scores)
    dist: dict[str, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    for s in latest_scores:
        dist[s.risk_level] = dist.get(s.risk_level, 0) + 1

    top5_sorted = sorted(latest_scores, key=lambda x: x.score, reverse=True)[:5]
    top5_with_trend = []
    for s in top5_sorted:
        prev_q = await db.execute(
            select(RiskScore)
            .where(RiskScore.employee_id == s.employee_id)
            .order_by(RiskScore.calculated_at.desc())
            .offset(1)
            .limit(1)
        )
        prev = prev_q.scalar_one_or_none()
        trend = "stable"
        if prev:
            diff = s.score - prev.score
            if diff > 5:
                trend = "worsening"
            elif diff < -5:
                trend = "improving"
        top5_with_trend.append({
            "employee_id": str(s.employee_id),
            "score": s.score,
            "risk_level": s.risk_level,
            "trend_direction": trend,
        })

    return {
        "client_id": str(client_id),
        "average_risk_score": round(avg, 1),
        "risk_distribution": dist,
        "total_employees_scored": len(latest_scores),
        "total_employees": len(employees),
        "highest_risk_employees": top5_with_trend,
    }


async def get_client_risk_trend(
    db: AsyncSession,
    client_id: uuid.UUID,
    months: int = 12,
) -> list[dict[str, Any]]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=months * 31)
    q = await db.execute(
        select(
            extract("year", RiskScore.calculated_at).label("year"),
            extract("month", RiskScore.calculated_at).label("month"),
            func.avg(RiskScore.score).label("avg_score"),
            func.count(RiskScore.id).label("score_count"),
        )
        .where(
            RiskScore.client_id == client_id,
            RiskScore.calculated_at >= cutoff,
        )
        .group_by("year", "month")
        .order_by("year", "month")
    )
    rows = q.all()
    return [
        {
            "period": f"{int(r.year)}-{int(r.month):02d}",
            "year": int(r.year),
            "month": int(r.month),
            "average_score": round(float(r.avg_score), 1) if r.avg_score else 0.0,
            "score_count": int(r.score_count),
        }
        for r in rows
    ]


async def get_client_dashboard(
    db: AsyncSession,
    client_id: uuid.UUID,
) -> dict[str, Any]:
    summary = await get_client_risk_summary(db, client_id)
    trend = await get_client_risk_trend(db, client_id, months=12)

    total_employees = summary.get("total_employees", 0)
    scored = summary.get("total_employees_scored", 0)

    return {
        "client_id": str(client_id),
        "summary": summary,
        "risk_trend": trend,
        "coverage": {
            "total_employees": total_employees,
            "employees_scored": scored,
            "coverage_percent": round(scored / max(total_employees, 1) * 100, 1),
        },
    }


async def get_client_department_benchmarking(
    db: AsyncSession,
    client_id: uuid.UUID,
) -> list[dict[str, Any]]:
    employees_q = await db.execute(
        select(Employee).where(
            Employee.client_id == client_id,
            Employee.is_active == True,
        )
    )
    employees = list(employees_q.scalars().all())

    dept_map: dict[str, dict[str, Any]] = {}
    for emp in employees:
        dept = emp.group.value if emp.group else "general"
        if dept not in dept_map:
            dept_map[dept] = {"employee_count": 0, "employee_ids": [], "total_clicks": 0, "total_sent": 0, "total_fails": 0}
        dept_map[dept]["employee_count"] += 1
        dept_map[dept]["employee_ids"].append(emp.id)

    for dept, info in dept_map.items():
        results_q = await db.execute(
            select(CampaignResult).where(
                CampaignResult.employee_id.in_(info["employee_ids"]),
            )
        )
        results = list(results_q.scalars().all())
        info["total_sent"] = len(results)
        info["total_clicks"] = sum(1 for r in results if r.link_clicked)
        info["total_fails"] = sum(1 for r in results if r.credentials_submitted)
        info["click_rate"] = round((info["total_clicks"] / info["total_sent"] * 100), 1) if info["total_sent"] else 0.0
        info["fail_rate"] = round((info["total_fails"] / info["total_sent"] * 100), 1) if info["total_sent"] else 0.0
        del info["employee_ids"]

        latest_scores = []
        for eid in [e.id for e in employees if (e.group.value if e.group else "general") == dept]:
            score_q = await db.execute(
                select(RiskScore).where(RiskScore.employee_id == eid).order_by(RiskScore.calculated_at.desc()).limit(1)
            )
            s = score_q.scalar_one_or_none()
            if s:
                latest_scores.append(s.score)
        info["avg_risk_score"] = round(sum(latest_scores) / len(latest_scores), 1) if latest_scores else 0.0

    sorted_depts = sorted(dept_map.items(), key=lambda x: x[1]["click_rate"], reverse=True)
    result = []
    for dept, info in sorted_depts:
        result.append({
            "department": dept,
            "employee_count": info["employee_count"],
            "total_sent": info["total_sent"],
            "click_rate": info["click_rate"],
            "fail_rate": info["fail_rate"],
            "avg_risk_score": info["avg_risk_score"],
        })
    return result


async def get_client_click_heatmap(
    db: AsyncSession,
    client_id: uuid.UUID,
) -> dict[str, Any]:
    campaigns_q = await db.execute(
        select(Campaign.id).where(Campaign.client_id == client_id)
    )
    campaign_ids = [row[0] for row in campaigns_q.all()]

    if not campaign_ids:
        return {"days": {}, "hours": {}}

    results_q = await db.execute(
        select(CampaignResult).where(
            CampaignResult.campaign_id.in_(campaign_ids),
            CampaignResult.link_clicked == True,
        )
    )
    results = list(results_q.scalars().all())

    day_dist: dict[str, int] = {}
    hour_dist: dict[int, int] = {}
    for r in results:
        if r.clicked_at:
            day_name = r.clicked_at.strftime("%A")
            day_dist[day_name] = day_dist.get(day_name, 0) + 1
            hour_dist[r.clicked_at.hour] = hour_dist.get(r.clicked_at.hour, 0) + 1

    days_ordered = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    hours_ordered = list(range(24))

    return {
        "total_clicks": len(results),
        "by_day_of_week": {d: day_dist.get(d, 0) for d in days_ordered},
        "by_hour": {str(h): hour_dist.get(h, 0) for h in hours_ordered},
        "peak_day": max(day_dist, key=day_dist.get) if day_dist else None,
        "peak_hour": max(hour_dist, key=hour_dist.get) if hour_dist else None,
    }
