"""
Day 2 addition: conversation/session state, backed by Redis.

Without this, every request to the servicing endpoints is completely
stateless — there is no memory of "the customer said X two messages
ago." A real conversational agent (built by the AI teammate in
LangGraph) needs somewhere to store, between turns:
  - the last detected intent
  - entities extracted so far (e.g. "fee amount" mentioned but not yet
    "which card") so the agent can ask only for what's missing
  - a short rolling history of the conversation for context

This module is intentionally thin: get/update/clear a JSON blob per
session_id. The AI layer owns what goes inside that blob — this module
only owns making it durable and fast to read/write between turns.

Sessions expire automatically after SESSION_TTL_SECONDS of inactivity
so Redis doesn't fill up with abandoned conversations.
"""
import json

import redis

from app.config import settings

SESSION_TTL_SECONDS = 30 * 60  # 30 minutes of inactivity = session expires

_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    """
    Lazily creates a single shared Redis connection. Kept as a function
    (not a module-level constant) so tests can monkeypatch it easily,
    and so a connection isn't opened at import time.
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def _key(session_id: str) -> str:
    return f"session:{session_id}"


def get_session(session_id: str) -> dict:
    """
    Returns the session's stored state, or a fresh empty session shape
    if none exists yet (first message in a new conversation).
    """
    client = get_redis_client()
    raw = client.get(_key(session_id))
    if raw is None:
        return {"last_intent": None, "entities": {}, "history": []}
    return json.loads(raw)


def update_session(session_id: str, last_intent: str | None = None,
                    entities: dict | None = None, history_append: str | None = None) -> dict:
    """
    Merges the given fields into the existing session (rather than
    overwriting it wholesale), resets the TTL on every update so an
    active conversation never expires mid-flow, and returns the full
    updated session.
    """
    session = get_session(session_id)

    if last_intent is not None:
        session["last_intent"] = last_intent
    if entities:
        session["entities"].update(entities)
    if history_append:
        session["history"].append(history_append)
        session["history"] = session["history"][-20:]  # cap history length

    client = get_redis_client()
    client.set(_key(session_id), json.dumps(session), ex=SESSION_TTL_SECONDS)
    return session


def clear_session(session_id: str) -> None:
    """Called once a request is fully resolved or escalated — no reason
    to keep state around for a conversation that's already finished."""
    client = get_redis_client()
    client.delete(_key(session_id))
