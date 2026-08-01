import uuid
import logging
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import CampaignTemplate

logger = logging.getLogger(__name__)


async def create_template(
    db: AsyncSession,
    client_id: uuid.UUID,
    name: str,
    description: str | None = None,
    difficulty: str = "medium",
    scenario_weights: dict[str, float] | None = None,
    page_html: str | None = None,
) -> CampaignTemplate:
    tpl = CampaignTemplate(
        client_id=client_id,
        name=name,
        description=description,
        difficulty=difficulty,
        scenario_weights=scenario_weights,
        page_html=page_html,
    )
    db.add(tpl)
    await db.flush()
    return tpl


async def get_template(db: AsyncSession, template_id: uuid.UUID) -> CampaignTemplate | None:
    return await db.get(CampaignTemplate, template_id)


async def list_templates(
    db: AsyncSession,
    client_id: uuid.UUID | None = None,
    active_only: bool = True,
) -> list[CampaignTemplate]:
    stmt = select(CampaignTemplate)
    if client_id:
        stmt = stmt.where(CampaignTemplate.client_id == client_id)
    if active_only:
        stmt = stmt.where(CampaignTemplate.is_active == True)
    stmt = stmt.order_by(CampaignTemplate.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def update_template(
    db: AsyncSession,
    template_id: uuid.UUID,
    **kwargs: Any,
) -> CampaignTemplate | None:
    tpl = await db.get(CampaignTemplate, template_id)
    if not tpl:
        return None
    for key, value in kwargs.items():
        if value is not None and hasattr(tpl, key):
            setattr(tpl, key, value)
    tpl.updated_at = datetime.utcnow()
    await db.flush()
    return tpl


async def delete_template(db: AsyncSession, template_id: uuid.UUID) -> bool:
    tpl = await db.get(CampaignTemplate, template_id)
    if not tpl:
        return False
    tpl.is_active = False
    await db.flush()
    return True
