import uuid
import logging
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import (
    Campaign, CampaignResult, Employee, TrainingAssignment, AuditLog,
)
from src.engine.training_engine import FAILURE_TO_TRAINING, SCENARIO_TRAINING_MAP, TRAINING_CONTENT, TRAINING_POINTS, TRAINING_TYPES

logger = logging.getLogger(__name__)


FEEDBACK_INTRO = """
<p>Bei der letzten Phishing-Simulation wurde festgestellt, dass Sie auf einen simulierten Phishing-Versuch hereingefallen sind.
Dies ist eine wertvolle Lernerfahrung – das Ziel ist nicht zu bestrafen, sondern zu sensibilisieren.</p>
"""


def _generate_feedback_html(
    employee_name: str,
    failure_type: str,
    scenario_type: str | None,
    training_type: str,
    score_before: float,
) -> str:
    failure_labels = {
        "credentials_submitted": "Sie haben Ihre Anmeldedaten auf einer gefälschten Seite eingegeben.",
        "link_clicked": "Sie haben auf einen Link in einer simulierten Phishing-E-Mail geklickt.",
    }
    failure_desc = failure_labels.get(failure_type, "Es wurde ein sicherheitsrelevantes Verhalten festgestellt.")

    training_key = FAILURE_TO_TRAINING.get(failure_type)
    if not training_key and scenario_type:
        training_key = SCENARIO_TRAINING_MAP.get(scenario_type)
    if not training_key:
        training_key = "phishing_awareness"

    title = TRAINING_TYPES.get(training_key, "Sicherheitsschulung")
    points_list = TRAINING_POINTS.get(training_key, TRAINING_POINTS["phishing_awareness"])
    points_html = "".join(f"<li>{p}</li>" for p in points_list)

    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>
body {{ font-family: 'Segoe UI', Arial, sans-serif; color: #1a1a2e; max-width: 640px; margin: 0 auto; padding: 24px; }}
h2 {{ color: #1a1a2e; border-bottom: 2px solid #e0e0e0; padding-bottom: 8px; }}
.alert {{ background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 16px; margin: 16px 0; }}
.score {{ display: inline-block; padding: 4px 12px; border-radius: 12px; font-size: 14px; font-weight: 600; }}
.score.low {{ background: #d4edda; color: #155724; }}
.score.medium {{ background: #fff3cd; color: #856404; }}
.score.high {{ background: #f8d7da; color: #721c24; }}
ul {{ padding-left: 20px; }}
li {{ margin-bottom: 8px; line-height: 1.5; }}
.footer {{ margin-top: 32px; font-size: 12px; color: #999; text-align: center; }}
</style></head><body>
<h2>Phishing-Simulation: Persönliches Feedback & Schulung</h2>
<div class="alert"><strong>Ergebnis:</strong> {failure_desc}</div>
{FEEDBACK_INTRO}
<h3>{title}</h3>
<ul>{points_html}</ul>
<h4>Ihr Risikoscore: <span class="score {'high' if score_before >= 40 else 'medium' if score_before >= 15 else 'low'}">{score_before}/100</span></h4>
<p>Ein niedrigerer Wert bedeutet ein sichereres Verhalten. Ihre Teilnahme an dieser Schulung hilft, Ihren Score zu verbessern.</p>
<h4>Nächste Schritte:</h4>
<ol>
<li>Lesen Sie die oben genannten Punkte sorgfältig durch</li>
<li>Wenden Sie die Tipps im Arbeitsalltag an</li>
<li>Bei Fragen wenden Sie sich an Ihr IT-Sicherheitsteam</li>
</ol>
<div class="footer">
PhishGuard – Automatisierte Phishing-Simulation & Sicherheitsbewusstsein | Vertraulich
</div>
</body></html>"""


async def assign_training_feedback(db: AsyncSession, campaign: Campaign) -> list[dict]:
    results_q = await db.execute(
        select(CampaignResult).where(CampaignResult.campaign_id == campaign.id)
    )
    results = list(results_q.scalars().all())

    assignments_q = await db.execute(
        select(TrainingAssignment).where(
            TrainingAssignment.campaign_id == campaign.id,
            TrainingAssignment.status == "pending",
        )
    )
    assignments = list(assignments_q.scalars().all())

    assignment_map: dict[uuid.UUID, TrainingAssignment] = {}
    for a in assignments:
        if a.employee_id not in assignment_map:
            assignment_map[a.employee_id] = a

    feedback_entries = []
    for cr in results:
        if not (cr.credentials_submitted or cr.link_clicked):
            continue

        assignment = assignment_map.get(cr.employee_id)
        if not assignment:
            continue
        if assignment.feedback_sent_at:
            continue

        emp_q = await db.execute(select(Employee).where(Employee.id == cr.employee_id))
        employee = emp_q.scalar_one_or_none()
        emp_name = employee.name_hash[:12] if employee and employee.name_hash else str(cr.employee_id)[:8]

        failure_type = "credentials_submitted" if cr.credentials_submitted else "link_clicked"
        scenario_type = None

        feedback_html = _generate_feedback_html(
            employee_name=emp_name,
            failure_type=failure_type,
            scenario_type=scenario_type,
            training_type=assignment.training_type,
            score_before=assignment.score_before,
        )

        assignment.feedback_sent_at = datetime.now(timezone.utc)

        log = AuditLog(
            client_id=campaign.client_id,
            action="training_feedback_generated",
            details={
                "assignment_id": str(assignment.id),
                "employee_id": str(cr.employee_id),
                "campaign_id": str(campaign.id),
                "training_type": assignment.training_type,
            },
        )
        db.add(log)

        feedback_entries.append({
            "assignment_id": str(assignment.id),
            "employee_id": str(cr.employee_id),
            "training_type": assignment.training_type,
            "feedback_html": feedback_html,
        })

    if feedback_entries:
        await db.flush()
        logger.info("Generated training feedback for %d employees in campaign %s", len(feedback_entries), campaign.id)

    return feedback_entries


async def get_employee_feedback(
    db: AsyncSession,
    employee_id: uuid.UUID,
    campaign_id: uuid.UUID | None = None,
) -> list[dict]:
    q = select(TrainingAssignment).where(
        TrainingAssignment.employee_id == employee_id,
        TrainingAssignment.feedback_sent_at.isnot(None),
    )
    if campaign_id:
        q = q.where(TrainingAssignment.campaign_id == campaign_id)
    q = q.order_by(TrainingAssignment.assigned_at.desc())

    rows = await db.execute(q)
    assignments = list(rows.scalars().all())

    result = []
    for a in assignments:
        failure_type = "link_clicked"
        scenario_type = None
        emp_q = await db.execute(select(Employee).where(Employee.id == employee_id))
        employee = emp_q.scalar_one_or_none()
        emp_name = employee.name_hash[:12] if employee and employee.name_hash else str(employee_id)[:8]

        feedback_html = _generate_feedback_html(
            employee_name=emp_name,
            failure_type=failure_type,
            scenario_type=scenario_type,
            training_type=a.training_type,
            score_before=a.score_before,
        )

        result.append({
            "assignment_id": str(a.id),
            "campaign_id": str(a.campaign_id) if a.campaign_id else None,
            "training_type": a.training_type,
            "training_title": TRAINING_TYPES.get(a.training_type, a.training_type),
            "score_before": a.score_before,
            "feedback_sent_at": a.feedback_sent_at.isoformat() if a.feedback_sent_at else None,
            "feedback_html": feedback_html,
        })

    return result
