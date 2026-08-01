import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import async_session
from src.database.models import Client, Campaign, CampaignStatus
from src.agents.base import BaseAgent
from src.agents.campaign_planner import CampaignPlanner
from src.agents.execution_agent import ExecutionAgent
from src.agents.monitoring_agent import MonitoringAgent
from src.agents.vishing_agent import VishingAgent


logger = logging.getLogger(__name__)


class Orchestrator(BaseAgent):
    def __init__(
        self,
        planner: CampaignPlanner | None = None,
        executor: ExecutionAgent | None = None,
        monitor: MonitoringAgent | None = None,
        vishing: VishingAgent | None = None,
    ) -> None:
        self.planner = planner or CampaignPlanner()
        self.executor = executor or ExecutionAgent()
        self.monitor = monitor or MonitoringAgent()
        self.vishing = vishing or VishingAgent()

    async def run_scheduled_campaigns(self) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        async with async_session() as db:
            active_clients = await self._get_active_clients(db)

            for client in active_clients:
                try:
                    if await self._client_needs_campaign(db, client):
                        logger.info("Scheduling campaign for client %s", client.company_name)
                        result = await self.run_client_campaign(client.id)
                        results.append(result)
                    else:
                        logger.debug(
                            "Client %s does not need a campaign yet", client.company_name
                        )
                except Exception:
                    logger.exception(
                        "Failed to process client %s", client.company_name
                    )
                    results.append({
                        "client_id": str(client.id),
                        "error": f"Campaign processing failed",
                    })

        return results

    async def run_client_campaign(self, client_id: uuid.UUID) -> dict[str, Any]:
        async with async_session() as db:
            client = await self._get_client(db, client_id)
            if not client:
                return {"error": "Client not found", "client_id": str(client_id)}

            if not client.is_active:
                return {"error": "Client is not active", "client_id": str(client_id)}

            employees = await self._get_client_employees(db, client_id)
            if not employees:
                return {"error": "No active employees", "client_id": str(client_id)}

            try:
                plan = await self.planner.plan_campaign(client, employees, db=db)

                campaign = Campaign(
                    client_id=client.id,
                    name=plan["name"],
                    status=CampaignStatus.scheduled,
                    difficulty=plan.get("difficulty", "medium"),
                    scheduled_date=datetime.fromisoformat(plan["scheduled_date"]),
                )
                db.add(campaign)
                await db.flush()

                await self._log_action(
                    db,
                    client.id,
                    "campaign_planned",
                    {
                        "campaign_id": str(campaign.id),
                        "employee_count": len(employees),
                        "difficulty": plan.get("difficulty"),
                    },
                )
                await db.commit()

                execution_ok = await self.executor.execute_campaign(campaign.id, plan)
                if not execution_ok:
                    return {
                        "client_id": str(client_id),
                        "campaign_id": str(campaign.id),
                        "status": "execution_failed",
                    }

                if client.vishing_enabled:
                    await self._schedule_vishing_calls(db, campaign, employees, plan)

                await self._log_action(
                    db,
                    client.id,
                    "campaign_completed",
                    {"campaign_id": str(campaign.id)},
                )
                await db.commit()

                return {
                    "client_id": str(client_id),
                    "campaign_id": str(campaign.id),
                    "status": "completed",
                    "employee_count": len(employees),
                    "vishing_included": client.vishing_enabled,
                }

            except Exception:
                await db.rollback()
                logger.exception("Campaign failed for client %s", client_id)
                return {
                    "client_id": str(client_id),
                    "error": "Campaign execution failed",
                }

    async def monitor_all_active_campaigns(self) -> list[dict[str, Any]]:
        return await self.monitor.check_running_campaigns()

    async def _get_active_clients(self, db: AsyncSession) -> list[Client]:
        result = await db.execute(
            select(Client).where(Client.is_active == True)
        )
        return list(result.scalars().all())

    async def _get_client(self, db: AsyncSession, client_id: uuid.UUID) -> Client | None:
        result = await db.execute(select(Client).where(Client.id == client_id))
        return result.scalar_one_or_none()

    async def _get_client_employees(self, db: AsyncSession, client_id: uuid.UUID) -> list[Any]:
        from src.database.models import Employee

        result = await db.execute(
            select(Employee).where(
                Employee.client_id == client_id,
                Employee.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def _client_needs_campaign(self, db: AsyncSession, client: Client) -> bool:
        now = datetime.now(timezone.utc)
        year_start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

        count_result = await db.execute(
            select(func.count(Campaign.id)).where(
                Campaign.client_id == client.id,
                Campaign.created_at >= year_start,
            )
        )
        campaigns_this_year: int = count_result.scalar() or 0

        if campaigns_this_year >= client.campaigns_per_year:
            return False

        target_per_month = max(1, round(client.campaigns_per_year / 12))
        months_elapsed = max(1, (now.year - year_start.year) * 12 + now.month - 1)
        expected_by_now = target_per_month * months_elapsed

        if campaigns_this_year >= expected_by_now:
            return False

        last_campaign_result = await db.execute(
            select(Campaign.created_at)
            .where(
                Campaign.client_id == client.id,
                Campaign.status == CampaignStatus.completed,
            )
            .order_by(Campaign.created_at.desc())
            .limit(1)
        )
        last_campaign_date = last_campaign_result.scalar_one_or_none()

        if last_campaign_date:
            days_since_last = (now - last_campaign_date).days
            min_interval = max(14, 365 // client.campaigns_per_year)
            if days_since_last < min_interval:
                return False

        return True

    async def _schedule_vishing_calls(
        self,
        db: AsyncSession,
        campaign: Campaign,
        employees: list[Any],
        plan: dict[str, Any],
    ) -> None:
        assignments = {
            a["employee_id"]: a["scenario_type"]
            for a in plan.get("employee_assignments", [])
        }

        for emp in employees:
            scenario = assignments.get(str(emp.id), "tech_support")
            try:
                result = await self.vishing.trigger_vishing_call(
                    employee_id=emp.id,
                    campaign_id=campaign.id,
                    scenario=scenario,
                )
                if "error" in result:
                    logger.warning(
                        "Vishing trigger failed for employee %s: %s",
                        emp.id,
                        result["error"],
                    )
            except Exception:
                logger.exception("Vishing trigger error for employee %s", emp.id)


