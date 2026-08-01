import hashlib
import hmac
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.database import models as m

logger = logging.getLogger("phishguard.gdpr")

SALT = settings.gdpr_hash_salt.encode("utf-8") if settings.gdpr_hash_salt else b""

RETENTION_CAMPAIGN_DAYS = 365
RETENTION_RESULT_DAYS = 365
RETENTION_VISHING_DAYS = 180
RETENTION_AUDIT_LOG_DAYS = 730


def hash_pii(data: str) -> str:
    return hmac.new(SALT, data.encode("utf-8"), hashlib.sha256).hexdigest()


PII_FIELDS = {"email_hash", "name_hash", "phone_number_hash", "linkedin_url"}


def anonymize_employee(employee_data: dict) -> dict:
    anonymized = {}
    for key, value in employee_data.items():
        if key in PII_FIELDS and value:
            anonymized[key] = hash_pii(str(value))
        elif key == "public_data" and isinstance(value, dict):
            anonymized[key] = {"anonymized": True}
        else:
            anonymized[key] = value
    return anonymized


async def validate_consent(client_id, db: AsyncSession) -> bool:
    result = await db.execute(
        select(m.AuditLog).where(
            m.AuditLog.client_id == client_id,
            m.AuditLog.action == "consent_recorded",
        ).limit(1)
    )
    return result.scalar_one_or_none() is not None


def generate_data_processing_agreement(client) -> str:
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return f"""
DATA PROCESSING AGREEMENT (DPA)

Date: {today}

Between:
  PhishGuard Ltd (Data Processor)
  and
  {client.company_name} (Data Controller)

1. SCOPE
   The Processor processes personal data on behalf of the Controller
   for the purpose of security awareness phishing simulations.

2. DATA CATEGORIES
   - Employee names (hashed), work email addresses (hashed),
     job roles, departments, and LinkedIn URLs (where provided).

3. PURPOSES
   - Conduct simulated phishing campaigns
   - Generate anonymised training reports
   - Improve AI-driven threat detection models

4. DATA SUBJECT RIGHTS
   The Controller may request access, rectification, or erasure
   of personal data by contacting privacy@phishguard.ai.

5. RETENTION
   Campaign data is retained for a maximum of {RETENTION_CAMPAIGN_DAYS} days.
   Vishing session recordings are retained for {RETENTION_VISHING_DAYS} days.

6. SECURITY
   All personal data is hashed (SHA-256) with a secret salt before storage.
   Raw personal data is never persisted in the database.

7. COMPLIANCE
   This DPA is governed by the General Data Protection Regulation (GDPR)
   and applicable local data protection laws.

Signed on behalf of PhishGuard Ltd
"""


async def cleanup_expired_data(db: AsyncSession) -> dict:
    now = datetime.now(timezone.utc)
    cutoff_campaign = now - timedelta(days=RETENTION_CAMPAIGN_DAYS)
    cutoff_vishing = now - timedelta(days=RETENTION_VISHING_DAYS)
    cutoff_audit = now - timedelta(days=RETENTION_AUDIT_LOG_DAYS)

    stats = {}

    deleted_campaigns = await db.execute(
        select(m.Campaign).where(m.Campaign.created_at < cutoff_campaign)
    )
    campaigns = deleted_campaigns.scalars().all()
    for c in campaigns:
        await db.delete(c)
    stats["campaigns_expired"] = len(campaigns)

    deleted_vishing = await db.execute(
        select(m.VishingSession).where(m.VishingSession.created_at < cutoff_vishing)
    )
    sessions = deleted_vishing.scalars().all()
    for s in sessions:
        await db.delete(s)
    stats["vishing_sessions_expired"] = len(sessions)

    deleted_audit = await db.execute(
        select(m.AuditLog).where(m.AuditLog.created_at < cutoff_audit)
    )
    logs = deleted_audit.scalars().all()
    for l in logs:
        await db.delete(l)
    stats["audit_logs_expired"] = len(logs)

    await db.commit()
    logger.info("GDPR cleanup complete: %s", stats)
    return stats


async def handle_data_subject_access_request(
    email_hash: str,
    db: AsyncSession,
) -> dict:
    employee = await db.execute(
        select(m.Employee).where(m.Employee.email_hash == email_hash).limit(1)
    )
    employee = employee.scalar_one_or_none()
    if not employee:
        return {"found": False, "message": "No data found for this email hash"}

    campaigns = await db.execute(
        select(m.Campaign).where(m.Campaign.client_id == employee.client_id)
    )
    results = await db.execute(
        select(m.CampaignResult).where(m.CampaignResult.employee_id == employee.id)
    )
    vishing = await db.execute(
        select(m.VishingSession).where(m.VishingSession.employee_id == employee.id)
    )

    return {
        "found": True,
        "employee": {
            "id": str(employee.id),
            "email_hash": employee.email_hash,
            "role": employee.role,
            "department": employee.department,
            "created_at": employee.created_at.isoformat(),
        },
        "campaigns": [
            {
                "id": str(c.id),
                "name": c.name,
                "status": c.status.value,
                "created_at": c.created_at.isoformat(),
            }
            for c in campaigns.scalars().all()
            if c.client_id == employee.client_id
        ],
        "campaign_results": [
            {
                "id": str(r.id),
                "campaign_id": str(r.campaign_id),
                "email_opened": r.email_opened,
                "link_clicked": r.link_clicked,
                "credentials_submitted": r.credentials_submitted,
                "reported_phishing": r.reported_phishing,
                "training_completed": r.training_completed,
            }
            for r in results.scalars().all()
        ],
        "vishing_sessions": [
            {
                "id": str(s.id),
                "status": s.status,
                "call_duration": s.call_duration,
                "sensitive_info_disclosed": s.sensitive_info_disclosed,
                "created_at": s.created_at.isoformat(),
            }
            for s in vishing.scalars().all()
        ],
    }
