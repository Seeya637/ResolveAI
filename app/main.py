from fastapi import FastAPI

from app.config import settings
from app.database import Base, engine
from app.routers import fees, cards, credit_limit, customers, audit, handoffs, sessions

# In Round 1/2 demo mode, create tables directly from models. In a real
# deployment this would be removed entirely in favor of Alembic-managed
# migrations only (see alembic/ — the migration history already exists).
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    description=(
        "Mock servicing backend for ResolveAI. Handles fee reversal, card "
        "replacement, and credit-limit increase requests. The AI/orchestration "
        "layer calls these endpoints; every endpoint runs a deterministic "
        "policy check before taking any action, and every step is written "
        "to an immutable audit log."
    ),
    version="0.1.0",
)

app.include_router(fees.router)
app.include_router(cards.router)
app.include_router(credit_limit.router)
app.include_router(customers.router)
app.include_router(audit.router)
app.include_router(handoffs.router)
app.include_router(sessions.router)


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "ok", "service": settings.app_name, "environment": settings.environment}
