import logging
from typing import Any

from src.engine.gophish import GophishClient

logger = logging.getLogger(__name__)


class GophishService:
    def __init__(self) -> None:
        self.client = GophishClient()

    async def create_group(self, group: dict[str, Any]) -> dict[str, Any]:
        return await self.client.create_group(group["name"], group.get("targets", []))

    async def create_template(self, template: dict[str, Any]) -> dict[str, Any]:
        return await self.client.create_template(
            name=template["name"],
            subject=template["subject"],
            html=template["html"],
            text=template.get("text", ""),
            envelope_sender=template.get("envelope_sender", ""),
        )

    async def create_page(self, page: dict[str, Any]) -> dict[str, Any]:
        return await self.client.create_page(
            name=page["name"],
            html=page["html"],
            capture_credentials=page.get("capture_credentials", True),
            capture_passwords=page.get("capture_passwords", True),
        )

    async def create_smtp_profile(self, smtp: dict[str, Any]) -> dict[str, Any]:
        return await self.client.create_smtp_profile(smtp["name"], smtp)

    async def launch_campaign(self, campaign: dict[str, Any]) -> dict[str, Any]:
        return await self.client.create_campaign(campaign)

    async def get_campaign_results(self, campaign_id: int) -> list[dict[str, Any]]:
        return await self.client.get_campaign_results(campaign_id)

    async def complete_campaign(self, campaign_id: int) -> dict[str, Any]:
        return await self.client.complete_campaign(campaign_id)
