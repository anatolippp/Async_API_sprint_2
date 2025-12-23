from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Campaign
from ..schemas.campaign import CampaignCreate


async def create_campaign(db: AsyncSession, data: CampaignCreate) -> Campaign:
    campaign = Campaign(**data.model_dump())
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


async def list_campaigns(db: AsyncSession) -> list[Campaign]:
    result = await db.execute(select(Campaign))
    return result.scalars().all()
