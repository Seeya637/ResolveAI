from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.customer import Customer
from app.schemas.common import CustomerContextOut
from app.security import verify_api_key

router = APIRouter(prefix="/customers", tags=["Customers"], dependencies=[Depends(verify_api_key)])


@router.get("/{customer_id}/context", response_model=CustomerContextOut)
def get_customer_context(customer_id: str, db: Session = Depends(get_db)):
    """
    Called by the AI orchestration layer before running any eligibility
    check — this is the "customer-context retrieval" node in the
    LangGraph workflow.
    """
    customer = db.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer
