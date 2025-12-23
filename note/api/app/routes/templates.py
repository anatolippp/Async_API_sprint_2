from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas.template import TemplateCreate, TemplateResponse
from ..services.templates import create_template, list_templates

router = APIRouter(prefix="/api/v1/templates", tags=["templates"])


@router.post("", response_model=TemplateResponse)
async def create_template_view(data: TemplateCreate, db: AsyncSession = Depends(get_db)):
    template = await create_template(db, data)
    return TemplateResponse.model_validate(template)


@router.get("", response_model=List[TemplateResponse])
async def list_templates_view(db: AsyncSession = Depends(get_db)):
    templates = await list_templates(db)
    return [TemplateResponse.model_validate(item) for item in templates]
