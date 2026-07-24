"""
Tests for the hash-chained audit log — the exact mechanism that was
previously broken (timestamp/UUID tie-breaking) and is now fixed with
a true autoincrement `seq` ordering column. These tests use a real
in-memory SQLite DB, not mocks, because the bug was a DB-ordering issue
that only shows up against a real database.
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.services import audit_service


@pytest.fixture
def db_session():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def test_single_entry_chains_from_genesis(db_session):
    entry = audit_service.log_step(db_session, "SR-TEST1", "intent_classified", "test")
    assert entry.prev_hash == audit_service.GENESIS_HASH
    assert entry.record_hash is not None
    intact, broken_at = audit_service.verify_chain(db_session)
    assert intact is True
    assert broken_at is None


def test_many_rapid_entries_stay_correctly_ordered(db_session):
    # Regression test for the exact bug found during hardening: entries
    # created within the same second must still chain in true insertion
    # order, not get scrambled by timestamp ties.
    for i in range(10):
        audit_service.log_step(db_session, f"SR-TEST{i}", "policy_check", f"step {i}")
    intact, broken_at = audit_service.verify_chain(db_session)
    assert intact is True
    assert broken_at is None


def test_tampering_a_row_breaks_the_chain(db_session):
    e1 = audit_service.log_step(db_session, "SR-TEST1", "intent_classified", "original reason")
    audit_service.log_step(db_session, "SR-TEST1", "policy_check", "Eligible")

    # Simulate tampering: directly mutate a historical row's policy_result
    # without going through log_step (exactly what UPDATE/DELETE
    # restrictions in Postgres are meant to prevent).
    e1.policy_result = "Eligible"  # tampered value, hash no longer matches
    db_session.commit()

    intact, broken_at = audit_service.verify_chain(db_session)
    assert intact is False
    assert broken_at == e1.audit_id
