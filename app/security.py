"""
Minimal service-to-service auth. Every servicing endpoint requires a valid
X-API-Key header. This is the floor, not the ceiling — production would
add per-caller keys, mTLS between internal services, and short-lived
customer-facing tokens validated against a real identity provider. But
"zero auth on financial mutation endpoints" is not shippable at any tier,
so this is non-negotiable even for a hackathon prototype.
"""
from fastapi import Header, HTTPException

from app.config import settings


def verify_api_key(x_api_key: str = Header(...)) -> None:
    if x_api_key != settings.internal_api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
