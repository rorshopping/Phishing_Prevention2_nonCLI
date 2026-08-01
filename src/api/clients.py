import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.database import models as m
from src.database.models import EmployeeGroup, TrainingAssignment, VishingSession
from src.agents.execution_agent import ExecutionAgent
from src.agents.campaign_planner import CampaignPlanner
from src.utils.gdpr import hash_pii
from src.engine.risk_engine import get_client_risk_summary, get_client_risk_trend

router = APIRouter(prefix="/clients", tags=["clients"])


class ClientCreate(BaseModel):
    company_name: str = Field(..., min_length=1, max_length=255)
    contact_email: EmailStr
    contact_name: Optional[str] = None
    industry: Optional[str] = None
    employee_count: int = Field(default=0, ge=0)
    country: str = Field(default="DE", min_length=2, max_length=2)
    vishing_enabled: bool = False


class ClientUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_name: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[int] = None
    country: Optional[str] = None
    is_active: Optional[bool] = None
    vishing_enabled: Optional[bool] = None


class EmployeeCreate(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None
    email_hash: Optional[str] = None
    name_hash: Optional[str] = None
    role: Optional[str] = None
    department: Optional[str] = None
    phone_number: Optional[str] = None
    phone_number_hash: Optional[str] = None
    group: Optional[str] = None
    linkedin_url: Optional[str] = None
    public_data: Optional[dict] = None


class CampaignTrigger(BaseModel):
    difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")


class ClientResponse(BaseModel):
    id: uuid.UUID
    company_name: str
    contact_email: str
    contact_name: Optional[str]
    industry: Optional[str]
    employee_count: int
    country: str
    is_active: bool
    vishing_enabled: bool
    campaigns_per_year: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmployeeResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    email_hash: str
    name_hash: Optional[str]
    role: Optional[str]
    department: Optional[str]
    group: Optional[str]
    linkedin_url: Optional[str]
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignBrief(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    status: str
    difficulty: str
    sent_count: int
    click_count: int
    fail_count: int
    created_at: datetime
    completed_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ClientStats(BaseModel):
    client_id: uuid.UUID
    company_name: str
    total_employees: int
    total_campaigns: int
    total_emails_sent: int
    total_clicks: int
    overall_click_rate: float
    total_fails: int
    overall_fail_rate: float
    active_campaigns: int
    vishing_sessions: int


@router.post("", response_model=ClientResponse, status_code=201)
async def create_client(body: ClientCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(m.Client).where(m.Client.company_name == body.company_name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="Client with this company name already exists")
    client = m.Client(**body.model_dump())
    db.add(client)
    await db.commit()
    await db.refresh(client)
    return client


@router.get("", response_model=list[ClientResponse])
async def list_clients(
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(m.Client)
    if active_only:
        stmt = stmt.where(m.Client.is_active == True)
    stmt = stmt.order_by(m.Client.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{client_id}", response_model=ClientResponse)
async def get_client(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: uuid.UUID, body: ClientUpdate, db: AsyncSession = Depends(get_db)
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    update_data = body.model_dump(exclude_unset=True)
    if "company_name" in update_data:
        existing = await db.execute(
            select(m.Client).where(
                m.Client.company_name == update_data["company_name"],
                m.Client.id != client_id,
            )
        )
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=409, detail="Company name already taken")
    for field, value in update_data.items():
        setattr(client, field, value)
    client.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(client)
    return client


@router.delete("/{client_id}", status_code=204)
async def deactivate_client(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    client.is_active = False
    client.updated_at = datetime.now(timezone.utc)
    await db.commit()
    return None


@router.post("/{client_id}/employees", response_model=list[EmployeeResponse], status_code=201)
async def upload_employees(
    client_id: uuid.UUID,
    employees: list[EmployeeCreate],
    db: AsyncSession = Depends(get_db),
):
    if len(employees) > 10000:
        raise HTTPException(status_code=422, detail="Max 10,000 employees per upload")
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not client.is_active:
        raise HTTPException(status_code=400, detail="Client is deactivated")
    created = []
    for emp in employees:
        if not emp.email and not emp.email_hash:
            raise HTTPException(status_code=422, detail="Each employee must have email or email_hash")
        data = emp.model_dump(exclude_none=True)
        if emp.email and not emp.email_hash:
            data["email_hash"] = hash_pii(emp.email)
        if emp.name and not emp.name_hash:
            data["name_hash"] = hash_pii(emp.name)
        if emp.phone_number:
            data["phone_number_hash"] = hash_pii(emp.phone_number)
        if emp.group:
            try:
                data["group"] = EmployeeGroup(emp.group)
            except ValueError:
                raise HTTPException(status_code=422, detail=f"Invalid group '{emp.group}'. Valid: {', '.join(e.value for e in EmployeeGroup)}")
        else:
            data["group"] = EmployeeGroup.general
        employee = m.Employee(client_id=client_id, **data)
        db.add(employee)
        created.append(employee)
    existing_count = await db.execute(
        select(func.count()).select_from(m.Employee).where(m.Employee.client_id == client_id)
    )
    client.employee_count = existing_count.scalar()
    client.updated_at = datetime.now(timezone.utc)
    await db.commit()
    for emp in created:
        await db.refresh(emp)
    return created


@router.get("/{client_id}/employees", response_model=list[EmployeeResponse])
async def list_employees(
    client_id: uuid.UUID,
    active_only: bool = Query(True),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    stmt = select(m.Employee).where(m.Employee.client_id == client_id)
    if active_only:
        stmt = stmt.where(m.Employee.is_active == True)
    stmt = stmt.order_by(m.Employee.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("/{client_id}/campaigns", response_model=CampaignBrief, status_code=201)
async def trigger_campaign(
    client_id: uuid.UUID,
    body: CampaignTrigger,
    template_id: uuid.UUID = Query(None),
    email_mode: str = Query("test", pattern="^(test|prod)$"),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    if not client.is_active:
        raise HTTPException(status_code=400, detail="Client is deactivated")
    employees_q = await db.execute(
        select(m.Employee).where(
            m.Employee.client_id == client_id,
            m.Employee.is_active == True,
        )
    )
    employees = list(employees_q.scalars().all())
    if not employees:
        raise HTTPException(status_code=400, detail="No active employees for this client")

    plan_overrides = None
    if template_id:
        tpl = await db.get(m.CampaignTemplate, template_id)
        if not tpl or tpl.client_id != client_id:
            raise HTTPException(status_code=404, detail="Template not found for this client")

    planner = CampaignPlanner()
    plan = await planner.plan_campaign(client, employees, db=db)

    if template_id and tpl:
        plan["difficulty"] = tpl.difficulty
        if tpl.scenario_weights:
            plan["scenario_weights"] = tpl.scenario_weights

    if body.difficulty:
        plan["difficulty"] = body.difficulty

    plan["email_mode"] = email_mode

    campaign = m.Campaign(
        client_id=client_id,
        name=plan["name"],
        status=m.CampaignStatus.draft,
        difficulty=plan.get("difficulty", body.difficulty),
        template_id=str(template_id) if template_id else None,
    )
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)

    executor = ExecutionAgent()
    success = await executor.execute_campaign(campaign.id, plan)

    await db.refresh(campaign)
    return campaign


@router.get("/{client_id}/campaigns", response_model=list[CampaignBrief])
async def list_campaigns(
    client_id: uuid.UUID,
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    stmt = select(m.Campaign).where(m.Campaign.client_id == client_id)
    if status:
        stmt = stmt.where(m.Campaign.status == status)
    stmt = stmt.order_by(m.Campaign.created_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{client_id}/stats", response_model=ClientStats)
async def get_client_stats(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    emp_count = await db.execute(
        select(func.count()).select_from(m.Employee).where(
            m.Employee.client_id == client_id,
            m.Employee.is_active == True,
        )
    )
    campaign_count = await db.execute(
        select(func.count()).select_from(m.Campaign).where(m.Campaign.client_id == client_id)
    )
    active_count = await db.execute(
        select(func.count()).select_from(m.Campaign).where(
            m.Campaign.client_id == client_id,
            m.Campaign.status == m.CampaignStatus.running,
        )
    )
    totals = await db.execute(
        select(
            func.coalesce(func.sum(m.Campaign.sent_count), 0),
            func.coalesce(func.sum(m.Campaign.click_count), 0),
            func.coalesce(func.sum(m.Campaign.fail_count), 0),
        ).where(m.Campaign.client_id == client_id)
    )
    total_sent, total_clicks, total_fails = totals.one()
    vishing_count = await db.execute(
        select(func.count()).select_from(m.VishingSession).where(
            m.VishingSession.client_id == client_id
        )
    )
    click_rate = round((total_clicks / total_sent * 100), 2) if total_sent > 0 else 0.0
    fail_rate = round((total_fails / total_sent * 100), 2) if total_sent > 0 else 0.0
    return ClientStats(
        client_id=client_id,
        company_name=client.company_name,
        total_employees=emp_count.scalar(),
        total_campaigns=campaign_count.scalar(),
        total_emails_sent=total_sent,
        total_clicks=total_clicks,
        overall_click_rate=click_rate,
        total_fails=total_fails,
        overall_fail_rate=fail_rate,
        active_campaigns=active_count.scalar(),
        vishing_sessions=vishing_count.scalar(),
    )


@router.get("/{client_id}/dashboard")
async def get_client_dashboard(client_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    emp_q = await db.execute(
        select(func.count()).select_from(m.Employee).where(
            m.Employee.client_id == client_id, m.Employee.is_active == True,
        )
    )
    total_employees = emp_q.scalar() or 0

    stats_q = await db.execute(
        select(
            func.count(m.Campaign.id),
            func.coalesce(func.sum(m.Campaign.sent_count), 0),
            func.coalesce(func.sum(m.Campaign.click_count), 0),
            func.coalesce(func.sum(m.Campaign.fail_count), 0),
        ).where(m.Campaign.client_id == client_id)
    )
    total_campaigns, total_sent, total_clicks, total_fails = stats_q.one()

    click_rate = round((total_clicks / total_sent * 100), 2) if total_sent else 0.0
    fail_rate = round((total_fails / total_sent * 100), 2) if total_sent else 0.0

    active_q = await db.execute(
        select(func.count()).select_from(m.Campaign).where(
            m.Campaign.client_id == client_id,
            m.Campaign.status == m.CampaignStatus.running,
        )
    )
    active_campaigns = active_q.scalar() or 0

    pending_q = await db.execute(
        select(func.count()).select_from(TrainingAssignment).where(
            TrainingAssignment.client_id == client_id,
            TrainingAssignment.status == "pending",
        )
    )
    pending_training = pending_q.scalar() or 0

    vishing_q = await db.execute(
        select(func.count()).select_from(VishingSession).where(
            VishingSession.client_id == client_id,
        )
    )
    vishing_total = vishing_q.scalar() or 0

    risk_summary = await get_client_risk_summary(db, client_id)
    risk_trend = await get_client_risk_trend(db, client_id, months=12)

    recent_q = await db.execute(
        select(m.Campaign).where(
            m.Campaign.client_id == client_id,
        ).order_by(m.Campaign.created_at.desc()).limit(5)
    )
    recent_campaigns = [
        {
            "id": str(c.id),
            "name": c.name[:40],
            "status": c.status.value,
            "difficulty": c.difficulty,
            "sent_count": c.sent_count,
            "click_count": c.click_count,
            "click_rate": round((c.click_count / c.sent_count * 100), 1) if c.sent_count else 0.0,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        }
        for c in recent_q.scalars().all()
    ]

    return {
        "client_id": str(client_id),
        "company_name": client.company_name,
        "summary": {
            "total_employees": total_employees,
            "total_campaigns": total_campaigns,
            "total_emails_sent": total_sent,
            "total_clicks": total_clicks,
            "total_fails": total_fails,
            "click_rate": click_rate,
            "fail_rate": fail_rate,
            "active_campaigns": active_campaigns,
            "pending_training": pending_training,
            "vishing_sessions": vishing_total,
        },
        "risk": risk_summary,
        "risk_trend": risk_trend,
        "recent_campaigns": recent_campaigns,
    }
