import hashlib
import hmac
import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.session import get_db
from src.database import models as m
from src.agents.vishing_agent import VishingAgent, VISHING_DISCLOSE_KEY

logger = logging.getLogger("phishguard.webhooks")

router = APIRouter(prefix="/webhooks", tags=["webhooks"])

GOPHISH_WEBHOOK_SECRET = settings.app_secret_key


class GophishEvent(BaseModel):
    campaign_id: int
    email: str
    event: str
    time: str
    details: dict[str, Any] | None = None


@router.post("/gophish")
async def receive_gophish_event(
    payload: GophishEvent,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    cid_str = str(payload.campaign_id)
    campaign = await db.execute(
        select(m.Campaign).where(
            m.Campaign.gophish_campaign_id.isnot(None),
            or_(
                m.Campaign.gophish_campaign_id == cid_str,
                m.Campaign.gophish_campaign_id.like(f"{cid_str},%"),
                m.Campaign.gophish_campaign_id.like(f"%,{cid_str}"),
                m.Campaign.gophish_campaign_id.like(f"%,{cid_str},%"),
            ),
        )
    )
    campaign = campaign.scalar_one_or_none()
    if not campaign:
        logger.warning("Gophish event for unknown campaign_id=%s", payload.campaign_id)
        return {"status": "ignored", "reason": "unknown campaign"}

    action = payload.event.lower()
    if action == "email sent":
        campaign.sent_count += 1
    elif action in ("clicked link", "link clicked"):
        campaign.click_count += 1
    elif action in ("submitted data", "data submitted"):
        result = await db.execute(
            select(m.CampaignResult).where(
                m.CampaignResult.campaign_id == campaign.id,
                m.CampaignResult.employee_id.isnot(None),
            )
        )
        r = result.scalars().first()
        if r:
            r.credentials_submitted = True
    elif action == "reported":
        result = await db.execute(
            select(m.CampaignResult).where(
                m.CampaignResult.campaign_id == campaign.id,
            )
        )
        r = result.scalars().first()
        if r:
            r.reported_phishing = True

    await db.commit()
    logger.info("Processed Gophish event: %s for campaign %s", payload.event, payload.campaign_id)
    return {"status": "processed"}


@router.post("/twilio")
async def receive_twilio_status(
    CallSid: str = Form(...),
    CallStatus: str = Form(...),
    Called: str = Form(""),
    Caller: str = Form(""),
    Duration: str = Form(""),
    RecordingUrl: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    session = await db.execute(
        select(m.VishingSession).where(m.VishingSession.twilio_sid == CallSid)
    )
    session = session.scalar_one_or_none()
    if not session:
        logger.warning("Twilio event for unknown CallSid=%s", CallSid)
        return {"status": "ignored"}

    status = CallStatus.lower()
    status_map = {
        "completed": "completed",
        "failed": "failed",
        "no-answer": "no_answer",
        "busy": "busy",
        "canceled": "cancelled",
        "in-progress": "in_progress",
        "ringing": "ringing",
    }
    session.status = status_map.get(status, status)

    if Duration:
        session.call_duration = int(Duration)
    if RecordingUrl:
        session.call_recording_url = RecordingUrl

    await db.commit()
    logger.info("Processed Twilio status: %s for session %s", CallStatus, CallSid)
    return {"status": "processed"}


@router.post("/vishing/gather")
async def receive_vishing_gather(
    CallSid: str = Form(...),
    Digits: str = Form(""),
    db: AsyncSession = Depends(get_db),
):
    session = await db.execute(
        select(m.VishingSession).where(m.VishingSession.twilio_sid == CallSid)
    )
    session = session.scalar_one_or_none()
    if not session:
        logger.warning("Vishing gather event for unknown CallSid=%s", CallSid)
        return PlainTextResponse("<Response></Response>", media_type="text/xml")

    disclosed = Digits.strip() == VISHING_DISCLOSE_KEY
    await VishingAgent().record_outcome(session.id, disclosed)

    thanks = (
        "Danke." if disclosed else "Vielen Dank für Ihre Mithilfe."
    )
    return PlainTextResponse(
        f"<Response><Say voice='Polly.Hans' language='de-DE'>{thanks}</Say></Response>",
        media_type="text/xml",
    )


@router.get("/vishing/twiml")
@router.post("/vishing/twiml")
async def serve_vishing_twiml(
    session_id: str = "",
    db: AsyncSession = Depends(get_db),
):
    try:
        session_uuid = uuid.UUID(session_id)
    except (ValueError, AttributeError):
        return PlainTextResponse("<Response></Response>", media_type="text/xml")

    session = await db.get(m.VishingSession, session_uuid)
    if not session or not session.twiml:
        return PlainTextResponse("<Response></Response>", media_type="text/xml")

    return PlainTextResponse(session.twiml, media_type="text/xml")
