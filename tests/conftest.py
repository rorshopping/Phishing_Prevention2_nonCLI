import uuid
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from src.database.models import Client, Employee, EmployeeGroup, Campaign, CampaignStatus
from src.database.session import Base


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine("sqlite+aiosqlite://", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine) -> AsyncGenerator[AsyncSession, None]:
    async with db_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)
        async with AsyncSession(bind=conn, expire_on_commit=False) as session:
            yield session


@pytest_asyncio.fixture
async def patched_db_session(db_engine):
    import src.database.session as db_module
    from src.agents import execution_agent, monitoring_agent, orchestrator

    async with db_engine.connect() as conn:
        await conn.run_sync(Base.metadata.create_all)

        def session_factory():
            return AsyncSession(bind=conn, expire_on_commit=False)

        originals = {
            "db_session": db_module.async_session,
            "execution_agent": execution_agent.async_session,
            "monitoring_agent": monitoring_agent.async_session,
            "orchestrator": orchestrator.async_session,
        }

        db_module.async_session = session_factory
        execution_agent.async_session = session_factory
        monitoring_agent.async_session = session_factory
        orchestrator.async_session = session_factory

        yield session_factory

        db_module.async_session = originals["db_session"]
        execution_agent.async_session = originals["execution_agent"]
        monitoring_agent.async_session = originals["monitoring_agent"]
        orchestrator.async_session = originals["orchestrator"]


@pytest_asyncio.fixture
async def sample_client(db_session) -> Client:
    client = Client(
        id=uuid.uuid4(),
        company_name="Dresdner Feinmechanik GmbH",
        contact_email="admin@test.de",
        industry="Technology",
        employee_count=50,
        country="DE",
        campaigns_per_year=25,
    )
    db_session.add(client)
    await db_session.commit()
    return client


@pytest_asyncio.fixture
async def sample_employees(sample_client, db_session) -> list[Employee]:
    employees = [
        Employee(
            id=uuid.uuid4(), client_id=sample_client.id,
            email_hash="ceo@test.de", name="Dr. Klaus Schmidt",
            role="CEO", department="Executive",
            group=EmployeeGroup.executive,
        ),
        Employee(
            id=uuid.uuid4(), client_id=sample_client.id,
            email_hash="cfo@test.de", name="Anna Weber",
            role="CFO", department="Finance",
            group=EmployeeGroup.finance,
        ),
        Employee(
            id=uuid.uuid4(), client_id=sample_client.id,
            email_hash="eng@test.de", name="Lukas Fischer",
            role="Engineer", department="Engineering",
            group=EmployeeGroup.engineering,
        ),
        Employee(
            id=uuid.uuid4(), client_id=sample_client.id,
            email_hash="hr@test.de", name="Sarah Klein",
            role="HR Lead", department="HR",
            group=EmployeeGroup.hr,
        ),
    ]
    for e in employees:
        db_session.add(e)
    await db_session.commit()
    return employees


@pytest_asyncio.fixture
async def sample_campaign(sample_client, db_session) -> Campaign:
    campaign = Campaign(
        id=uuid.uuid4(),
        client_id=sample_client.id,
        name="Test Campaign",
        status=CampaignStatus.draft,
        difficulty="easy",
    )
    db_session.add(campaign)
    await db_session.commit()
    return campaign
