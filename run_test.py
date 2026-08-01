"""One-step test: sends 4 phishing emails via Gophish with different scenarios.

Usage:
    python run_test.py

Prerequisites:
    - Gophish running (start_gophish.ps1)
    - .env configured with GMAIL_USER, GMAIL_APP_PASSWORD
    - Target emails in DB (change with: python update_emails.py --old @gmail.com --new @yourdomain.com)
"""
import asyncio, uuid, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
os.chdir(os.path.dirname(os.path.abspath(__file__)))

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
        import random
        from sqlalchemy import delete

        existing = await db.execute(select(Employee).limit(1))
        existing_emp = existing.scalar_one_or_none()
        if existing_emp and existing_emp.email_hash and "@" in existing_emp.email_hash:
            local, domain = existing_emp.email_hash.rsplit("@", 1)
            base_local = local.split("+")[0]
            email_domain = f"@{domain}"
        else:
            base_local = "rorshopping"
            email_domain = "@gmail.com"

        company_names = [
            "Müller & Söhne GmbH", "Schmidt Metallbau AG", "Bayerische Industrie GmbH",
            "Norddeutsche Handels Union", "Thüringer Präzisionstechnik", "Süwag Energie AG",
            "Rheinische Versicherung KG", "Hamburger Hafen Logistik GmbH", "Dresdner Feinmechanik",
            "Kölner Digital Solutions AG",
        ]
        company_name = random.choice(company_names)
        await db.execute(delete(Client).where(Client.company_name == company_name))
        client = Client(
            company_name=company_name,
            contact_email="admin@test.de",
            contact_name="Admin",
            industry="Technology",
            employee_count=4,
            country="DE",
            campaigns_per_year=25,
        )
        db.add(client)
        await db.flush()

        employees = [
            Employee(client_id=client.id, email_hash=f"{base_local}+anja{email_domain}", name_hash="Anja Schneider",
                     role="CFO", department="Finance", group=EmployeeGroup.finance),
            Employee(client_id=client.id, email_hash=f"{base_local}+felix{email_domain}", name_hash="Felix Wagner",
                     role="Engineer", department="Engineering", group=EmployeeGroup.engineering),
            Employee(client_id=client.id, email_hash=f"{base_local}+lena{email_domain}", name_hash="Lena Hoffmann",
                     role="HR Manager", department="HR", group=EmployeeGroup.hr),
            Employee(client_id=client.id, email_hash=f"{base_local}+klaus{email_domain}", name_hash="Klaus Weber",
                     role="IT Admin", department="IT", group=EmployeeGroup.it_management),
        ]
        for e in employees:
            db.add(e)
        await db.flush()

        campaign = Campaign(
            client_id=client.id,
            name=f"4-Email {datetime.utcnow().strftime('%H:%M')}",
            status=CampaignStatus.draft,
            difficulty="easy",
        )
        db.add(campaign)
        await db.commit()
        await db.refresh(campaign)

        print(f"Client: {client.company_name}")
        print(f"Campaign: {campaign.id}")
        for e in employees:
            print(f"  {e.id}: {e.email_hash} ({e.group.value})")

    plan = {
        "employee_assignments": [
            {"employee_id": str(employees[0].id), "group": "finance", "scenario_type": "ceo_fraud"},
            {"employee_id": str(employees[1].id), "group": "engineering", "scenario_type": "cloud_notification"},
            {"employee_id": str(employees[2].id), "group": "hr", "scenario_type": "dropbox_share"},
            {"employee_id": str(employees[3].id), "group": "it_management", "scenario_type": "credential_harvest"},
        ],
    }

    agent = ExecutionAgent()
    success = await agent.execute_campaign(campaign.id, plan)
    print(f"\nResult: {'Success' if success else 'Failed'}")

    async with async_session() as db:
        c = (await db.execute(select(Campaign).where(Campaign.id == campaign.id))).scalar_one()
        print(f"Gophish campaign IDs: {c.gophish_campaign_id}")
        print(f"Status: {c.status.value}")

asyncio.run(main())
