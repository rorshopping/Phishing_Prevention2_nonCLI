import uuid
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.database import models as m
from src.agents.vishing_agent import VishingAgent

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
