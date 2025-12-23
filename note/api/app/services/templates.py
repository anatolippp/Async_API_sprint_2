from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Template
from ..schemas.template import TemplateCreate


async def create_template(db: AsyncSession, data: TemplateCreate) -> Template:
    template = Template(**data.model_dump())
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def list_templates(db: AsyncSession) -> list[Template]:
    result = await db.execute(select(Template))
    return result.scalars().all()
