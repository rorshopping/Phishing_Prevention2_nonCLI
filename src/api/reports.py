import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import HTMLResponse, PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.database import models as m
from src.engine.report_engine import generate_client_report, generate_campaign_report, generate_campaign_report_csv, generate_client_report_csv

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/client/{client_id}", response_class=HTMLResponse)
async def client_report(
    client_id: uuid.UUID,
    days: int = Query(365, ge=1, le=730),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    date_to = datetime.now(timezone.utc)
    date_from = date_to - timedelta(days=days)
    html = await generate_client_report(db, client_id, date_from=date_from, date_to=date_to)
    return HTMLResponse(content=html)


@router.get("/campaign/{campaign_id}", response_class=HTMLResponse)
async def campaign_report(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    html = await generate_campaign_report(db, campaign_id)
    return HTMLResponse(content=html)


@router.get("/client/{client_id}/json")
async def client_report_json(
    client_id: uuid.UUID,
    days: int = Query(365, ge=1, le=730),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    from src.engine.report_engine import generate_client_report_json
    date_to = datetime.now(timezone.utc)
    date_from = date_to - timedelta(days=days)
    return await generate_client_report_json(db, client_id, date_from=date_from, date_to=date_to)


@router.get("/campaign/{campaign_id}/csv", response_class=PlainTextResponse)
async def campaign_report_csv(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    results_q = await db.execute(
        select(m.CampaignResult).where(m.CampaignResult.campaign_id == campaign_id)
    )
    results = list(results_q.scalars().all())
    emp_q = await db.execute(
        select(m.Employee).where(m.Employee.client_id == campaign.client_id)
    )
    employee_map = {str(e.id): (e.name_hash[:12] if e.name_hash else str(e.id)[:8]) for e in emp_q.scalars().all()}
    csv_data = generate_campaign_report_csv(results, employee_map)
    return PlainTextResponse(content=csv_data, media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=campaign_{campaign_id}.csv"})


@router.get("/client/{client_id}/csv", response_class=PlainTextResponse)
async def client_report_csv(
    client_id: uuid.UUID,
    days: int = Query(365, ge=1, le=730),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    date_to = datetime.now(timezone.utc)
    date_from = date_to - timedelta(days=days)
    campaigns_q = await db.execute(
        select(m.Campaign).where(
            m.Campaign.client_id == client_id,
            m.Campaign.created_at >= date_from,
            m.Campaign.created_at <= date_to,
        ).order_by(m.Campaign.created_at.desc())
    )
    campaigns = list(campaigns_q.scalars().all())
    csv_data = generate_client_report_csv(campaigns)
    return PlainTextResponse(content=csv_data, media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename=client_{client_id}_report.csv"})
