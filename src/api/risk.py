import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.database import models as m
from src.engine.risk_engine import (
    compute_employee_risk,
    get_employee_risk_trend,
    get_client_risk_summary,
    get_client_risk_trend,
    get_client_dashboard,
    get_client_department_benchmarking,
    get_client_click_heatmap,
)

router = APIRouter(prefix="/risk", tags=["risk"])


class RiskScoreResponse(BaseModel):
    risk_score_id: str
    employee_id: str
    score: float
    risk_level: str
    total_campaigns_attended: int

    model_config = {"from_attributes": True}


class RiskTrendItem(BaseModel):
    score: float
    risk_level: str
    campaign_id: Optional[str]
    calculated_at: str


class ClientRiskSummary(BaseModel):
    client_id: str
    average_risk_score: float
    risk_distribution: dict[str, int]
    total_employees_scored: int
    total_employees: int
    highest_risk_employees: list[dict]


@router.get("/employee/{employee_id}", response_model=RiskScoreResponse)
async def get_employee_risk(employee_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    emp = await db.get(m.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    result = await compute_employee_risk(db, employee_id, emp.client_id)
    await db.commit()
    return result


@router.get("/employee/{employee_id}/trend")
async def employee_risk_trend(
    employee_id: uuid.UUID,
    limit: int = Query(12, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(m.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return await get_employee_risk_trend(db, employee_id, limit=limit)


@router.get("/employee/{employee_id}/predict")
async def employee_risk_predict(
    employee_id: uuid.UUID,
    limit: int = Query(10, ge=2, le=50),
    db: AsyncSession = Depends(get_db),
):
    emp = await db.get(m.Employee, employee_id)
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    return await predict_employee_risk(db, employee_id, limit=limit)


@router.get("/client/{client_id}", response_model=ClientRiskSummary)
async def client_risk_summary(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await get_client_risk_summary(db, client_id)


@router.get("/client/{client_id}/trend")
async def client_risk_trend(
    client_id: uuid.UUID,
    months: int = Query(12, ge=1, le=60),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await get_client_risk_trend(db, client_id, months=months)


@router.get("/client/{client_id}/dashboard")
async def client_dashboard(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await get_client_dashboard(db, client_id)


@router.get("/client/{client_id}/departments")
async def client_department_benchmarking(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await get_client_department_benchmarking(db, client_id)


@router.get("/client/{client_id}/heatmap")
async def client_click_heatmap(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return await get_client_click_heatmap(db, client_id)
