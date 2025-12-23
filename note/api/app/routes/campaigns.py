from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..schemas.campaign import CampaignCreate, CampaignResponse
from ..services.campaigns import create_campaign, list_campaigns

router = APIRouter(prefix="/api/v1/campaigns", tags=["campaigns"])


@router.post("", response_model=CampaignResponse)
async def create_campaign_view(data: CampaignCreate, db: AsyncSession = Depends(get_db)):
    campaign = await create_campaign(db, data)
    return CampaignResponse.model_validate(campaign)


@router.get("", response_model=List[CampaignResponse])
async def list_campaigns_view(db: AsyncSession = Depends(get_db)):
    campaigns = await list_campaigns(db)
    return [CampaignResponse.model_validate(item) for item in campaigns]
