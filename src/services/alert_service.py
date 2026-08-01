import json
import logging

import httpx

from src.config import settings

logger = logging.getLogger(__name__)


async def send_alert(payload: dict) -> bool:
    webhook_url = settings.alert_webhook_url
    if not webhook_url:
        return False

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.post(webhook_url, json=payload)
            resp.raise_for_status()
        logger.info("Alert sent to %s (status=%d)", webhook_url[:50], resp.status_code)
        return True
    except Exception:
        logger.exception("Failed to send alert to %s", webhook_url[:50])
        return False


def build_campaign_alert(campaign_name: str, summary: dict) -> dict:
    return {
        "event": "campaign_completed",
        "severity": "high" if summary.get("clicked", 0) >= settings.alert_webhook_threshold else "info",
        "campaign": campaign_name,
        "summary": {
            "sent": summary.get("sent", 0),
            "opened": summary.get("opened", 0),
            "clicked": summary.get("clicked", 0),
            "credentials_submitted": summary.get("credentials_submitted", 0),
            "phish_prone_percentage": summary.get("phish_prone_percentage", 0),
        },
        "message": (
            f"Campaign '{campaign_name}' completed: "
            f"{summary.get('clicked', 0)}/{summary.get('sent', 0)} clicked ({summary.get('phish_prone_percentage', 0)}%). "
            f"Credentials submitted: {summary.get('credentials_submitted', 0)}."
        ),
    }
