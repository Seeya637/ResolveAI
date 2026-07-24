from sqlalchemy import Column, String, Integer, Numeric, DateTime, func

from app.database import Base


class Customer(Base):
    """
    Minimal customer profile needed by the policy engine to make
    eligibility decisions. In production this would be sourced from
    the bank's core customer system, not owned by this service.
    """
    __tablename__ = "customers"

    customer_id = Column(String, primary_key=True, index=True)
    verification_status = Column(String, nullable=False, default="unverified")
    account_age_months = Column(Integer, nullable=False, default=0)
    card_status = Column(String, nullable=False, default="active")  # active | damaged | lost | blocked
    current_credit_limit = Column(Numeric(12, 2), nullable=False, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
