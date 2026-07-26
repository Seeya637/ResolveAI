import uuid

from sqlalchemy import Column, String, DateTime, Integer, ForeignKey, func

from app.database import Base


def generate_audit_id() -> str:
    return f"AUD-{uuid.uuid4().hex[:8].upper()}"


class AuditLog(Base):
    """
    Append-only, hash-chained log of every workflow step.

    `seq` is a plain autoincrement integer used ONLY to establish true
    insertion order within a transaction — timestamp alone is not
    sufficient because multiple steps of the same request can land in
    the same second, and audit_id (a random UUID) must never be used as
    a tie-breaker since it has no relationship to insertion order.

    record_hash = sha256(prev_hash + audit_id + request_id + workflow_step
    + policy_result + action_taken), chained via prev_hash to the row at
    seq-1. Tampering with or deleting any row breaks the chain for every
    row after it — verifiable via audit_service.verify_chain, and
    enforced at the database level by revoking UPDATE/DELETE on this
    table for the application role in Postgres (see the accompanying
    migration).
    """
    __tablename__ = "audit_logs"

    seq = Column(Integer, primary_key=True, autoincrement=True)
    audit_id = Column(String, nullable=False, unique=True, default=generate_audit_id)
    request_id = Column(String, ForeignKey("service_requests.request_id"), nullable=False, index=True)
    workflow_step = Column(String, nullable=False)
    policy_result = Column(String, nullable=False)
    action_taken = Column(String, nullable=True)
    prev_hash = Column(String, nullable=False)
    record_hash = Column(String, nullable=False, unique=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
