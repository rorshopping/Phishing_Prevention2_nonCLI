import asyncio, uuid, os, sys
sys.path.insert(0, "C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI")
os.environ["PYTHONPATH"] = "C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI"
os.chdir("C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI")

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s %(message)s")

async def main():
    from src.database.session import async_session, engine, Base
    from src.database.models import Client, Employee, EmployeeGroup, Campaign, CampaignStatus, AuditLog
    from src.agents.execution_agent import ExecutionAgent
    from sqlalchemy import select
    from datetime import datetime

    # Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Create client
        client = Client(
            company_name="Thüringer Präzisionstechnik GmbH",
            contact_email="admin@testcompany.de",
            contact_name="Test Admin",
            industry="Technology",
            employee_count=1,
            country="DE",
            campaigns_per_year=25,
        )
        db.add(client)
        await db.flush()

        # Create employee with user's email
        emp = Employee(
            client_id=client.id,
            email_hash="rorshopping@gmail.com",
            name_hash="Richard Or",
            role="Developer",
            department="Engineering",
            group=EmployeeGroup.engineering,
        )
        db.add(emp)
        await db.flush()

        # Create campaign
        campaign = Campaign(
            client_id=client.id,
            name=f"Test {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            status=CampaignStatus.draft,
            difficulty="easy",
        )
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)

        print(f"Client ID: {client.id}")
        print(f"Employee ID: {emp.id}")
        print(f"Campaign ID: {campaign.id}")

    # Execute via ExecutionAgent
    agent = ExecutionAgent()
    print("\n--- Running ExecutionAgent ---")
    success = await agent.execute_campaign(campaign.id)
    print(f"Execution result: {success}")

    # Check updated campaign
    async with async_session() as db:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign.id))
        updated = result.scalar_one()
        print(f"\nUpdated campaign:")
        print(f"  status: {updated.status}")
        print(f"  gophish_campaign_id: {updated.gophish_campaign_id}")
        print(f"  gophish_group_id: {updated.gophish_group_id}")
        print(f"  gophish_template_id: {updated.gophish_template_id}")
        print(f"  gophish_page_id: {updated.gophish_page_id}")

        # Check results
        from src.database.models import CampaignResult
        result = await db.execute(select(CampaignResult).where(CampaignResult.campaign_id == campaign.id))
        results = result.scalars().all()
        print(f"\nResults count: {len(results)}")

        # Check audit logs
        result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(5))
        print(f"\nAudit logs:")
        for log in result.scalars():
            print(f"  {log.action}: {log.details}")

    print("\n=== DONE ===")

asyncio.run(main())
