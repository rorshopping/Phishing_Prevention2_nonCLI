import asyncio, uuid, os, sys
sys.path.insert(0, "C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI")
os.environ["PYTHONPATH"] = "C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI"
os.chdir("C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI")

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-8s %(name)s %(message)s")

async def main():
    from src.database.session import async_session, engine, Base
    from src.database.models import Client, Employee, EmployeeGroup, Campaign, CampaignStatus, CampaignResult
    from src.agents.execution_agent import ExecutionAgent
    from sqlalchemy import select
    from datetime import datetime

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        client = Client(
            company_name=f"Schmidt & Söhne GmbH {uuid.uuid4().hex[:6]}",
            contact_email="admin@testcompany.de",
            contact_name="Test Admin",
            industry="Technology",
            employee_count=1,
            country="DE",
            campaigns_per_year=25,
        )
        db.add(client)
        await db.flush()

        employees_data = [
            Employee(
                client_id=client.id,
                email_hash="rorshopping+anja@gmail.com",
                name="Anja Schneider",
                name_hash="hashed_alice",
                role="CFO",
                department="Finance",
                group=EmployeeGroup.finance,
            ),
            Employee(
                client_id=client.id,
                email_hash="rorshopping+felix@gmail.com",
                name="Felix Wagner",
                name_hash="hashed_bob",
                role="Engineer",
                department="Engineering",
                group=EmployeeGroup.engineering,
            ),
            Employee(
                client_id=client.id,
                email_hash="rorshopping+lena@gmail.com",
                name="Lena Hoffmann",
                name_hash="hashed_carol",
                role="HR Manager",
                department="Human Resources",
                group=EmployeeGroup.hr,
            ),
        ]
        for emp in employees_data:
            db.add(emp)
        await db.flush()

        campaign = Campaign(
            client_id=client.id,
            name=f"3-Email Test {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}",
            status=CampaignStatus.draft,
            difficulty="easy",
        )
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)
        for emp in employees_data:
            await db.refresh(emp)

        print(f"Client ID: {client.id}")
        print(f"Campaign ID: {campaign.id}")
        for emp in employees_data:
            print(f"  Employee {emp.id}: {emp.email_hash} ({emp.group.value})")

    plan = {
        "client_id": str(client.id),
        "name": f"TestCompany GmbH - {datetime.utcnow().strftime('%Y-%m-%d')}",
        "difficulty": "easy",
        "monthly_budget": 2,
        "industry_context": {"industry": "Technology", "country": "DE", "employee_count": 3, "recent_threats": []},
        "llm_strategy": {"difficulty": "easy", "scenario_weights": {}, "rationale": "test"},
        "employee_assignments": [
            {"employee_id": str(employees_data[0].id), "group": "finance", "scenario_type": "ceo_fraud"},
            {"employee_id": str(employees_data[1].id), "group": "engineering", "scenario_type": "cloud_notification"},
            {"employee_id": str(employees_data[2].id), "group": "hr", "scenario_type": "dropbox_share"},
        ],
    }

    agent = ExecutionAgent()
    print("\n--- Running ExecutionAgent with 3 scenarios ---")
    success = await agent.execute_campaign(campaign.id, plan)
    print(f"Execution result: {success}")

    async with async_session() as db:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign.id))
        updated = result.scalar_one()
        print(f"\nUpdated campaign:")
        print(f"  status: {updated.status}")
        print(f"  gophish_campaign_id: {updated.gophish_campaign_id}")
        print(f"  gophish_group_id: {updated.gophish_group_id}")
        print(f"  gophish_template_id: {updated.gophish_template_id}")
        print(f"  gophish_page_id: {updated.gophish_page_id}")

        result = await db.execute(select(CampaignResult).where(CampaignResult.campaign_id == campaign.id))
        results = result.scalars().all()
        print(f"\nResults count: {len(results)}")

    print("\n=== DONE ===")

asyncio.run(main())
