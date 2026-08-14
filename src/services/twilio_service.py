import asyncio
import logging
from typing import Any

from twilio.rest import Client as TwilioRestClient
from twilio.base.exceptions import TwilioRestException

from src.config import settings

logger = logging.getLogger(__name__)


class TwilioService:
    def __init__(self) -> None:
        self.client: TwilioRestClient | None = None
        if settings.twilio_account_sid and settings.twilio_auth_token:
            self.client = TwilioRestClient(settings.twilio_account_sid, settings.twilio_auth_token)

    async def make_call(
        self,
        to: str,
        twiml: str | None = None,
        url: str | None = None,
        recording_enabled: bool = False,
    ) -> dict[str, Any]:
        if not self.client:
            logger.warning("Twilio not configured; returning mock call result")
            return {"sid": "mock-sid", "status": "queued"}

        try:
            kwargs: dict[str, Any] = {
                "to": to,
                "from_": settings.twilio_phone_number,
            }
            if recording_enabled:
                kwargs["record"] = True
            if url:
                kwargs["url"] = url
            else:
                kwargs["twiml"] = twiml or "<Response/>"
            call = await asyncio.to_thread(self.client.calls.create, **kwargs)
            return {"sid": call.sid, "status": call.status}
        except TwilioRestException as e:
            logger.error("Twilio call failed: %s", e)
            raise

    async def hang_up(self, call_sid: str) -> None:
        if not self.client:
            return
        try:
            await asyncio.to_thread(
                lambda: self.client.calls(call_sid).update(status="completed")
            )
        except TwilioRestException as e:
            logger.error("Twilio hangup failed: %s", e)
            raise

    async def get_call_status(self, call_sid: str) -> dict[str, Any]:
        if not self.client:
            return {"sid": call_sid, "status": "unknown"}

        try:
            call = await asyncio.to_thread(self.client.calls(call_sid).fetch)
            return {"sid": call.sid, "status": call.status, "duration": call.duration}
        except TwilioRestException as e:
            logger.error("Twilio status fetch failed: %s", e)
            raise
