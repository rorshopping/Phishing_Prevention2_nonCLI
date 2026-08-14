import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, WebSocket
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db, async_session
from src.database import models as m
from src.agents.vishing_agent import VishingAgent
from src.services.live_voice import LiveVishingCaller

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/vishing", tags=["vishing"])


class VishingTrigger(BaseModel):
    employee_id: uuid.UUID
    campaign_id: Optional[uuid.UUID] = None
    scenario: str = "tech_support"


@router.post("/trigger", status_code=201)
async def trigger_vishing(body: VishingTrigger, db: AsyncSession = Depends(get_db)):
    employee = await db.get(m.Employee, body.employee_id)
    if not employee:
        raise HTTPException(status_code=404, detail="Employee not found")

    agent = VishingAgent()
    result = await agent.trigger_vishing_call(
        employee_id=body.employee_id,
        campaign_id=body.campaign_id,
        scenario=body.scenario,
    )
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    return result


@router.websocket("/ws/vishing/{session_id}")
async def vishing_stream(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        await websocket.close(code=1008)
        return

    async with async_session() as db:
        session = await db.get(m.VishingSession, session_uuid)
    if not session:
        await websocket.close(code=1008)
        return

    caller = LiveVishingCaller(str(session_uuid))
    await caller.run(websocket)
