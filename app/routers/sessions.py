from fastapi import APIRouter, Depends

from app.schemas.sessions import SessionUpdateRequest, SessionOut
from app.security import verify_api_key
from app.services import session_service

router = APIRouter(prefix="/sessions", tags=["Sessions"], dependencies=[Depends(verify_api_key)])


@router.get("/{session_id}", response_model=SessionOut)
def get_session(session_id: str):
    """
    Called by the AI orchestration layer at the start of every turn to
    recover conversation state (what's already been asked/answered).
    """
    return session_service.get_session(session_id)


@router.post("/{session_id}", response_model=SessionOut)
def update_session(session_id: str, payload: SessionUpdateRequest):
    """
    Called by the AI orchestration layer after each turn to persist the
    newly detected intent/entities. Resets the session's TTL.
    """
    return session_service.update_session(
        session_id,
        last_intent=payload.last_intent,
        entities=payload.entities,
        history_append=payload.history_append,
    )


@router.delete("/{session_id}")
def clear_session(session_id: str):
    """Called once a request resolves or escalates — the conversation is over."""
    session_service.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}
