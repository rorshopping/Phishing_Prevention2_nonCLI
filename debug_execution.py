import asyncio, uuid, os, sys
sys.path.insert(0, "C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI")
os.environ["PYTHONPATH"] = "C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI"
os.chdir("C:\\Users\\Richard\\Documents\\Projects\\Phishing_Prevention2_nonCLI")

import logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s %(levelname)-8s %(name)s %(message)s")

async def main():
    from src.agents.execution_agent import ExecutionAgent
    from src.database.session import async_session
    from src.database.models import Campaign, CampaignStatus, Client, Employee
    from sqlalchemy import select

    # Find the most recent campaign
    async with async_session() as db:
        result = await db.execute(select(Campaign).order_by(Campaign.created_at.desc()))
        campaign = result.scalars().first()
        if not campaign:
            print("No campaign found")
            return
        print(f"Found campaign: id={campaign.id} status={campaign.status} client_id={campaign.client_id}")

    # Execute via ExecutionAgent
    agent = ExecutionAgent()
    success = await agent.execute_campaign(campaign.id)
    print(f"\nExecution result: {success}")

    # Check updated status
    async with async_session() as db:
        result = await db.execute(select(Campaign).where(Campaign.id == campaign.id))
        updated = result.scalar_one()
        print(f"Updated campaign: status={updated.status} gophish_group_id={updated.gophish_group_id} gophish_template_id={updated.gophish_template_id} gophish_page_id={updated.gophish_page_id} gophish_campaign_id={updated.gophish_campaign_id}")

    # Check audit log
    async with async_session() as db:
        from src.database.models import AuditLog
        result = await db.execute(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(5))
        for log in result.scalars():
            print(f"AuditLog: action={log.action} details={log.details}")

asyncio.run(main())
