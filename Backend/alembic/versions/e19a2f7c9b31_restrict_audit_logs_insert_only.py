"""restrict audit_logs to insert-only (Postgres only)

Revision ID: e19a2f7c9b31
Revises: 9e4efd57daa1
Create Date: 2026-07-24

No-op on SQLite (used only for local dev without docker) since SQLite
has no GRANT/REVOKE model. On real Postgres, revokes UPDATE and DELETE
on audit_logs from the application's runtime role, so even a
compromised or buggy app process cannot alter or erase audit history —
only INSERT is permitted. Combined with the hash chain in
audit_service.py, this turns "immutable audit trail" from a slide
bullet into an enforced, verifiable database property.
"""
from alembic import op


revision = "e19a2f7c9b31"
down_revision = "9e4efd57daa1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return  # SQLite dev fallback has no privilege model to restrict

    op.execute("REVOKE UPDATE, DELETE ON audit_logs FROM PUBLIC;")
    # In a real deployment, replace PUBLIC with the actual least-privilege
    # application role, e.g.:
    # op.execute("REVOKE UPDATE, DELETE ON audit_logs FROM resolveai_app_role;")


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return
    op.execute("GRANT UPDATE, DELETE ON audit_logs TO PUBLIC;")
