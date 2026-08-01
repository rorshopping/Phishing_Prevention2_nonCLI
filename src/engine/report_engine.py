import uuid
import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Client, Campaign, CampaignResult, CampaignStatus, Employee, RiskScore, TrainingAssignment,
)

logger = logging.getLogger(__name__)

REPORT_CSS = """
body { font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a2e; margin: 0; padding: 0; background: #f8f9fa; }
.header { background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 40px 60px; }
.header h1 { margin: 0; font-size: 28px; font-weight: 300; }
.header .subtitle { font-size: 14px; opacity: 0.8; margin-top: 8px; }
.content { padding: 40px 60px; max-width: 1000px; margin: 0 auto; background: white; }
.section { margin-bottom: 40px; }
.section h2 { font-size: 20px; border-bottom: 2px solid #e0e0e0; padding-bottom: 10px; margin-bottom: 20px; color: #1a1a2e; }
.metric-row { display: flex; gap: 20px; flex-wrap: wrap; margin-bottom: 24px; }
.metric-card { flex: 1; min-width: 140px; background: #f8f9fa; border-radius: 8px; padding: 20px; text-align: center; border: 1px solid #e8e8e8; }
.metric-card .value { font-size: 32px; font-weight: 700; color: #1a1a2e; }
.metric-card .label { font-size: 12px; text-transform: uppercase; letter-spacing: 1px; color: #666; margin-top: 4px; }
.metric-card.danger .value { color: #e74c3c; }
.metric-card.warning .value { color: #f39c12; }
.metric-card.success .value { color: #27ae60; }
table { width: 100%; border-collapse: collapse; margin: 16px 0; }
th { background: #1a1a2e; color: white; padding: 12px 16px; text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: 0.5px; }
td { padding: 10px 16px; border-bottom: 1px solid #e8e8e8; font-size: 14px; }
tr:hover td { background: #f0f0f5; }
.badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; }
.badge.low { background: #d4edda; color: #155724; }
.badge.medium { background: #fff3cd; color: #856404; }
.badge.high { background: #f8d7da; color: #721c24; }
.badge.critical { background: #e74c3c; color: white; }
.footer { text-align: center; padding: 20px; font-size: 12px; color: #999; }
.distribution-bar { display: flex; height: 24px; border-radius: 4px; overflow: hidden; margin: 12px 0; }
.distribution-bar .seg { display: flex; align-items: center; justify-content: center; font-size: 11px; color: white; font-weight: 600; }
"""


async def generate_client_report(
    db: AsyncSession,
    client_id: uuid.UUID,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> str:
    client_q = await db.execute(select(Client).where(Client.id == client_id))
    client = client_q.scalar_one_or_none()
    if not client:
        return "<h1>Client not found</h1>"

    if not date_to:
        date_to = datetime.now(timezone.utc)
    if not date_from:
        date_from = date_to - timedelta(days=365)

    emp_q = await db.execute(
        select(func.count()).select_from(Employee).where(
            Employee.client_id == client_id,
            Employee.is_active == True,
        )
    )
    total_employees = emp_q.scalar() or 0

    stats_q = await db.execute(
        select(
            func.count(Campaign.id),
            func.coalesce(func.sum(Campaign.sent_count), 0),
            func.coalesce(func.sum(Campaign.click_count), 0),
            func.coalesce(func.sum(Campaign.fail_count), 0),
        ).where(
            Campaign.client_id == client_id,
            Campaign.created_at >= date_from,
            Campaign.created_at <= date_to,
        )
    )
    total_campaigns, total_sent, total_clicks, total_fails = stats_q.one()

    campaigns_q = await db.execute(
        select(Campaign).where(
            Campaign.client_id == client_id,
            Campaign.created_at >= date_from,
            Campaign.created_at <= date_to,
        ).order_by(Campaign.created_at.desc())
    )
    campaigns = list(campaigns_q.scalars().all())

    risk_q = await db.execute(
        select(func.avg(RiskScore.score)).where(
            RiskScore.client_id == client_id,
        )
    )
    avg_risk = round(risk_q.scalar() or 0.0, 1)

    risk_dist: dict[str, int] = {"low": 0, "medium": 0, "high": 0, "critical": 0}
    latest_risk_q = await db.execute(
        select(RiskScore).where(RiskScore.client_id == client_id)
    )
    for rs in latest_risk_q.scalars().all():
        risk_dist[rs.risk_level] = risk_dist.get(rs.risk_level, 0) + 1

    training_q = await db.execute(
        select(func.count()).select_from(TrainingAssignment).where(
            TrainingAssignment.client_id == client_id,
            TrainingAssignment.status == "pending",
        )
    )
    pending_training = training_q.scalar() or 0

    training_done_q = await db.execute(
        select(func.count()).select_from(TrainingAssignment).where(
            TrainingAssignment.client_id == client_id,
            TrainingAssignment.status == "completed",
        )
    )
    completed_training = training_done_q.scalar() or 0

    click_rate = round((total_clicks / total_sent * 100), 1) if total_sent else 0.0
    fail_rate = round((total_fails / total_sent * 100), 1) if total_sent else 0.0

    total_risk = sum(risk_dist.values())
    def bar_pct(v: int) -> str:
        return f"{round(v / total_risk * 100)}%" if total_risk else "0%"

    rows_html = ""
    for c in campaigns:
        cr = round((c.click_count / c.sent_count * 100), 1) if c.sent_count else 0.0
        rows_html += f"""
        <tr>
            <td>{c.name[:40]}</td>
            <td>{c.status.value}</td>
            <td>{c.difficulty}</td>
            <td>{c.sent_count}</td>
            <td>{c.click_count}</td>
            <td>{c.fail_count}</td>
            <td>{cr}%</td>
            <td>{c.created_at.strftime('%Y-%m-%d') if c.created_at else '-'}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Sicherheitsreport – {client.company_name}</title>
<style>{REPORT_CSS}</style></head><body>
<div class="header">
    <h1>Sicherheitsreport: {client.company_name}</h1>
    <div class="subtitle">Zeitraum: {date_from.strftime('%d.%m.%Y')} – {date_to.strftime('%d.%m.%Y')} | Erstellt: {datetime.now(timezone.utc).strftime('%d.%m.%Y %H:%M')} UTC</div>
</div>
<div class="content">
    <div class="section">
        <h2>Übersicht</h2>
        <div class="metric-row">
            <div class="metric-card"><div class="value">{total_employees}</div><div class="label">Mitarbeiter</div></div>
            <div class="metric-card"><div class="value">{total_campaigns}</div><div class="label">Kampagnen</div></div>
            <div class="metric-card"><div class="value">{total_sent}</div><div class="label">E-Mails gesendet</div></div>
            <div class="metric-card {'danger' if avg_risk >= 40 else 'warning' if avg_risk >= 15 else 'success'}"><div class="value">{avg_risk}</div><div class="label">Risikoscore Ø</div></div>
        </div>
    </div>
    <div class="section">
        <h2>Klick- & Failraten</h2>
        <div class="metric-row">
            <div class="metric-card danger"><div class="value">{click_rate}%</div><div class="label">Klickrate</div></div>
            <div class="metric-card danger"><div class="value">{fail_rate}%</div><div class="label">Failrate (Credentials)</div></div>
            <div class="metric-card warning"><div class="value">{pending_training}</div><div class="label">Ausstehende Schulungen</div></div>
            <div class="metric-card success"><div class="value">{completed_training}</div><div class="label">Abgeschlossene Schulungen</div></div>
        </div>
    </div>
    <div class="section">
        <h2>Risikoverteilung</h2>
        <div class="distribution-bar">
            <div class="seg" style="width:{bar_pct(risk_dist['critical'])};background:#e74c3c;">{risk_dist['critical']}</div>
            <div class="seg" style="width:{bar_pct(risk_dist['high'])};background:#f39c12;">{risk_dist['high']}</div>
            <div class="seg" style="width:{bar_pct(risk_dist['medium'])};background:#3498db;">{risk_dist['medium']}</div>
            <div class="seg" style="width:{bar_pct(risk_dist['low'])};background:#27ae60;">{risk_dist['low']}</div>
        </div>
        <table>
            <tr><th>Level</th><th>Anzahl</th><th>Anteil</th></tr>
            <tr><td><span class="badge critical">Critical</span></td><td>{risk_dist['critical']}</td><td>{bar_pct(risk_dist['critical'])}</td></tr>
            <tr><td><span class="badge high">High</span></td><td>{risk_dist['high']}</td><td>{bar_pct(risk_dist['high'])}</td></tr>
            <tr><td><span class="badge medium">Medium</span></td><td>{risk_dist['medium']}</td><td>{bar_pct(risk_dist['medium'])}</td></tr>
            <tr><td><span class="badge low">Low</span></td><td>{risk_dist['low']}</td><td>{bar_pct(risk_dist['low'])}</td></tr>
        </table>
    </div>
    <div class="section">
        <h2>Kampagnenverlauf</h2>
        <table>
            <tr><th>Name</th><th>Status</th><th>Schwierigkeit</th><th>Gesendet</th><th>Clicks</th><th>Fails</th><th>Klickrate</th><th>Datum</th></tr>
            {rows_html}
        </table>
    </div>
</div>
<div class="footer">
    PhishGuard – Automatisierte Phishing-Simulation & Sicherheitsbewusstsein | Vertraulich
</div>
</body></html>"""


async def generate_client_report_json(
    db: AsyncSession,
    client_id: uuid.UUID,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> dict[str, Any]:
    client_q = await db.execute(select(Client).where(Client.id == client_id))
    client = client_q.scalar_one_or_none()
    if not client:
        return {"error": "Client not found"}

    if not date_to:
        date_to = datetime.now(timezone.utc)
    if not date_from:
        date_from = date_to - timedelta(days=365)

    emp_q = await db.execute(
        select(func.count()).select_from(Employee).where(
            Employee.client_id == client_id, Employee.is_active == True,
        )
    )
    total_employees = emp_q.scalar() or 0

    stats_q = await db.execute(
        select(
            func.count(Campaign.id).label("campaigns"),
            func.coalesce(func.sum(Campaign.sent_count), 0).label("sent"),
            func.coalesce(func.sum(Campaign.click_count), 0).label("clicks"),
            func.coalesce(func.sum(Campaign.fail_count), 0).label("fails"),
        ).where(
            Campaign.client_id == client_id,
            Campaign.created_at >= date_from, Campaign.created_at <= date_to,
        )
    )
    row = stats_q.one()
    total_campaigns = int(row.campaigns)
    total_sent = int(row.sent)
    total_clicks = int(row.clicks)
    total_fails = int(row.fails)

    click_rate = round((total_clicks / total_sent * 100), 1) if total_sent else 0.0
    fail_rate = round((total_fails / total_sent * 100), 1) if total_sent else 0.0

    from src.engine.risk_engine import get_client_risk_summary, get_client_risk_trend
    risk = await get_client_risk_summary(db, client_id)
    trend = await get_client_risk_trend(db, client_id, months=12)

    campaigns_q = await db.execute(
        select(Campaign).where(
            Campaign.client_id == client_id,
            Campaign.created_at >= date_from, Campaign.created_at <= date_to,
        ).order_by(Campaign.created_at.desc())
    )
    campaigns_list = []
    for c in campaigns_q.scalars().all():
        cr = round((c.click_count / c.sent_count * 100), 1) if c.sent_count else 0.0
        campaigns_list.append({
            "id": str(c.id),
            "name": c.name,
            "status": c.status.value,
            "difficulty": c.difficulty,
            "sent_count": c.sent_count,
            "click_count": c.click_count,
            "fail_count": c.fail_count,
            "click_rate": cr,
            "created_at": c.created_at.isoformat() if c.created_at else None,
        })

    return {
        "client_id": str(client_id),
        "company_name": client.company_name,
        "period": {
            "from": date_from.isoformat(),
            "to": date_to.isoformat(),
        },
        "summary": {
            "total_employees": total_employees,
            "total_campaigns": total_campaigns,
            "total_emails_sent": total_sent,
            "total_clicks": total_clicks,
            "total_fails": total_fails,
            "click_rate": click_rate,
            "fail_rate": fail_rate,
        },
        "risk": risk,
        "risk_trend": trend,
        "campaigns": campaigns_list,
    }


async def generate_campaign_report(
    db: AsyncSession,
    campaign_id: uuid.UUID,
) -> str:
    campaign_q = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = campaign_q.scalar_one_or_none()
    if not campaign:
        return "<h1>Campaign not found</h1>"

    client_q = await db.execute(select(Client).where(Client.id == campaign.client_id))
    client = client_q.scalar_one_or_none()

    results_q = await db.execute(
        select(CampaignResult).where(CampaignResult.campaign_id == campaign_id)
    )
    results = list(results_q.scalars().all())

    sent = len(results)
    opened = sum(1 for r in results if r.email_opened)
    clicked = sum(1 for r in results if r.link_clicked)
    submitted = sum(1 for r in results if r.credentials_submitted)
    reported = sum(1 for r in results if r.reported_phishing)

    open_rate = round((opened / sent * 100), 1) if sent else 0.0
    click_rate = round((clicked / sent * 100), 1) if sent else 0.0
    fail_rate = round((submitted / sent * 100), 1) if sent else 0.0
    report_rate = round((reported / sent * 100), 1) if sent else 0.0

    results_rows = ""
    for r in results:
        emp_q = await db.execute(select(Employee).where(Employee.id == r.employee_id))
        emp = emp_q.scalar_one_or_none()
        name = emp.name_hash[:12] if emp and emp.name_hash else str(r.employee_id)[:8]
        results_rows += f"""
        <tr>
            <td>{name}</td>
            <td>{'✅' if r.email_opened else '—'}</td>
            <td>{'✅' if r.link_clicked else '—'}</td>
            <td>{'✅' if r.credentials_submitted else '—'}</td>
            <td>{'✅' if r.reported_phishing else '—'}</td>
            <td>{'✅' if r.training_completed else '—'}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>Kampagnenreport – {campaign.name}</title>
<style>{REPORT_CSS}</style></head><body>
<div class="header">
    <h1>Kampagnenreport: {campaign.name[:50]}</h1>
    <div class="subtitle">{client.company_name if client else ''} | {campaign.created_at.strftime('%d.%m.%Y') if campaign.created_at else ''} | Schwierigkeit: {campaign.difficulty}</div>
</div>
<div class="content">
    <div class="section">
        <h2>Ergebnisse</h2>
        <div class="metric-row">
            <div class="metric-card"><div class="value">{sent}</div><div class="label">Gesendet</div></div>
            <div class="metric-card warning"><div class="value">{open_rate}%</div><div class="label">Öffnungsrate</div></div>
            <div class="metric-card danger"><div class="value">{click_rate}%</div><div class="label">Klickrate</div></div>
            <div class="metric-card danger"><div class="value">{fail_rate}%</div><div class="label">Failrate</div></div>
            <div class="metric-card success"><div class="value">{report_rate}%</div><div class="label">Meldungen</div></div>
        </div>
    </div>
    <div class="section">
        <h2>Mitarbeiter-Details</h2>
        <table>
            <tr><th>Mitarbeiter</th><th>Geöffnet</th><th>Geklickt</th><th>Credentials</th><th>Gemeldet</th><th>Training</th></tr>
            {results_rows}
        </table>
    </div>
</div>
<div class="footer">
    PhishGuard – Automatisierte Phishing-Simulation & Sicherheitsbewusstsein | Vertraulich
</div>
</body></html>"""


def generate_campaign_report_csv(results: list, employee_map: dict[str, str]) -> str:
    import io
    import csv

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Employee", "Email Opened", "Link Clicked", "Credentials Submitted", "Reported", "Training Completed", "Opened At", "Clicked At"])
    for r in results:
        emp_id = str(r.employee_id)
        name = employee_map.get(emp_id, emp_id[:8])
        writer.writerow([
            name,
            "Yes" if r.email_opened else "No",
            "Yes" if r.link_clicked else "No",
            "Yes" if r.credentials_submitted else "No",
            "Yes" if r.reported_phishing else "No",
            "Yes" if r.training_completed else "No",
            r.opened_at.strftime("%Y-%m-%d %H:%M") if r.opened_at else "",
            r.clicked_at.strftime("%Y-%m-%d %H:%M") if r.clicked_at else "",
        ])
    return out.getvalue()


def generate_client_report_csv(campaigns: list) -> str:
    import io
    import csv

    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["Campaign Name", "Status", "Difficulty", "Sent", "Clicks", "Fails", "Click Rate (%)", "Created At", "Completed At"])
    for c in campaigns:
        click_rate = round((c.click_count / c.sent_count * 100), 1) if c.sent_count else 0.0
        writer.writerow([
            c.name,
            c.status.value,
            c.difficulty,
            c.sent_count,
            c.click_count,
            c.fail_count,
            click_rate,
            c.created_at.strftime("%Y-%m-%d") if c.created_at else "",
            c.completed_at.strftime("%Y-%m-%d") if c.completed_at else "",
        ])
    return out.getvalue()
