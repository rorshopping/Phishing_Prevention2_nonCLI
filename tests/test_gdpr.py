from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
import pytest_asyncio

from src.utils.gdpr import hash_pii, anonymize_employee, generate_data_processing_agreement
from src.database.models import Client


SAMPLE_SALT = "a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6"


def test_hash_pii_consistent(monkeypatch):
    monkeypatch.setattr("src.utils.gdpr.SALT", SAMPLE_SALT.encode())
    h1 = hash_pii("rorshopping@gmail.com")
    h2 = hash_pii("rorshopping@gmail.com")
    assert h1 == h2


def test_hash_pii_different_inputs(monkeypatch):
    monkeypatch.setattr("src.utils.gdpr.SALT", SAMPLE_SALT.encode())
    h1 = hash_pii("alice@example.com")
    h2 = hash_pii("bob@example.com")
    assert h1 != h2


def test_hash_pii_salt_changes_hash(monkeypatch):
    monkeypatch.setattr("src.utils.gdpr.SALT", b"salt_a")
    h1 = hash_pii("test@example.com")
    monkeypatch.setattr("src.utils.gdpr.SALT", b"salt_b")
    h2 = hash_pii("test@example.com")
    assert h1 != h2


def test_anonymize_employee_hashes_pii(monkeypatch):
    monkeypatch.setattr("src.utils.gdpr.SALT", SAMPLE_SALT.encode())
    data = {
        "email_hash": "user@example.com",
        "name_hash": "John Doe",
        "role": "CEO",
        "department": "Executive",
        "linkedin_url": "https://linkedin.com/in/johndoe",
    }
    result = anonymize_employee(data)
    assert result["email_hash"] != data["email_hash"]
    assert result["name_hash"] != data["name_hash"]
    assert result["linkedin_url"] != data["linkedin_url"]
    assert result["role"] == "CEO"
    assert result["department"] == "Executive"


def test_anonymize_employee_skips_missing_fields():
    data = {"role": "Engineer", "department": "Engineering"}
    result = anonymize_employee(data)
    assert result["role"] == "Engineer"
    assert result["department"] == "Engineering"


def test_anonymize_employee_anonymizes_public_data(monkeypatch):
    monkeypatch.setattr("src.utils.gdpr.SALT", SAMPLE_SALT.encode())
    data = {
        "email_hash": "e@e.com",
        "public_data": {"linkedin": "url", "recent_news": "news"},
    }
    result = anonymize_employee(data)
    assert result["public_data"] == {"anonymized": True}


def test_generate_data_processing_agreement_contains_expected_sections():
    client = Client(company_name="TestCorp GmbH")
    dpa = generate_data_processing_agreement(client)
    assert "DATA PROCESSING AGREEMENT" in dpa
    assert "TestCorp GmbH" in dpa
    assert "PhishGuard Ltd" in dpa
    assert "GDPR" in dpa
    assert "365 days" in dpa
    assert "180 days" in dpa


@pytest.mark.asyncio
async def test_cleanup_expired_data(db_session, db_engine):
    from datetime import datetime
    from src.database.models import Campaign, CampaignStatus, VishingSession, AuditLog

    old_date = datetime.now(timezone.utc) - timedelta(days=400)
    recent_date = datetime.now(timezone.utc) - timedelta(days=10)

    client = Client(id=uuid4(), company_name="Cleanup Corp", contact_email="c@c.com")
    db_session.add(client)
    await db_session.flush()

    old_campaign = Campaign(
        id=uuid4(), client_id=client.id, name="Old Campaign",
        status=CampaignStatus.completed, created_at=old_date,
    )
    recent_campaign = Campaign(
        id=uuid4(), client_id=client.id, name="Recent Campaign",
        status=CampaignStatus.completed, created_at=recent_date,
    )
    db_session.add_all([old_campaign, recent_campaign])
    await db_session.commit()

    from src.utils.gdpr import cleanup_expired_data
    stats = await cleanup_expired_data(db_session)

    assert stats["campaigns_expired"] >= 1
