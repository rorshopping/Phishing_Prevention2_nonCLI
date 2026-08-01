import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.database import models as m

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


class CampaignDetail(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    status: str
    difficulty: str
    template_id: Optional[str]
    scheduled_date: Optional[datetime]
    sent_count: int
    click_count: int
    fail_count: int
    gophish_campaign_id: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class CampaignScheduleRequest(BaseModel):
    scheduled_date: datetime


class CampaignResultItem(BaseModel):
    id: uuid.UUID
    employee_id: uuid.UUID
    email_hash: Optional[str] = None
    email_opened: bool
    link_clicked: bool
    credentials_submitted: bool
    reported_phishing: bool
    opened_at: Optional[datetime]
    clicked_at: Optional[datetime]
    training_completed: bool
    ip_address: Optional[str]
    user_agent: Optional[str]

    model_config = {"from_attributes": True}


class CampaignResultResponse(BaseModel):
    campaign: CampaignDetail
    results: list[CampaignResultItem]


@router.get("/{campaign_id}", response_model=CampaignDetail)
async def get_campaign(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return campaign


@router.get("/{campaign_id}/results", response_model=CampaignResultResponse)
async def get_campaign_results(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    result = await db.execute(
        select(m.CampaignResult).where(m.CampaignResult.campaign_id == campaign_id)
    )
    results = result.scalars().all()
    enriched = []
    for r in results:
        emp = await db.get(m.Employee, r.employee_id)
        enriched.append(CampaignResultItem(
            id=r.id,
            employee_id=r.employee_id,
            email_hash=emp.email_hash if emp else None,
            email_opened=r.email_opened,
            link_clicked=r.link_clicked,
            credentials_submitted=r.credentials_submitted,
            reported_phishing=r.reported_phishing,
            opened_at=r.opened_at,
            clicked_at=r.clicked_at,
            training_completed=r.training_completed,
            ip_address=r.ip_address,
            user_agent=r.user_agent,
        ))
    return CampaignResultResponse(
        campaign=CampaignDetail.model_validate(campaign),
        results=enriched,
    )


@router.post("/{campaign_id}/cancel", response_model=CampaignDetail)
async def cancel_campaign(campaign_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status in (m.CampaignStatus.completed, m.CampaignStatus.cancelled):
        raise HTTPException(status_code=400, detail="Campaign is already finished")
    campaign.status = m.CampaignStatus.cancelled
    campaign.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.post("/{campaign_id}/schedule", response_model=CampaignDetail)
async def schedule_campaign(
    campaign_id: uuid.UUID,
    body: CampaignScheduleRequest,
    db: AsyncSession = Depends(get_db),
):
    campaign = await db.get(m.Campaign, campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if campaign.status != m.CampaignStatus.draft:
        raise HTTPException(status_code=400, detail="Only draft campaigns can be scheduled")
    campaign.scheduled_date = body.scheduled_date
    campaign.status = m.CampaignStatus.scheduled
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/scheduled", response_model=list[CampaignDetail])
async def list_scheduled_campaigns(
    client_id: uuid.UUID = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(m.Campaign).where(m.Campaign.status == m.CampaignStatus.scheduled)
    if client_id:
        stmt = stmt.where(m.Campaign.client_id == client_id)
    stmt = stmt.order_by(m.Campaign.scheduled_date.asc())
    result = await db.execute(stmt)
    return result.scalars().all()
