from pydantic import BaseModel, Field


class CardReplacementRequest(BaseModel):
    customer_id: str = Field(..., examples=["C1024"])
    reason: str = Field(..., examples=["damaged card"])  # damaged | lost | stolen | other


class CardReplacementResponse(BaseModel):
    request_id: str
    status: str
    approved: bool
    policy_result: str
    message: str
