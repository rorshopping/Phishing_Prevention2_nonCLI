import uuid
import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel, Field
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database.session import get_db
from src.database import models as m

logger = logging.getLogger(__name__)

# The FastAPI app sets this to the background scheduler task on startup so the
# console can report whether the autonomous loop is actually alive.
scheduler_task: Any | None = None


def require_ops_auth(request: Request) -> None:
    token = settings.ops_token
    if not token:
        return
    auth = request.headers.get("Authorization", "")
    if auth != f"Bearer {token}":
        raise HTTPException(status_code=401, detail="Invalid or missing ops token")


# Public (unauthenticated) routes — only expose what the console needs to know
# before it can authenticate.
public_router = APIRouter(prefix="/ops", tags=["ops"])

# Everything else requires the ops token (when configured).
router = APIRouter(
    prefix="/ops",
    tags=["ops"],
    dependencies=[Depends(require_ops_auth)],
)


@public_router.get("/config")
async def ops_config() -> dict[str, Any]:
    return {
        "auth_required": bool(settings.ops_token),
        "version": "1.0.0",
    }


async def _health_check() -> dict[str, Any]:
    db_ok = False
    gophish_ok = False
    try:
        from sqlalchemy import text
        from src.database.session import engine

        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            db_ok = True
    except Exception:
        pass
    if settings.gophish_api_key:
        try:
            import httpx

            async with httpx.AsyncClient(verify=False) as hc:
                resp = await hc.get(
                    f"{settings.gophish_api_url}/campaigns/",
                    headers={"Authorization": f"Bearer {settings.gophish_api_key}"},
                    timeout=5,
                )
                gophish_ok = resp.status_code < 500
        except Exception:
            pass
    return {
        "db": "connected" if db_ok else "error",
        "gophish": "reachable" if gophish_ok else "unreachable",
    }


async def _global_risk(db: AsyncSession) -> tuple[float, dict[str, int]]:
    dist: dict[str, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    rows = (
        await db.execute(
            select(
                m.RiskScore.employee_id,
                m.RiskScore.score,
                m.RiskScore.risk_level,
            )
            .order_by(m.RiskScore.employee_id, m.RiskScore.calculated_at.desc())
        )
    ).all()
    latest: dict[uuid.UUID, tuple[float, str]] = {}
    for emp_id, score, level in rows:
        if emp_id not in latest:
            latest[emp_id] = (float(score), level)
    scores = [v[0] for v in latest.values()]
    for _, level in latest.values():
        dist[level] = dist.get(level, 0) + 1
    avg = round(sum(scores) / len(scores), 1) if scores else 0.0
    return avg, dist


async def _recent_activity(db: AsyncSession, limit: int = 50) -> list[dict[str, Any]]:
    q = await db.execute(
        select(m.AuditLog, m.Client.company_name)
        .outerjoin(m.Client, m.Client.id == m.AuditLog.client_id)
        .order_by(m.AuditLog.created_at.desc())
        .limit(limit)
    )
    return [
        {
            "id": str(log.id),
            "action": log.action,
            "client_id": str(log.client_id) if log.client_id else None,
            "client_name": name,
            "details": log.details,
            "created_at": log.created_at.isoformat() if log.created_at else None,
        }
        for log, name in q.all()
    ]


def _campaign_dict(camp: m.Campaign, client_name: str | None) -> dict[str, Any]:
    return {
        "id": str(camp.id),
        "client_id": str(camp.client_id),
        "client_name": client_name,
        "name": camp.name,
        "status": camp.status.value if hasattr(camp.status, "value") else str(camp.status),
        "difficulty": camp.difficulty,
        "template_id": camp.template_id,
        "scheduled_date": camp.scheduled_date.isoformat() if camp.scheduled_date else None,
        "sent_count": camp.sent_count,
        "click_count": camp.click_count,
        "fail_count": camp.fail_count,
        "gophish_campaign_id": camp.gophish_campaign_id,
        "created_at": camp.created_at.isoformat() if camp.created_at else None,
        "completed_at": camp.completed_at.isoformat() if camp.completed_at else None,
    }


@router.get("/status")
async def ops_status(db: AsyncSession = Depends(get_db)):
    health = await _health_check()

    client_counts = await db.execute(
        select(
            func.count(m.Client.id),
            func.count(m.Client.id).filter(m.Client.is_active == True),
        )
    )
    total_clients, active_clients = client_counts.one()

    emp_counts = await db.execute(
        select(
            func.count(m.Employee.id),
            func.count(m.Employee.id).filter(m.Employee.is_active == True),
        )
    )
    total_employees, active_employees = emp_counts.one()

    campaign_rows = await db.execute(
        select(m.Campaign.status, func.count(m.Campaign.id)).group_by(m.Campaign.status)
    )
    campaign_by_status: dict[str, int] = {}
    for st, cnt in campaign_rows.all():
        key = st.value if hasattr(st, "value") else str(st)
        campaign_by_status[key] = int(cnt)
    for s in ("draft", "scheduled", "running", "completed", "cancelled"):
        campaign_by_status.setdefault(s, 0)

    totals_q = await db.execute(
        select(
            func.coalesce(func.sum(m.Campaign.sent_count), 0),
            func.coalesce(func.sum(m.Campaign.click_count), 0),
            func.coalesce(func.sum(m.Campaign.fail_count), 0),
        )
    )
    total_sent, total_clicks, total_fails = totals_q.one()

    pending_training = await db.execute(
        select(func.count()).select_from(m.TrainingAssignment).where(
            m.TrainingAssignment.status == "pending"
        )
    )
    vishing_count = await db.execute(
        select(func.count()).select_from(m.VishingSession)
    )

    running_q = await db.execute(
        select(m.Campaign, m.Client.company_name)
        .join(m.Client, m.Client.id == m.Campaign.client_id)
        .where(m.Campaign.status == m.CampaignStatus.running)
        .order_by(m.Campaign.created_at.desc())
    )
    running: list[dict[str, Any]] = []
    for camp, client_name in running_q.all():
        results_q = await db.execute(
            select(
                func.count(m.CampaignResult.id),
                func.count(m.CampaignResult.id).filter(m.CampaignResult.email_opened == True),
                func.count(m.CampaignResult.id).filter(m.CampaignResult.link_clicked == True),
                func.count(m.CampaignResult.id).filter(m.CampaignResult.credentials_submitted == True),
                func.count(m.CampaignResult.id).filter(m.CampaignResult.reported_phishing == True),
            ).where(m.CampaignResult.campaign_id == camp.id)
        )
        total, opened, clicked, submitted, reported = results_q.one()
        running.append({
            "id": str(camp.id),
            "name": camp.name,
            "client_id": str(camp.client_id),
            "client_name": client_name,
            "difficulty": camp.difficulty,
            "created_at": camp.created_at.isoformat() if camp.created_at else None,
            "scheduled_date": camp.scheduled_date.isoformat() if camp.scheduled_date else None,
            "gophish_campaign_id": camp.gophish_campaign_id,
            "totals": {
                "sent": int(total),
                "opened": int(opened),
                "clicked": int(clicked),
                "credentials_submitted": int(submitted),
                "reported": int(reported),
            },
        })

    risk_avg, risk_dist = await _global_risk(db)

    return {
        "health": health,
        "scheduler": {
            "configured": bool(settings.gophish_api_key),
            "running": scheduler_task is not None and not scheduler_task.done(),
            "interval_seconds": settings.scheduler_interval_seconds,
        },
        "counts": {
            "clients_total": int(total_clients),
            "clients_active": int(active_clients),
            "employees_total": int(total_employees),
            "employees_active": int(active_employees),
            "campaigns": campaign_by_status,
            "emails_sent": int(total_sent),
            "clicks": int(total_clicks),
            "fails": int(total_fails),
            "pending_training": int(pending_training.scalar() or 0),
            "vishing_sessions": int(vishing_count.scalar() or 0),
        },
        "risk": {"average_score": risk_avg, "distribution": risk_dist},
        "running_campaigns": running,
        "recent_activity": await _recent_activity(db, limit=15),
    }


@router.get("/activity")
async def ops_activity(
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    return await _recent_activity(db, limit=limit)


@router.get("/campaigns")
async def ops_campaigns(
    status: Optional[str] = Query(None),
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(m.Campaign, m.Client.company_name)
        .join(m.Client, m.Client.id == m.Campaign.client_id)
        .order_by(m.Campaign.created_at.desc())
    )
    if status:
        stmt = stmt.where(m.Campaign.status == status)
    if client_id:
        stmt = stmt.where(m.Campaign.client_id == client_id)
    rows = (await db.execute(stmt)).all()
    return [_campaign_dict(c, name) for c, name in rows]


@router.get("/vishing")
async def ops_vishing(
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(m.VishingSession, m.Employee.name_hash, m.Client.company_name)
        .join(m.Employee, m.Employee.id == m.VishingSession.employee_id)
        .join(m.Client, m.Client.id == m.VishingSession.client_id)
        .order_by(m.VishingSession.created_at.desc())
    )
    if status:
        stmt = stmt.where(m.VishingSession.status == status)
    rows = (await db.execute(stmt)).all()
    return [
        {
            "id": str(s.id),
            "client_id": str(s.client_id),
            "client_name": client_name,
            "employee_id": str(s.employee_id),
            "employee": (name_hash[:14] if name_hash else str(s.employee_id)[:8]),
            "campaign_id": str(s.campaign_id) if s.campaign_id else None,
            "status": s.status,
            "call_duration": s.call_duration,
            "sensitive_info_disclosed": s.sensitive_info_disclosed,
            "ai_used": s.ai_used,
            "phone_number_hash": s.phone_number_hash,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "transcript_preview": (s.transcript or "")[:200],
        }
        for s, name_hash, client_name in rows
    ]


@router.get("/training")
async def ops_training(
    status: Optional[str] = Query(None),
    client_id: Optional[uuid.UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = (
        select(m.TrainingAssignment, m.Employee.name_hash, m.Client.company_name)
        .join(m.Employee, m.Employee.id == m.TrainingAssignment.employee_id)
        .join(m.Client, m.Client.id == m.TrainingAssignment.client_id)
        .order_by(m.TrainingAssignment.assigned_at.desc())
    )
    if status:
        stmt = stmt.where(m.TrainingAssignment.status == status)
    if client_id:
        stmt = stmt.where(m.TrainingAssignment.client_id == client_id)
    rows = (await db.execute(stmt)).all()
    return [
        {
            "id": str(a.id),
            "employee_id": str(a.employee_id),
            "employee": (name_hash[:14] if name_hash else str(a.employee_id)[:8]),
            "client_id": str(a.client_id),
            "client_name": client_name,
            "campaign_id": str(a.campaign_id) if a.campaign_id else None,
            "training_type": a.training_type,
            "status": a.status,
            "score_before": a.score_before,
            "score_after": a.score_after,
            "assigned_at": a.assigned_at.isoformat() if a.assigned_at else None,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        }
        for a, name_hash, client_name in rows
    ]


@router.post("/monitor")
async def ops_monitor():
    from src.agents.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    results = await orchestrator.monitor_all_active_campaigns()
    return {"monitored": len(results), "results": results}


@router.post("/campaigns/{campaign_id}/monitor")
async def ops_monitor_campaign(campaign_id: uuid.UUID):
    from src.agents.monitoring_agent import MonitoringAgent

    agent = MonitoringAgent()
    result = await agent.monitor_campaign(campaign_id, force=True)
    return result


@router.post("/run-scheduler")
async def ops_run_scheduler():
    from src.agents.orchestrator import Orchestrator

    health = await _health_check()
    if health.get("gophish") != "reachable":
        raise HTTPException(
            status_code=503,
            detail="Gophish is unreachable — scheduler pass skipped so no zombie campaigns are created. Start Gophish and try again.",
        )

    orchestrator = Orchestrator()
    results = await orchestrator.run_scheduled_campaigns()
    return {"campaigns": len(results), "results": results}


class TriggerCampaignRequest(BaseModel):
    difficulty: str = Field(default="medium", pattern=r"^(easy|medium|hard)$")
    email_mode: str = Field(default="test", pattern=r"^(test|prod)$")
    vishing_enabled: Optional[bool] = None


@router.post("/clients/{client_id}/campaign", status_code=201)
async def ops_trigger_campaign(
    client_id: uuid.UUID,
    body: TriggerCampaignRequest,
    db: AsyncSession = Depends(get_db),
):
    client = await db.get(m.Client, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")

    from src.agents.orchestrator import Orchestrator

    orchestrator = Orchestrator()
    result = await orchestrator.run_client_campaign(
        client_id=client_id,
        email_mode=body.email_mode,
        difficulty=body.difficulty,
        vishing_enabled=body.vishing_enabled,
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result
