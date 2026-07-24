from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.service_request import ServiceRequest
from app.schemas.cards import CardReplacementRequest, CardReplacementResponse
from app.security import verify_api_key
from app.services import policy_engine, audit_service

router = APIRouter(prefix="/cards", tags=["Card Replacement"], dependencies=[Depends(verify_api_key)])


@router.post("/replacement", response_model=CardReplacementResponse)
def replace_card(
    payload: CardReplacementRequest,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    existing = db.execute(
        select(ServiceRequest).where(
            ServiceRequest.idempotency_key == idempotency_key,
            ServiceRequest.intent == "card_replacement",
        )
    ).scalar_one_or_none()
    if existing:
        return CardReplacementResponse(
            request_id=existing.request_id, status=existing.status,
            approved=(existing.status == "completed"),
            policy_result="Duplicate request — returning original result",
            message="This request was already processed (idempotency key replay).",
        )

    try:
        customer = db.execute(
            select(Customer).where(Customer.customer_id == payload.customer_id).with_for_update()
        ).scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        request = ServiceRequest(
            customer_id=customer.customer_id, intent="card_replacement",
            idempotency_key=idempotency_key, request_text=payload.reason, status="pending",
        )
        db.add(request)
        db.flush()

        audit_service.log_step(db, request.request_id, "intent_classified",
                                "card_replacement request received", flush_only=True)

        approved, reason = policy_engine.check_card_replacement_eligibility(customer, payload.reason)
        audit_service.log_step(db, request.request_id, "policy_check", reason, flush_only=True)

        if approved:
            request.status = "completed"
            customer.card_status = "replacement_ordered"
            audit_service.log_step(db, request.request_id, "action_execution", reason,
                                    action_taken="card_replacement_ordered", flush_only=True)
            db.commit()
            return CardReplacementResponse(
                request_id=request.request_id, status="completed", approved=True,
                policy_result=reason, message="Replacement card ordered. It will arrive within 5-7 business days.",
            )

        request.status = "escalated"
        audit_service.log_step(db, request.request_id, "action_execution", reason,
                                action_taken="escalated", flush_only=True)
        db.commit()
        return CardReplacementResponse(
            request_id=request.request_id, status="escalated", approved=False,
            policy_result=reason, message="This request needs identity verification. Escalating to a specialist.",
        )
    except Exception:
        db.rollback()
        raise
