import uuid
from datetime import datetime
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.session import get_db
from src.database import models as m
from src.engine.template_engine import (
    create_template, get_template, list_templates,
    update_template, delete_template,
)

router = APIRouter(prefix="/templates", tags=["templates"])


class TemplateCreate(BaseModel):
    client_id: uuid.UUID
    name: str
    description: Optional[str] = None
    difficulty: str = "medium"
    scenario_weights: Optional[dict[str, float]] = None
    page_html: Optional[str] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    difficulty: Optional[str] = None
    scenario_weights: Optional[dict[str, float]] = None
    page_html: Optional[str] = None


class TemplateResponse(BaseModel):
    id: uuid.UUID
    client_id: uuid.UUID
    name: str
    description: Optional[str]
    difficulty: str
    scenario_weights: Optional[dict[str, float]]
    page_html: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


@router.post("", response_model=TemplateResponse, status_code=201)
async def create_template_endpoint(body: TemplateCreate, db: AsyncSession = Depends(get_db)):
    client = await db.get(m.Client, body.client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    tpl = await create_template(
        db=db,
        client_id=body.client_id,
        name=body.name,
        description=body.description,
        difficulty=body.difficulty,
        scenario_weights=body.scenario_weights,
        page_html=body.page_html,
    )
    await db.commit()
    await db.refresh(tpl)
    return tpl


@router.get("", response_model=list[TemplateResponse])
async def list_templates_endpoint(
    client_id: uuid.UUID = Query(None),
    db: AsyncSession = Depends(get_db),
):
    return await list_templates(db, client_id=client_id)


@router.get("/{template_id}", response_model=TemplateResponse)
async def get_template_endpoint(template_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    tpl = await get_template(db, template_id)
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    return tpl


@router.put("/{template_id}", response_model=TemplateResponse)
async def update_template_endpoint(
    template_id: uuid.UUID,
    body: TemplateUpdate,
    db: AsyncSession = Depends(get_db),
):
    tpl = await update_template(db, template_id, **body.model_dump(exclude_unset=True))
    if not tpl:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.commit()
    await db.refresh(tpl)
    return tpl


@router.delete("/{template_id}")
async def delete_template_endpoint(template_id: uuid.UUID, db: AsyncSession = Depends(get_db)):
    ok = await delete_template(db, template_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Template not found")
    await db.commit()
    return {"status": "deleted"}
