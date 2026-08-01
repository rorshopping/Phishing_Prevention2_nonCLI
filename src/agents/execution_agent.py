import uuid
import logging
import random
import string
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import async_session
from src.database.models import Campaign, CampaignResult, CampaignStatus, Client, Employee
from src.services.gophish_service import GophishService
from src.engine.email_builder import generate_email, ScenarioType, PLANNER_TO_EMAIL_SCENARIO
from src.engine.personalizer import build_target_context
from src.agents.base import BaseAgent
from src.config import settings

logger = logging.getLogger(__name__)


def _unique_suffix() -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=6))


class ExecutionAgent(BaseAgent):
    def __init__(
        self,
        gophish: GophishService | None = None,
    ) -> None:
        self.gophish = gophish or GophishService()

    async def execute_campaign(self, campaign_id: uuid.UUID, plan: dict[str, Any] | None = None) -> bool:
        async with async_session() as db:
            campaign = await self._load_campaign(db, campaign_id)
            if not campaign:
                return False

            try:
                await self._update_status(db, campaign, CampaignStatus.running)

                employees = await self._get_campaign_employees(db, campaign)
                if not employees:
                    logger.warning("No active employees for campaign %s", campaign_id)
                    await self._update_status(db, campaign, CampaignStatus.completed)
                    return True

                pages = await self._ensure_landing_pages(db, campaign)
                smtp_name = await self._ensure_smtp_profile()

                employee_assignments = self._get_employee_assignments(plan, employees)

                scenario_groups = self._group_employees_by_scenario(employee_assignments, employees)

                all_gophish_ids: list[int] = []
                all_group_ids: list[int] = []
                all_template_ids: list[int] = []

                for scenario_type, group_employees in scenario_groups.items():
                    employee_contexts = [
                        build_target_context({
                            "name": emp.name or emp.name_hash or "Employee",
                            "role": emp.role or "employee",
                            "department": emp.department or "",
                            "group": emp.group.value if emp.group else "general",
                            "linkedin_url": emp.linkedin_url or "",
                            "public_data": emp.public_data or {},
                        })
                        for emp in group_employees
                    ]

                    template = await self._generate_single_template(
                        db, campaign, scenario_type, employee_contexts
                    )
                    gophish_group = await self._create_group_for_targets(
                        db, campaign, group_employees, scenario_type.value
                    )
                    gophish_campaign = await self._launch_gophish_campaign(
                        db, campaign, gophish_group, template, pages, smtp_name
                    )

                    gid = gophish_campaign.get("id")
                    if gid is not None:
                        all_gophish_ids.append(gid)
                    grp_id = gophish_group.get("id")
                    if grp_id is not None:
                        all_group_ids.append(grp_id)
                    tpl_id = template.get("id")
                    if tpl_id is not None:
                        all_template_ids.append(tpl_id)

                campaign.gophish_campaign_id = ",".join(str(i) for i in all_gophish_ids) if all_gophish_ids else None
                campaign.gophish_group_id = ",".join(str(i) for i in all_group_ids) if all_group_ids else None
                campaign.gophish_template_id = ",".join(str(i) for i in all_template_ids) if all_template_ids else None

                await self._create_result_records(db, campaign, employees)

                await self._log_action(
                    db,
                    campaign.client_id,
                    "campaign_executed",
                    {
                        "campaign_id": str(campaign_id),
                        "gophish_ids": all_gophish_ids,
                        "scenario_count": len(scenario_groups),
                        "employee_count": len(employees),
                    },
                )

                await db.commit()
                return True

            except Exception:
                await db.rollback()
                await self._update_status(db, campaign, CampaignStatus.draft)
                logger.exception("Campaign execution failed for %s", campaign_id)
                return False

    def _get_employee_assignments(
        self, plan: dict[str, Any] | None, employees: list[Employee]
    ) -> dict[uuid.UUID, ScenarioType]:
        if not plan:
            return {emp.id: ScenarioType.bank_transfer for emp in employees}

        assignments: dict[str, str] = {}
        for ea in plan.get("employee_assignments", []):
            assignments[ea["employee_id"]] = ea["scenario_type"]

        result: dict[uuid.UUID, ScenarioType] = {}
        for emp in employees:
            planner_scenario = assignments.get(str(emp.id))
            if planner_scenario and planner_scenario in PLANNER_TO_EMAIL_SCENARIO:
                result[emp.id] = PLANNER_TO_EMAIL_SCENARIO[planner_scenario]
            else:
                result[emp.id] = ScenarioType.bank_transfer
        return result

    def _group_employees_by_scenario(
        self, assignments: dict[uuid.UUID, ScenarioType], employees: list[Employee]
    ) -> dict[ScenarioType, list[Employee]]:
        emp_map = {emp.id: emp for emp in employees}
        groups: dict[ScenarioType, list[Employee]] = defaultdict(list)
        for emp_id, scenario in assignments.items():
            emp = emp_map.get(emp_id)
            if emp:
                groups[scenario].append(emp)
        return dict(groups)

    def _sanitize_for_llm(self, ctx: dict[str, Any]) -> dict[str, Any]:
        raw_name = ctx.get("name", "Employee")
        first_name = raw_name.split()[0] if raw_name else "Employee"
        return {
            "name": first_name,
            "role": ctx.get("role", "employee"),
            "department": ctx.get("department", ""),
            "group": ctx.get("group", "general"),
        }

    async def _generate_single_template(
        self,
        db: AsyncSession,
        campaign: Campaign,
        scenario_type: ScenarioType,
        employee_contexts: list[dict[str, Any]],
    ) -> dict[str, Any]:
        raw_ctx = employee_contexts[0] if employee_contexts else build_target_context({})
        representative_ctx = self._sanitize_for_llm(raw_ctx)
        client_result = await db.execute(select(Client).where(Client.id == campaign.client_id))
        client = client_result.scalar_one_or_none()
        company_name = client.company_name if client else "Company"
        email_body = await generate_email(
            scenario_type=scenario_type,
            employee_context=representative_ctx,
            company_context={"name": company_name},
        )
        import re
        body_html = email_body.get("body_html", "<p>Please review this document.</p>")
        body_only = re.sub(r'^.*?<body[^>]*>(.*?)</body>.*?$', r'\1', body_html, flags=re.DOTALL)
        if body_only == body_html:
            body_only = re.sub(r'^.*?<html>.*?<body[^>]*>(.*?)</body>.*?</html>.*?$', r'\1', body_html, flags=re.DOTALL)
        if body_only == body_html:
            body_only = body_html
        template = {
            "name": f"PH TPL {campaign.name[:15]}-{scenario_type.value}-{_unique_suffix()}",
            "envelope_sender": settings.gmail_from or settings.email_source,
            "subject": email_body.get("subject", "Important notification"),
            "html": body_only,
        }
        created = await self.gophish.create_template(template)
        return created

    async def _create_group_for_targets(
        self,
        db: AsyncSession,
        campaign: Campaign,
        employees: list[Employee],
        scenario_label: str,
    ) -> dict[str, Any]:
        targets = []
        for emp in employees:
            emp_name = emp.name or emp.name_hash or ""
            targets.append({
                "email": emp.email or emp.email_hash,
                "first_name": emp_name.split()[0] if emp_name else "",
                "last_name": " ".join(emp_name.split()[1:]) if emp_name and len(emp_name.split()) > 1 else "",
                "position": emp.role or "Employee",
            })
        group = {
            "name": f"PH Group {campaign.name[:25]}-{scenario_label}-{_unique_suffix()}",
            "targets": targets,
        }
        created = await self.gophish.create_group(group)
        return created

    async def _load_campaign(self, db: AsyncSession, campaign_id: uuid.UUID) -> Campaign | None:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        return result.scalar_one_or_none()

    async def _update_status(self, db: AsyncSession, campaign: Campaign, status: CampaignStatus) -> None:
        campaign.status = status
        if status == CampaignStatus.completed:
            campaign.completed_at = datetime.now(timezone.utc)
        await db.flush()

    async def _get_campaign_employees(self, db: AsyncSession, campaign: Campaign) -> list[Employee]:
        result = await db.execute(
            select(Employee).where(
                Employee.client_id == campaign.client_id,
                Employee.is_active == True,
            )
        )
        return list(result.scalars().all())

    async def _ensure_landing_pages(self, db: AsyncSession, campaign: Campaign) -> list[dict[str, Any]]:
        suffix = _unique_suffix()
        page = {
            "name": f"PH Page {campaign.name[:30]} {suffix}",
            "html": "<html><body><h2>Bitte anmelden um fortzufahren</h2>"
                    "<form><input name='email' placeholder='E-Mail'/>"
                    "<input name='password' type='password' placeholder='Passwort'/>"
                    "<button type='submit'>Anmelden</button></form></body></html>",
            "capture_credentials": True,
            "capture_passwords": True,
            "redirect_url": "https://www.example.com",
        }
        created = await self.gophish.create_page(page)
        page_id = created.get("id")
        if page_id:
            campaign.gophish_page_id = page_id
        return [created]

    async def _ensure_smtp_profile(self) -> str:
        name = "PhishGuard SMTP"
        smtp_config = {
            "name": name,
            "interface_type": "SMTP",
            "from_address": settings.gmail_from or settings.email_source,
            "host": "smtp.gmail.com",
            "username": settings.gmail_user,
            "password": settings.gmail_app_password,
            "port": 587,
            "ignore_cert_errors": False,
        }
        try:
            await self.gophish.create_smtp_profile(smtp_config)
            logger.info("Created SMTP profile '%s' in Gophish", name)
        except Exception:
            logger.info("SMTP profile '%s' already exists in Gophish", name)
        return name

    async def _launch_gophish_campaign(
        self,
        db: AsyncSession,
        campaign: Campaign,
        group: dict[str, Any],
        template: dict[str, Any],
        pages: list[dict[str, Any]],
        smtp_name: str,
    ) -> dict[str, Any]:
        gophish_campaign = {
            "name": f"PhishGuard {campaign.name[:25]}-{_unique_suffix()}",
            "groups": [{"name": group.get("name")}] if group.get("name") else [],
            "page": {"name": pages[0].get("name")} if pages else None,
            "template": {"name": template.get("name")} if template else None,
            "smtp": {"name": smtp_name},
            "url": settings.gophish_phishing_server_url,
        }
        if campaign.scheduled_date:
            gophish_campaign["launch_date"] = campaign.scheduled_date.strftime("%Y-%m-%dT%H:%M:%SZ")
        logger.info("Launching Gophish campaign with payload: %s", gophish_campaign)
        result = await self.gophish.launch_campaign(gophish_campaign)
        return result

    async def _create_result_records(
        self, db: AsyncSession, campaign: Campaign, employees: list[Employee]
    ) -> None:
        existing = await db.execute(
            select(CampaignResult).where(CampaignResult.campaign_id == campaign.id)
        )
        if existing.scalars().first():
            return

        for emp in employees:
            context = build_target_context({
                "name": emp.name_hash or "Employee",
                "role": emp.role or "employee",
                "department": emp.department or "",
                "group": emp.group.value if emp.group else "general",
                "linkedin_url": emp.linkedin_url or "",
                "public_data": emp.public_data or {},
            })
            result = CampaignResult(
                campaign_id=campaign.id,
                employee_id=emp.id,
                personalization_context=context,
            )
            db.add(result)


