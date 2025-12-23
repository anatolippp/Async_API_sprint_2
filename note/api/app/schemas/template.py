from pydantic import BaseModel


class TemplateCreate(BaseModel):
    name: str
    subject_template: str
    body_template: str
    channel: str = "email"


class TemplateResponse(TemplateCreate):
    id: int

    class Config:
        from_attributes = True
