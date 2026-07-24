from datetime import datetime
from pydantic import BaseModel


class AuditLogOut(BaseModel):
    audit_id: str
    request_id: str
    workflow_step: str
    policy_result: str
    action_taken: str | None
    timestamp: datetime

    class Config:
        from_attributes = True


class CustomerContextOut(BaseModel):
    customer_id: str
    verification_status: str
    account_age_months: int
    card_status: str
    current_credit_limit: float

    class Config:
        from_attributes = True
