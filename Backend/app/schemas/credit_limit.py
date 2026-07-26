from pydantic import BaseModel, Field


class CreditLimitRequest(BaseModel):
    customer_id: str = Field(..., examples=["C1024"])
    requested_increase: float = Field(..., gt=0, examples=[10000.00])


class CreditLimitResponse(BaseModel):
    request_id: str
    status: str
    approved: bool
    policy_result: str
    message: str
