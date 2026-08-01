import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.database import models as m
from src.engine.training_engine import (
    assign_training_for_employee,
    assign_bulk_training_for_campaign,
    complete_training,
    get_pending_training,
    get_training_content,
    get_client_training_roi,
)
from src.engine.feedback_engine import get_employee_feedback

router = APIRouter(prefix="/training", tags=["training"])


class TrainingAssignResponse(BaseModel):
    assignment_id: str
    employee_id: str
    training_type: str
    status: str
    score_before: float


class TrainingCompleteRequest(BaseModel):
    score_after: Optional[float] = None


class TrainingItem(BaseModel):
    id: str
    employee_id: str
    client_id: str
    campaign_id: Optional[str]
    training_type: str
    training_title: str
    status: str
    assigned_at: str
    score_before: float

    model_config = {"from_attributes": True}


class TrainingContentResponse(BaseModel):
    training_type: str
    title: str
    html: str


@router.post("/assign", response_model=TrainingAssignResponse)
async def assign_training(
    employee_id: uuid.UUID,
    campaign_id: uuid.UUID,
    failure_type: str = Query("link_clicked"),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(m.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    result = await assign_training_for_employee(
        db=db,
        employee_id=employee_id,
        client_id=emp.client_id,
        campaign_id=campaign_id,
        failure_type=failure_type,
    )
    await db.commit()
    return result


@router.post("/campaign/{campaign_id}/assign-all")
async def assign_bulk_training(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    results = await assign_bulk_training_for_campaign(db, campaign_id)
    await db.commit()
    return {"assignments": results, "total": len(results)}


@router.post("/{assignment_id}/complete")
async def mark_training_complete(
    assignment_id: uuid.UUID,
    body: TrainingCompleteRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await complete_training(db, assignment_id, score_after=body.score_after)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    await db.commit()
    return result


@router.get("/pending")
async def list_pending_training(
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await get_pending_training(db, client_id=client_id)


@router.get("/content/{training_type}", response_model=TrainingContentResponse)
async def training_content(training_type: str):
    return get_training_content(training_type)


@router.get("/client/{client_id}/roi")
async def client_training_roi(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await get_client_training_roi(db, client_id)


@router.get("/feedback/{employee_id}")
async def employee_feedback(
    employee_id: uuid.UUID,
    campaign_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(m.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return await get_employee_feedback(db, employee_id, campaign_id=campaign_id)
