"""
Every action calls log_step() exactly once per workflow step. This is the
single code path that writes to AuditLogs, and it is the only place a
record_hash is ever computed, so no endpoint can write an unhashed or
inconsistent audit row.

Ordering for the hash chain is by `seq` (autoincrement integer), never by
timestamp or audit_id — timestamp can tie within a transaction, and
audit_id is a random UUID with no relationship to insertion order.

GENESIS_HASH anchors the very first row of the entire table's chain.
"""
import hashlib

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.audit_log import AuditLog, generate_audit_id

GENESIS_HASH = "0" * 64


def _compute_hash(prev_hash: str, audit_id: str, request_id: str,
                   workflow_step: str, policy_result: str, action_taken: str | None) -> str:
    payload = f"{prev_hash}|{audit_id}|{request_id}|{workflow_step}|{policy_result}|{action_taken or ''}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _get_last_hash(db: Session) -> str:
    last = db.execute(select(AuditLog).order_by(AuditLog.seq.desc())).scalars().first()
    return last.record_hash if last else GENESIS_HASH


def log_step(
    db: Session,
    request_id: str,
    workflow_step: str,
    policy_result: str,
    action_taken: str | None = None,
    flush_only: bool = False,
) -> AuditLog:
    """
    flush_only guards a larger atomic transaction (see the routers) so
    the whole request-create -> policy-check -> action -> audit
    sequence commits as one unit, or none of it does.

    audit_id and record_hash are both computed in Python BEFORE the row
    is ever added/flushed — record_hash is NOT NULL at the schema level,
    so the row must arrive at the database already fully formed. Never
    flush an AuditLog row before its hash is set.
    """
    prev_hash = _get_last_hash(db)
    audit_id = generate_audit_id()
    record_hash = _compute_hash(prev_hash, audit_id, request_id, workflow_step, policy_result, action_taken)

    entry = AuditLog(
        audit_id=audit_id,
        request_id=request_id,
        workflow_step=workflow_step,
        policy_result=policy_result,
        action_taken=action_taken,
        prev_hash=prev_hash,
        record_hash=record_hash,
    )
    db.add(entry)
    db.flush()  # assigns entry.seq without ending the outer transaction

    if not flush_only:
        db.commit()
        db.refresh(entry)
    return entry


def verify_chain(db: Session) -> tuple[bool, str | None]:
    """
    Recomputes every row's hash from its stored fields, in true `seq`
    order, and confirms it matches both record_hash and the next row's
    prev_hash. Returns (True, None) if the whole table is intact, or
    (False, audit_id) at the first row where the chain breaks.
    """
    rows = db.execute(select(AuditLog).order_by(AuditLog.seq)).scalars().all()
    expected_prev = GENESIS_HASH
    for row in rows:
        recomputed = _compute_hash(expected_prev, row.audit_id, row.request_id,
                                    row.workflow_step, row.policy_result, row.action_taken)
        if row.prev_hash != expected_prev or row.record_hash != recomputed:
            return False, row.audit_id
        expected_prev = row.record_hash
    return True, None
