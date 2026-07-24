"""
Tests for the Day 2 Redis session service. Uses fakeredis (an in-memory
Redis-compatible server) instead of a real Redis connection, so these
tests run anywhere with zero infrastructure — matching the same
philosophy as the policy-engine tests.
"""
import fakeredis
import pytest

from app.services import session_service


@pytest.fixture(autouse=True)
def fake_redis(monkeypatch):
    fake = fakeredis.FakeRedis(decode_responses=True)
    monkeypatch.setattr(session_service, "_redis_client", fake)
    monkeypatch.setattr(session_service, "get_redis_client", lambda: fake)
    yield fake


def test_new_session_has_empty_shape():
    session = session_service.get_session("s1")
    assert session == {"last_intent": None, "entities": {}, "history": []}


def test_update_sets_intent_and_entities():
    session_service.update_session("s1", last_intent="fee_reversal", entities={"fee_amount": 199.0})
    session = session_service.get_session("s1")
    assert session["last_intent"] == "fee_reversal"
    assert session["entities"]["fee_amount"] == 199.0


def test_update_merges_entities_instead_of_overwriting():
    session_service.update_session("s1", entities={"fee_amount": 199.0})
    session_service.update_session("s1", entities={"card_last4": "4321"})
    session = session_service.get_session("s1")
    assert session["entities"] == {"fee_amount": 199.0, "card_last4": "4321"}


def test_history_appends_and_caps_at_20():
    for i in range(25):
        session_service.update_session("s1", history_append=f"message {i}")
    session = session_service.get_session("s1")
    assert len(session["history"]) == 20
    assert session["history"][0] == "message 5"  # oldest 5 dropped
    assert session["history"][-1] == "message 24"


def test_clear_session_resets_to_empty():
    session_service.update_session("s1", last_intent="card_replacement")
    session_service.clear_session("s1")
    session = session_service.get_session("s1")
    assert session == {"last_intent": None, "entities": {}, "history": []}
