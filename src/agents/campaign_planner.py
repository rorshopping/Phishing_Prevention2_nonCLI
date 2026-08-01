import uuid
import logging
import random
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Client, Employee, EmployeeGroup, RiskScore
from src.services.llm_service import LLMService

logger = logging.getLogger(__name__)


SCENARIO_TYPES = [
    "credential_harvest",
    "malware_attachment",
    "urgency_alert",
    "ceo_fraud",
    "invoice_fraud",
    "cloud_notification",
    "calendar_invite",
    "voicemail_phish",
    "dropbox_share",
    "linkedin_message",
]

GROUP_SCENARIO_AFFINITY: dict[EmployeeGroup, list[str]] = {
    EmployeeGroup.executive: ["ceo_fraud", "urgency_alert", "cloud_notification"],
    EmployeeGroup.finance: ["invoice_fraud", "credential_harvest", "ceo_fraud"],
    EmployeeGroup.hr: ["credential_harvest", "malware_attachment", "dropbox_share"],
    EmployeeGroup.it_management: ["cloud_notification", "voicemail_phish", "credential_harvest"],
    EmployeeGroup.it_staff: ["malware_attachment", "credential_harvest", "dropbox_share"],
    EmployeeGroup.sales: ["linkedin_message", "dropbox_share", "urgency_alert"],
    EmployeeGroup.engineering: ["cloud_notification", "voicemail_phish", "malware_attachment"],
    EmployeeGroup.general: ["credential_harvest", "urgency_alert", "dropbox_share"],
}


class CampaignPlanner:
    def __init__(self, llm_service: LLMService | None = None) -> None:
        self.llm = llm_service or LLMService()

    async def plan_campaign(
        self,
        client: Client,
        employees: list[Employee],
        db: AsyncSession | None = None,
    ) -> dict[str, Any]:
        monthly_budget = max(1, round(client.campaigns_per_year / 12))

        industry_context = await self._gather_industry_context(client)

        avg_risk_score = await self._compute_average_risk(employees, db)
        adjusted_difficulty = self._adjust_difficulty(avg_risk_score)

        llm_strategy = await self._llm_campaign_strategy(client, industry_context)
        if adjusted_difficulty:
            llm_strategy["difficulty"] = adjusted_difficulty

        employee_assignments: list[dict[str, Any]] = []
        for emp in employees:
            scenario = await self.decide_scenario_for_employee(emp, llm_strategy)
            employee_assignments.append({
                "employee_id": str(emp.id),
                "group": emp.group.value,
                "scenario_type": scenario,
            })

        return {
            "client_id": str(client.id),
            "name": f"{client.company_name} - {datetime.now(timezone.utc).strftime('%Y-%m-%d')}",
            "scheduled_date": (datetime.now(timezone.utc) + timedelta(hours=1)).isoformat(),
            "difficulty": llm_strategy.get("difficulty", "medium"),
            "monthly_budget": monthly_budget,
            "industry_context": industry_context,
            "llm_strategy": llm_strategy,
            "employee_assignments": employee_assignments,
        }

    async def _compute_average_risk(
        self, employees: list[Employee], db: AsyncSession | None = None
    ) -> float | None:
        if not db or not employees:
            return None
        emp_ids = [e.id for e in employees]
        scores: list[float] = []
        for eid in emp_ids:
            q = await db.execute(
                select(RiskScore.score)
                .where(RiskScore.employee_id == eid)
                .order_by(RiskScore.calculated_at.desc())
                .limit(1)
            )
            score = q.scalar_one_or_none()
            if score is not None:
                scores.append(score)
        if not scores:
            return None
        avg = sum(scores) / len(scores)
        return round(avg, 1)

    def _adjust_difficulty(self, avg_risk_score: float | None) -> str | None:
        if avg_risk_score is None:
            return None
        if avg_risk_score >= 60:
            return "hard"
        if avg_risk_score >= 30:
            return "medium"
        return "easy"

    async def decide_scenario_for_employee(
        self, employee: Employee, llm_strategy: dict[str, Any] | None = None
    ) -> str:
        affinity = GROUP_SCENARIO_AFFINITY.get(employee.group, GROUP_SCENARIO_AFFINITY[EmployeeGroup.general])

        if llm_strategy and "scenario_weights" in llm_strategy:
            weights = llm_strategy["scenario_weights"]
            available = [s for s in SCENARIO_TYPES if weights.get(s, 0) > 0]
            if available:
                chosen = random.choices(
                    available,
                    weights=[weights[s] for s in available],
                    k=1,
                )[0]
                return chosen

        return random.choice(affinity)

    async def _gather_industry_context(self, client: Client) -> dict[str, Any]:
        return {
            "industry": client.industry or "General",
            "country": client.country,
            "employee_count": client.employee_count,
            "recent_threats": [],
        }

    async def _llm_campaign_strategy(self, client: Client, context: dict[str, Any]) -> dict[str, Any]:
        prompt = (
            f"Design a phishing simulation campaign strategy for {client.company_name}, "
            f"a {context['industry']} company in {context['country']} with {context['employee_count']} employees.\n"
            f"Recent threats in industry: {context['recent_threats']}\n\n"
            f"Return a JSON object with:\n"
            f'- "difficulty": "easy", "medium", or "hard"\n'
            f'- "scenario_weights": an object mapping scenario types to weights (0-100)\n'
            f'- "rationale": a brief explanation\n\n'
            f"Scenario types: {', '.join(SCENARIO_TYPES)}"
        )

        try:
            result = await self.llm.structured_generate(prompt)
            return result
        except Exception:
            logger.warning("LLM strategy generation failed, using defaults")
            return {"difficulty": "medium", "scenario_weights": {s: 50 for s in SCENARIO_TYPES}, "rationale": "default"}
