from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class CampaignCreate(BaseModel):
    name: str
    template_id: int
    scheduled_at: Optional[datetime] = None
    repeat_cron: Optional[str] = None
    audience: Optional[str] = None


class CampaignResponse(CampaignCreate):
    id: int

    class Config:
        from_attributes = True
