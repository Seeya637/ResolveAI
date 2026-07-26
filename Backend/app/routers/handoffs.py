from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.handoff import HumanHandoff
from app.schemas.handoffs import HandoffCreate, HandoffOut
from app.security import verify_api_key
from app.services import audit_service

router = APIRouter(prefix="/handoffs", tags=["Human Handoffs"], dependencies=[Depends(verify_api_key)])


@router.post("", response_model=HandoffOut)
def create_handoff(payload: HandoffCreate, db: Session = Depends(get_db)):
    """
    Called whenever the AI layer or the policy engine decides a request
    can't be auto-resolved. Carries the AI's summary of the conversation
    so the human agent never asks the customer to repeat themselves.
    """
    handoff = HumanHandoff(
        request_id=payload.request_id,
        escalation_reason=payload.escalation_reason,
        ai_summary=payload.ai_summary,
        status="pending",
    )
    db.add(handoff)
    db.commit()
    db.refresh(handoff)

    audit_service.log_step(
        db, payload.request_id, "human_handoff_created",
        payload.escalation_reason, action_taken="escalated",
    )
    return handoff
