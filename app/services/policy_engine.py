"""
Deterministic eligibility rules.

This is the single most important file in the backend. The AI/orchestration
layer (LangGraph) is only ever allowed to ask "is this customer eligible for
this action?" — it never decides the answer itself. Every function here is
plain, testable Python with no dependency on any LLM, so it can be unit
tested and audited independently of the AI layer.

Every function returns (approved: bool, reason: str). The reason string is
written verbatim into AuditLog.policy_result, so the audit trail always
shows *why* a decision was made in human-readable form.
"""
from datetime import datetime, timedelta, timezone

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from app.config import settings
from app.models.customer import Customer
from app.models.service_request import ServiceRequest


def count_recent_fee_reversals(db: Session, customer_id: str, days: int = 90) -> int:
    """
    Replaces the old hardcoded `prior_reversals_90d=0`. Queries actual
    completed fee_reversal requests for this customer in the lookback
    window. This is the real thing the pitch claims exists — a policy
    engine cannot be called "deterministic" if one of its own inputs was
    a constant.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    stmt = select(func.count()).select_from(ServiceRequest).where(
        ServiceRequest.customer_id == customer_id,
        ServiceRequest.intent == "fee_reversal",
        ServiceRequest.status == "completed",
        ServiceRequest.created_at >= cutoff,
    )
    return db.execute(stmt).scalar_one()


def check_fee_reversal_eligibility(
    customer: Customer,
    fee_amount: float,
    days_since_charge: int,
    prior_reversals_90d: int,
) -> tuple[bool, str]:
    if prior_reversals_90d > 0:
        return False, "Prior reversal already granted within the last 90 days"
    if fee_amount > settings.fee_reversal_max_amount:
        return False, f"Fee amount exceeds auto-approval threshold of {settings.fee_reversal_max_amount}"
    if customer.account_age_months < settings.fee_reversal_min_account_age_months:
        return False, f"Account age below minimum of {settings.fee_reversal_min_account_age_months} months for auto-approval"
    if days_since_charge > 60:
        return False, "Charge is older than the 60-day auto-review window"
    return True, "Eligible for automatic reversal"


def check_card_replacement_eligibility(customer: Customer, reason: str) -> tuple[bool, str]:
    reason_normalized = reason.strip().lower()
    if reason_normalized in {"lost", "stolen"}:
        return False, "Lost/stolen cards require identity re-verification before replacement"
    if customer.verification_status != "verified":
        return False, "Customer identity not verified"
    if customer.card_status == "blocked":
        return False, "Card is blocked pending investigation; cannot auto-replace"
    return True, "Eligible for automatic replacement"


def check_credit_limit_eligibility(customer: Customer, requested_increase: float) -> tuple[bool, str]:
    if requested_increase > settings.credit_limit_max_auto_increase:
        return False, f"Requested increase exceeds auto-approval cap of {settings.credit_limit_max_auto_increase}"
    if customer.account_age_months < settings.credit_limit_min_account_age_months:
        return False, f"Account age below minimum of {settings.credit_limit_min_account_age_months} months for auto-approval"
    if customer.verification_status != "verified":
        return False, "Customer identity not verified"
    return True, "Eligible for automatic credit-limit increase"
