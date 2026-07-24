from pydantic import BaseModel, Field


class SessionUpdateRequest(BaseModel):
    last_intent: str | None = Field(None, examples=["fee_reversal"])
    entities: dict | None = Field(None, examples=[{"fee_amount": 199.0, "card_last4": "4321"}])
    history_append: str | None = Field(None, examples=["Customer: I was charged twice for the annual fee"])


class SessionOut(BaseModel):
    last_intent: str | None
    entities: dict
    history: list[str]
