from pydantic import BaseModel


class PreferenceUpdate(BaseModel):
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = False


class PreferenceResponse(PreferenceUpdate):
    user_id: str

    class Config:
        from_attributes = True
