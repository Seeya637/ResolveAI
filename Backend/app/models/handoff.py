import uuid

from sqlalchemy import Column, String, DateTime, ForeignKey, func

from app.database import Base


def generate_handoff_id() -> str:
    return f"H-{uuid.uuid4().hex[:8].upper()}"


class HumanHandoff(Base):
    """
    Created whenever the policy engine or classifier decides a request
    can't be auto-resolved. Carries the full AI summary so the customer
    never has to re-explain themselves to a human agent.
    """
    __tablename__ = "human_handoffs"

    handoff_id = Column(String, primary_key=True, default=generate_handoff_id)
    request_id = Column(String, ForeignKey("service_requests.request_id"), nullable=False, index=True)
    escalation_reason = Column(String, nullable=False)
    ai_summary = Column(String, nullable=True)
    status = Column(String, nullable=False, default="pending")  # pending | in_review | resolved
    created_at = Column(DateTime(timezone=True), server_default=func.now())
