import uuid
import logging
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import async_session
from src.database.models import Campaign, CampaignResult, CampaignStatus, Employee
from src.services.gophish_service import GophishService as GophishService
from src.agents.base import BaseAgent
from src.utils.gdpr import hash_pii
from src.engine.risk_engine import compute_employee_risk
from src.engine.training_engine import assign_training_for_employee
from src.engine.feedback_engine import assign_training_feedback
from src.services.alert_service import send_alert, build_campaign_alert
from src.config import settings

logger = logging.getLogger(__name__)

POLL_INTERVAL_SECONDS = 300


class MonitoringAgent(BaseAgent):
    def __init__(self, gophish: GophishService | None = None) -> None:
        self.gophish = gophish or GophishService()

    async def monitor_campaign(self, campaign_id: uuid.UUID, force: bool = False) -> dict[str, Any]:
        async with async_session() as db:
            campaign = await self._load_campaign(db, campaign_id)
            if not campaign:
                return {"error": "Campaign not found", "campaign_id": str(campaign_id)}

            if campaign.status != CampaignStatus.running and not force:
                return {
                    "campaign_id": str(campaign_id),
                    "status": campaign.status.value,
                    "message": "Campaign is not currently running",
                }

            try:
                gophish_results = await self._fetch_gophish_results(campaign)
                await self._update_results(db, campaign, gophish_results)

                is_complete = self._detect_completion(campaign, gophish_results)
                summary = self._build_summary(campaign, gophish_results)

                if is_complete:
                    await self._finalize_campaign(db, campaign, summary)

                await self._log_action(
                    db,
                    campaign.client_id,
                    "campaign_monitored",
                    {"campaign_id": str(campaign_id), **summary},
                )

                await db.commit()
                return summary

            except Exception:
                await db.rollback()
                logger.exception("Monitoring failed for campaign %s", campaign_id)
                return {"error": "Monitoring failed", "campaign_id": str(campaign_id)}

    async def check_running_campaigns(self) -> list[dict[str, Any]]:
        async with async_session() as db:
            result = await db.execute(
                select(Campaign).where(Campaign.status == CampaignStatus.running)
            )
            running = list(result.scalars().all())

        results = []
        for campaign in running:
            try:
                summary = await self.monitor_campaign(campaign.id)
                results.append({"campaign_id": str(campaign.id), **summary})
            except Exception:
                logger.exception("Error monitoring campaign %s", campaign.id)
                results.append({"campaign_id": str(campaign.id), "error": "Monitor error"})

        return results

    async def _load_campaign(self, db: AsyncSession, campaign_id: uuid.UUID) -> Campaign | None:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
        return result.scalar_one_or_none()

    async def _fetch_gophish_results(self, campaign: Campaign) -> list[dict[str, Any]]:
        if not campaign.gophish_campaign_id:
            logger.warning("Campaign %s has no Gophish ID", campaign.id)
            return []

        raw_ids = campaign.gophish_campaign_id
        gophish_ids = [int(i.strip()) for i in raw_ids.split(",") if i.strip().isdigit()]
        if not gophish_ids:
            logger.warning("Campaign %s has no valid Gophish IDs", campaign.id)
            return []

        all_results: list[dict[str, Any]] = []
        for gid in gophish_ids:
            try:
                result = await self.gophish.get_campaign_results(gid)
                if isinstance(result, list):
                    all_results.extend(result)
            except Exception:
                logger.exception("Failed to fetch Gophish results for campaign %s (Gophish ID %s)", campaign.id, gid)
        return all_results

    async def _update_results(
        self, db: AsyncSession, campaign: Campaign, gophish_results: list[dict[str, Any]]
    ) -> None:
        for gres in gophish_results:
            email = gres.get("email", "")
            status = gres.get("status", "")
            ip = gres.get("ip", "")
            email_hashed = hash_pii(email)

            result_q = await db.execute(
                select(CampaignResult)
                .join(CampaignResult.employee)
                .where(
                    CampaignResult.campaign_id == campaign.id,
                    Employee.email_hash == email_hashed,
                )
            )
            cr: CampaignResult | None = result_q.scalar_one_or_none()
            if not cr:
                continue

            if status in ("Opened", "Email Opened") and not cr.email_opened:
                cr.email_opened = True
                cr.opened_at = datetime.now(timezone.utc)

            if status in ("Clicked", "Link Clicked", "Clicked Link") and not cr.link_clicked:
                cr.link_clicked = True
                cr.clicked_at = datetime.now(timezone.utc)

            if status in ("Reported", "Phishing Reported") and not cr.reported_phishing:
                cr.reported_phishing = True

            if "data" in gres and gres["data"]:
                submitted_creds = any(
                    "password" in d.get("value", "").lower()
                    for d in gres["data"]
                    if isinstance(d, dict)
                )
                if submitted_creds:
                    cr.credentials_submitted = True

            if ip:
                cr.ip_address = ip

    def _detect_completion(
        self, campaign: Campaign, gophish_results: list[dict[str, Any]]
    ) -> bool:
        if not gophish_results:
            return False

        completed_statuses = ("Email Sent", "Opened", "Email Opened", "Clicked", "Link Clicked", "Clicked Link")
        return all(r.get("status") in completed_statuses for r in gophish_results)

    def _build_summary(
        self, campaign: Campaign, gophish_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        sent = len(gophish_results)
        opened = sum(1 for r in gophish_results if r.get("status") in ("Opened", "Email Opened", "Clicked", "Link Clicked", "Clicked Link"))
        clicked = sum(1 for r in gophish_results if r.get("status") in ("Clicked", "Link Clicked", "Clicked Link"))
        reported = sum(1 for r in gophish_results if r.get("status") in ("Reported", "Phishing Reported"))
        submitted = sum(
            1 for r in gophish_results
            if "data" in r and any(
                isinstance(d, dict) and "password" in d.get("value", "").lower()
                for d in r["data"]
            )
        )

        return {
            "campaign_id": str(campaign.id),
            "sent": sent,
            "opened": opened,
            "clicked": clicked,
            "reported": reported,
            "credentials_submitted": submitted,
            "phish_prone_percentage": round((clicked / sent * 100) if sent else 0, 2),
            "is_complete": self._detect_completion(campaign, gophish_results),
        }

    async def _finalize_campaign(
        self, db: AsyncSession, campaign: Campaign, summary: dict[str, Any]
    ) -> None:
        campaign.status = CampaignStatus.completed
        campaign.completed_at = datetime.now(timezone.utc)
        campaign.sent_count = summary.get("sent", 0)
        campaign.click_count = summary.get("clicked", 0)
        campaign.fail_count = summary.get("credentials_submitted", 0)

        results_q = await db.execute(
            select(CampaignResult).where(CampaignResult.campaign_id == campaign.id)
        )
        results = list(results_q.scalars().all())

        for cr in results:
            try:
                await compute_employee_risk(
                    db=db,
                    employee_id=cr.employee_id,
                    client_id=campaign.client_id,
                    campaign_id=campaign.id,
                )
            except Exception:
                logger.exception("Risk computation failed for employee %s", cr.employee_id)

            if cr.credentials_submitted or cr.link_clicked:
                try:
                    failure = "credentials_submitted" if cr.credentials_submitted else "link_clicked"
                    await assign_training_for_employee(
                        db=db,
                        employee_id=cr.employee_id,
                        client_id=campaign.client_id,
                        campaign_id=campaign.id,
                        failure_type=failure,
                    )
                except Exception:
                    logger.exception("Training assignment failed for employee %s", cr.employee_id)

        if summary.get("clicked", 0) > 0:
            await self._send_failure_alert(db, campaign, summary)

        await self._send_webhook_alert(campaign, summary)

        if summary.get("clicked", 0) > 0 or summary.get("credentials_submitted", 0) > 0:
            await assign_training_feedback(db, campaign)

    async def _send_webhook_alert(
        self, campaign: Campaign, summary: dict[str, Any]
    ) -> None:
        if not settings.alert_webhook_url:
            return
        if settings.alert_webhook_threshold > 0 and summary.get("clicked", 0) < settings.alert_webhook_threshold:
            return
        payload = build_campaign_alert(campaign.name, summary)
        await send_alert(payload)

    async def _send_failure_alert(
        self, db: AsyncSession, campaign: Campaign, summary: dict[str, Any]
    ) -> None:
        logger.warning(
            "FAILURE ALERT [%s]: %d/%d employees clicked phishing links. "
            "Credentials submitted: %d",
            campaign.name,
            summary.get("clicked", 0),
            summary.get("sent", 0),
            summary.get("credentials_submitted", 0),
        )

        await self._log_action(
            db,
            campaign.client_id,
            "failure_alert",
            {
                "campaign_id": str(campaign.id),
                "campaign_name": campaign.name,
                "clicked": summary.get("clicked", 0),
                "credentials_submitted": summary.get("credentials_submitted", 0),
            },
        )


