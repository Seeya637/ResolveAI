from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.models.service_request import ServiceRequest
from app.schemas.fees import FeeReversalRequest, FeeReversalResponse
from app.security import verify_api_key
from app.services import policy_engine, audit_service

router = APIRouter(prefix="/fees", tags=["Fee Reversal"], dependencies=[Depends(verify_api_key)])


@router.post("/reversal", response_model=FeeReversalResponse)
def reverse_fee(
    payload: FeeReversalRequest,
    db: Session = Depends(get_db),
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
):
    # --- Idempotency check: same key + intent already processed? Return
    # the original outcome instead of re-running a financial action. ---
    existing = db.execute(
        select(ServiceRequest).where(
            ServiceRequest.idempotency_key == idempotency_key,
            ServiceRequest.intent == "fee_reversal",
        )
    ).scalar_one_or_none()
    if existing:
        return FeeReversalResponse(
            request_id=existing.request_id, status=existing.status,
            approved=(existing.status == "completed"),
            policy_result="Duplicate request — returning original result",
            message="This request was already processed (idempotency key replay).",
        )

    # --- Everything below is ONE atomic transaction: either the whole
    # sequence (request row, customer lock, policy check, audit rows,
    # action) commits together, or none of it does. ---
    try:
        # SELECT ... FOR UPDATE: locks this customer's row for the
        # duration of the transaction, so a second concurrent request for
        # the same customer blocks until this one commits or rolls back.
        # Prevents the lost-update race on shared customer state.
        customer = db.execute(
            select(Customer).where(Customer.customer_id == payload.customer_id).with_for_update()
        ).scalar_one_or_none()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        request = ServiceRequest(
            customer_id=customer.customer_id,
            intent="fee_reversal",
            idempotency_key=idempotency_key,
            request_text=payload.reason,
            status="pending",
        )
        db.add(request)
        db.flush()  # assigns request_id without ending the transaction

        audit_service.log_step(db, request.request_id, "intent_classified",
                                "fee_reversal request received", flush_only=True)

        prior_reversals = policy_engine.count_recent_fee_reversals(db, customer.customer_id)
        approved, reason = policy_engine.check_fee_reversal_eligibility(
            customer=customer,
            fee_amount=payload.fee_amount,
            days_since_charge=payload.days_since_charge,
            prior_reversals_90d=prior_reversals,
        )
        audit_service.log_step(db, request.request_id, "policy_check", reason, flush_only=True)

        if approved:
            request.status = "completed"
            audit_service.log_step(db, request.request_id, "action_execution", reason,
                                    action_taken="fee_reversed", flush_only=True)
            db.commit()
            return FeeReversalResponse(
                request_id=request.request_id, status="completed", approved=True,
                policy_result=reason, message=f"Fee of {payload.fee_amount} reversed successfully.",
            )

        request.status = "rejected"
        audit_service.log_step(db, request.request_id, "action_execution", reason,
                                action_taken="none", flush_only=True)
        db.commit()
        return FeeReversalResponse(
            request_id=request.request_id, status="rejected", approved=False,
            policy_result=reason, message="This fee could not be auto-reversed. It will be reviewed by a specialist.",
        )
    except Exception:
        db.rollback()
        raise
