from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.service_request import ServiceRequest
from app.schemas.credit_limit import CreditLimitRequest, CreditLimitResponse
from app.security import verify_api_key
from app.services import policy_engine, audit_service

router = APIRouter(prefix="/credit-limit", tags=["Credit Limit"], dependencies=[Depends(verify_api_key)])


@router.post("/request", response_model=CreditLimitResponse)
def request_credit_limit_increase(
    payload: CreditLimitRequest,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    existing = db.execute(
        select(ServiceRequest).where(
            ServiceRequest.idempotency_key == idempotency_key,
            ServiceRequest.intent == "credit_limit_increase",
        )
    ).scalar_one_or_none()
    if existing:
        return CreditLimitResponse(
            request_id=existing.request_id, status=existing.status,
            approved=(existing.status == "completed"),
            policy_result="Duplicate request — returning original result",
            message="This request was already processed (idempotency key replay).",
        )

    try:
        # Row lock is the critical fix here: without it, two concurrent
        # increase requests can both read the same current_credit_limit
        # before either writes, and the second write silently overwrites
        # the first (lost update) instead of stacking correctly.
        customer = db.execute(
            select(Customer).where(Customer.customer_id == payload.customer_id).with_for_update()
        ).scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        request = ServiceRequest(
            customer_id=customer.customer_id, intent="credit_limit_increase",
            idempotency_key=idempotency_key,
            request_text=f"Requested increase of {payload.requested_increase}", status="pending",
        )
        db.add(request)
        db.flush()

        audit_service.log_step(db, request.request_id, "intent_classified",
                                "credit_limit_increase request received", flush_only=True)

        approved, reason = policy_engine.check_credit_limit_eligibility(customer, payload.requested_increase)
        audit_service.log_step(db, request.request_id, "policy_check", reason, flush_only=True)

        if approved:
            request.status = "completed"
            customer.current_credit_limit = float(customer.current_credit_limit) + payload.requested_increase
            audit_service.log_step(db, request.request_id, "action_execution", reason,
                                    action_taken="credit_limit_increased", flush_only=True)
            db.commit()
            return CreditLimitResponse(
                request_id=request.request_id, status="completed", approved=True,
                policy_result=reason, message=f"Credit limit increased by {payload.requested_increase}.",
            )

        request.status = "escalated"
        audit_service.log_step(db, request.request_id, "action_execution", reason,
                                action_taken="escalated", flush_only=True)
        db.commit()
        return CreditLimitResponse(
            request_id=request.request_id, status="escalated", approved=False,
            policy_result=reason, message="This request exceeds automatic approval limits. Escalating to a specialist.",
        )
    except Exception:
        db.rollback()
        raise
