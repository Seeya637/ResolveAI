import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, func, UniqueConstraint

from app.database import Base


def generate_request_id() -> str:
    return f"SR-{uuid.uuid4().hex[:8].upper()}"


class ServiceRequest(Base):
    """
    One row per customer-facing servicing request (fee reversal, card
    replacement, credit-limit increase). status moves through:
    pending -> completed | rejected | escalated

    idempotency_key + intent is unique: if the same caller retries the
    same logical request (network timeout, AI-layer retry, double-tap on
    the frontend), the second call returns the original result instead
    of re-running the financial action. This is what prevents a retry
    from silently reversing a fee twice or increasing a limit twice.
    """
    __tablename__ = "service_requests"
    __table_args__ = (UniqueConstraint("idempotency_key", "intent", name="uq_idempotency_per_intent"),)

    request_id = Column(String, primary_key=True, default=generate_request_id)
    customer_id = Column(String, ForeignKey("customers.customer_id"), nullable=False, index=True)
    intent = Column(String, nullable=False)  # fee_reversal | card_replacement | credit_limit_increase
    idempotency_key = Column(String, nullable=False, index=True)
    request_text = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
