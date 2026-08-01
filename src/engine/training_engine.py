import uuid
import logging
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Campaign, CampaignResult, CampaignStatus, Employee,
    TrainingAssignment, RiskScore, Client, AuditLog,
)

logger = logging.getLogger(__name__)

TRAINING_TYPES = {
    "phishing_awareness": "Phishing Awareness – Erkennen und Melden verdächtiger E-Mails",
    "password_security": "Passwortsicherheit – Zwei-Faktor-Authentifizierung und sichere Passwörter",
    "social_engineering": "Social Engineering – Schutz vor Manipulation am Arbeitsplatz",
    "safe_browsing": "Sicheres Surfen – Erkennen verdächtiger Links und Websites",
    "data_protection": "Datenschutz – Umgang mit vertraulichen Informationen",
}

FAILURE_TO_TRAINING = {
    "credentials_submitted": "password_security",
    "link_clicked": "phishing_awareness",
}

SCENARIO_TRAINING_MAP = {
    "bank_transfer": "social_engineering",
    "invoice": "social_engineering",
    "shared_doc": "safe_browsing",
    "password_reset": "password_security",
    "security_alert": "safe_browsing",
    "voicemail": "social_engineering",
    "calendar_invite": "safe_browsing",
    "urgent_review": "social_engineering",
    "bonus": "social_engineering",
    "vacation_policy": "social_engineering",
}

TRAINING_CONTENT = """
<h3>{title}</h3>
<p>{description}</p>
<h4>Wichtige Punkte:</h4>
<ul>
{points}
</ul>
<h4>Nächste Schritte:</h4>
<ol>
<li>Lesen Sie die bereitgestellten Materialien sorgfältig durch</li>
<li>Absolvieren Sie das kurze Verständnisquiz am Ende</li>
<li>Wenden Sie das Gelernte im Arbeitsalltag an</li>
<li>Bei Fragen wenden Sie sich an Ihr IT-Sicherheitsteam</li>
</ol>
<p><em>Diese Schulung wurde automatisch zugewiesen nach einer Phishing-Simulation, bei der
Verbesserungspotential festgestellt wurde.</em></p>
"""

TRAINING_POINTS = {
    "phishing_awareness": [
        "Überprüfen Sie immer den Absender einer E-Mail genau",
        "Seien Sie vorsichtig bei unerwarteten Anhängen oder Links",
        "Achten Sie auf Rechtschreibfehler und ungewöhnliche Formulierungen",
        "Bei Unsicherheit: Nicht klicken, sondern direkt beim Absender nachfragen",
        "Nutzen Sie die Meldefunktion für verdächtige E-Mails",
    ],
    "password_security": [
        "Verwenden Sie starke, einzigartige Passwörter für jeden Dienst",
        "Aktivieren Sie die Zwei-Faktor-Authentifizierung (2FA) wo immer möglich",
        "Geben Sie Ihr Passwort niemals weiter – auch nicht an IT-Mitarbeiter",
        "Verwenden Sie einen Passwort-Manager für sichere Passwörter",
        "Ändern Sie Ihr Passwort sofort bei Verdacht auf Kompromittierung",
    ],
    "social_engineering": [
        "Seien Sie skeptisch bei unerwarteten Anrufen oder Nachrichten",
        "Geben Sie keine vertraulichen Informationen am Telefon preis",
        "Verifizieren Sie die Identität des Absenders über einen zweiten Kanal",
        "Druck und Dringlichkeit sind typische Anzeichen von Social Engineering",
        "Bei ungewöhnlichen Anfragen: Immer Rückfrage beim Vorgesetzten halten",
    ],
    "safe_browsing": [
        "Überprüfen Sie URLs bevor Sie klicken (Mouse-over-Test)",
        "Achten Sie auf HTTPS-Verschlüsselung in der Adresszeile",
        "Laden Sie keine Dateien von unbekannten Quellen herunter",
        "Öffnen Sie keine verdächtigen Kalendereinladungen oder Dokumentfreigaben",
        "Melden Sie verdächtige Websites Ihrer IT-Abteilung",
    ],
    "data_protection": [
        "Klassifizieren Sie Daten nach ihrer Vertraulichkeit",
        "Versenden Sie vertrauliche Daten nur verschlüsselt",
        "Halten Sie Ihre Bildschirme in öffentlichen Bereichen sauber",
        "Entsorgen Sie Dokumente sicher (Aktenvernichter)",
        "Melden Sie Datenverluste sofort Ihrer Datenschutzabteilung",
    ],
}


async def assign_training_for_employee(
    db: AsyncSession,
    employee_id: uuid.UUID,
    client_id: uuid.UUID,
    campaign_id: uuid.UUID,
    failure_type: str = "link_clicked",
    scenario_type: str | None = None,
) -> dict[str, Any]:
    training_key = FAILURE_TO_TRAINING.get(failure_type)
    if not training_key and scenario_type:
        training_key = SCENARIO_TRAINING_MAP.get(scenario_type, "phishing_awareness")
    if not training_key:
        training_key = "phishing_awareness"

    score_q = await db.execute(
        select(func.coalesce(func.max(RiskScore.score), 0.0))
        .where(RiskScore.employee_id == employee_id)
    )
    score_before = score_q.scalar() or 0.0

    existing = await db.execute(
        select(TrainingAssignment).where(
            TrainingAssignment.employee_id == employee_id,
            TrainingAssignment.campaign_id == campaign_id,
            TrainingAssignment.training_type == training_key,
        )
    )
    if existing.scalar_one_or_none():
        return {"status": "already_assigned", "training_type": training_key}

    assignment = TrainingAssignment(
        employee_id=employee_id,
        client_id=client_id,
        campaign_id=campaign_id,
        training_type=training_key,
        status="pending",
        score_before=score_before,
    )
    db.add(assignment)
    await db.flush()

    log = AuditLog(
        client_id=client_id,
        action="training_assigned",
        details={
            "employee_id": str(employee_id),
            "campaign_id": str(campaign_id),
            "training_type": training_key,
            "score_before": score_before,
        },
    )
    db.add(log)

    logger.info(
        "Assigned training '%s' to employee %s (score: %.1f)",
        training_key, employee_id, score_before,
    )

    return {
        "assignment_id": str(assignment.id),
        "employee_id": str(employee_id),
        "training_type": training_key,
        "status": "assigned",
        "score_before": score_before,
    }


async def assign_bulk_training_for_campaign(
    db: AsyncSession,
    campaign_id: uuid.UUID,
) -> list[dict[str, Any]]:
    results_q = await db.execute(
        select(CampaignResult).where(CampaignResult.campaign_id == campaign_id)
    )
    results = list(results_q.scalars().all())

    campaign_q = await db.execute(
        select(Campaign).where(Campaign.id == campaign_id)
    )
    campaign = campaign_q.scalar_one_or_none()
    if not campaign:
        return []

    assignments = []
    for cr in results:
        if cr.credentials_submitted or cr.link_clicked:
            failure = "credentials_submitted" if cr.credentials_submitted else "link_clicked"
            result = await assign_training_for_employee(
                db=db,
                employee_id=cr.employee_id,
                client_id=campaign.client_id,
                campaign_id=campaign_id,
                failure_type=failure,
            )
            assignments.append(result)

    return assignments


async def complete_training(
    db: AsyncSession,
    assignment_id: uuid.UUID,
    score_after: float | None = None,
) -> dict[str, Any]:
    assignment_q = await db.execute(
        select(TrainingAssignment).where(TrainingAssignment.id == assignment_id)
    )
    assignment = assignment_q.scalar_one_or_none()
    if not assignment:
        return {"error": "Assignment not found"}

    assignment.status = "completed"
    assignment.completed_at = datetime.now(timezone.utc)
    if score_after is not None:
        assignment.score_after = score_after

    result_q = await db.execute(
        select(CampaignResult).where(
            CampaignResult.employee_id == assignment.employee_id,
        ).order_by(CampaignResult.created_at.desc()).limit(1)
    )
    latest_result = result_q.scalar_one_or_none()
    if latest_result:
        latest_result.training_completed = True

    await db.flush()

    log = AuditLog(
        client_id=assignment.client_id,
        action="training_completed",
        details={
            "assignment_id": str(assignment_id),
            "employee_id": str(assignment.employee_id),
            "training_type": assignment.training_type,
        },
    )
    db.add(log)

    return {
        "assignment_id": str(assignment_id),
        "status": "completed",
        "completed_at": assignment.completed_at.isoformat(),
    }


async def get_pending_training(
    db: AsyncSession,
    client_id: uuid.UUID | None = None,
) -> list[dict[str, Any]]:
    q = select(TrainingAssignment).where(TrainingAssignment.status == "pending")
    if client_id:
        q = q.where(TrainingAssignment.client_id == client_id)
    q = q.order_by(TrainingAssignment.assigned_at.desc())

    results_q = await db.execute(q)
    assignments = list(results_q.scalars().all())

    return [
        {
            "id": str(a.id),
            "employee_id": str(a.employee_id),
            "client_id": str(a.client_id),
            "campaign_id": str(a.campaign_id) if a.campaign_id else None,
            "training_type": a.training_type,
            "training_title": TRAINING_TYPES.get(a.training_type, a.training_type),
            "status": a.status,
            "assigned_at": a.assigned_at.isoformat(),
            "score_before": a.score_before,
        }
        for a in assignments
    ]


def get_training_content(training_type: str) -> dict[str, Any]:
    title = TRAINING_TYPES.get(training_type, "Sicherheitsschulung")
    points_list = TRAINING_POINTS.get(training_type, TRAINING_POINTS["phishing_awareness"])
    points_html = "".join(f"<li>{p}</li>" for p in points_list)
    description = title
    html = TRAINING_CONTENT.format(
        title=title,
        description=description,
        points=points_html,
    )
    return {
        "training_type": training_type,
        "title": title,
        "html": html,
    }


async def get_client_training_roi(
    db: AsyncSession,
    client_id: uuid.UUID,
) -> dict[str, Any]:
    assignments_q = await db.execute(
        select(TrainingAssignment).where(
            TrainingAssignment.client_id == client_id,
        )
    )
    assignments = list(assignments_q.scalars().all())

    total_assigned = len(assignments)
    completed = [a for a in assignments if a.status == "completed"]
    pending = [a for a in assignments if a.status == "pending"]
    total_completed = len(completed)

    by_type: dict[str, dict[str, Any]] = {}
    for a in assignments:
        t = a.training_type
        if t not in by_type:
            by_type[t] = {
                "training_type": t,
                "title": TRAINING_TYPES.get(t, t),
                "assigned": 0,
                "completed": 0,
                "avg_score_before": 0.0,
                "avg_score_after": 0.0,
                "score_improvement": 0.0,
                "scores_before": [],
                "scores_after": [],
            }
        by_type[t]["assigned"] += 1
        if a.status == "completed":
            by_type[t]["completed"] += 1
        by_type[t]["scores_before"].append(a.score_before)
        if a.score_after is not None:
            by_type[t]["scores_after"].append(a.score_after)

    training_types = []
    for t, info in by_type.items():
        avg_before = round(sum(info["scores_before"]) / len(info["scores_before"]), 1) if info["scores_before"] else 0.0
        avg_after = round(sum(info["scores_after"]) / len(info["scores_after"]), 1) if info["scores_after"] else 0.0
        improvement = round(avg_before - avg_after, 1)
        training_types.append({
            "training_type": t,
            "title": info["title"],
            "assigned": info["assigned"],
            "completed": info["completed"],
            "completion_rate": round((info["completed"] / info["assigned"] * 100), 1) if info["assigned"] else 0.0,
            "avg_score_before": avg_before,
            "avg_score_after": avg_after,
            "score_improvement": improvement,
            "improvement_percent": round((improvement / max(avg_before, 0.1) * 100), 1) if avg_before > 0 else 0.0,
        })
        del info["scores_before"], info["scores_after"]

    avg_all_before = round(sum(a.score_before for a in assignments) / total_assigned, 1) if total_assigned else 0.0
    completed_with_after = [a for a in completed if a.score_after is not None]
    avg_all_after = round(sum(a.score_after for a in completed_with_after) / len(completed_with_after), 1) if completed_with_after else 0.0

    return {
        "client_id": str(client_id),
        "total_assignments": total_assigned,
        "total_completed": total_completed,
        "total_pending": len(pending),
        "completion_rate": round((total_completed / total_assigned * 100), 1) if total_assigned else 0.0,
        "overall_avg_score_before": avg_all_before,
        "overall_avg_score_after": avg_all_after,
        "overall_score_improvement": round(avg_all_before - avg_all_after, 1),
        "improvement_percent": round(((avg_all_before - avg_all_after) / max(avg_all_before, 0.1) * 100), 1) if avg_all_before > 0 else 0.0,
        "by_training_type": training_types,
    }
