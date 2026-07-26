from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.database import get_db
from app.models.audit_log import AuditLog
from app.schemas.common import AuditLogOut
from app.security import verify_api_key
from app.services.audit_service import verify_chain

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"], dependencies=[Depends(verify_api_key)])


@router.get("/{request_id}", response_model=list[AuditLogOut])
def get_audit_trail(request_id: str, db: Session = Depends(get_db)):
    stmt = select(AuditLog).where(AuditLog.request_id == request_id).order_by(AuditLog.timestamp)
    return db.execute(stmt).scalars().all()


@router.get("/_integrity/verify")
def verify_audit_log_integrity(db: Session = Depends(get_db)):
    """
    Recomputes the hash chain across the ENTIRE audit_logs table and
    reports whether it's intact. Run this before any compliance export
    or Round-2 demo — a broken chain means a row was tampered with or
    deleted outside of this service.
    """
    intact, broken_at = verify_chain(db)
    return {"intact": intact, "broken_at_audit_id": broken_at}
