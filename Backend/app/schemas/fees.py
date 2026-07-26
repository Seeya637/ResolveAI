from pydantic import BaseModel, Field


class FeeReversalRequest(BaseModel):
    customer_id: str = Field(..., examples=["C1024"])
    fee_id: str = Field(..., examples=["FEE-8831"])
    fee_amount: float = Field(..., gt=0, examples=[199.00])
    days_since_charge: int = Field(..., ge=0, examples=[3])
    reason: str = Field(..., examples=["duplicate charge"])


class FeeReversalResponse(BaseModel):
    request_id: str
    status: str          # completed | rejected | escalated
    approved: bool
    policy_result: str
    message: str
