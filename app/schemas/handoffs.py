from datetime import datetime
from pydantic import BaseModel, Field


class HandoffCreate(BaseModel):
    request_id: str = Field(..., examples=["SR-A1B2C3D4"])
    escalation_reason: str = Field(..., examples=["Requested limit exceeds automated approval threshold"])
    ai_summary: str | None = Field(None, examples=["Customer requested a 25,000 limit increase; account age 8 months."])


class HandoffOut(BaseModel):
    handoff_id: str
    request_id: str
    escalation_reason: str
    ai_summary: str | None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
