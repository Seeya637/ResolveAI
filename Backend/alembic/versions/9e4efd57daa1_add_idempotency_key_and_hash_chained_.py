"""add idempotency key and hash-chained audit log with seq ordering

Revision ID: 9e4efd57daa1
Revises: 241eaddd0fee
Create Date: 2026-07-24 04:50:27.891170

The audit_logs primary key changes from audit_id (random UUID string) to
seq (autoincrement integer) — a true insertion-order column is required
for the hash chain, since audit_id has no relationship to insertion
order and cannot break timestamp ties correctly.

This is early-stage schema evolution (Day 1, no production data), so
rather than an in-place PK migration this drops and recreates
audit_logs with the corrected schema. Once this system holds real
audit data, a schema change like this would instead require a proper
zero-downtime migration (new table, backfill, dual-write, cutover) —
noted here explicitly so it isn't forgotten later.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '9e4efd57daa1'
down_revision: Union[str, Sequence[str], None] = '241eaddd0fee'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table('audit_logs')
    op.create_table(
        'audit_logs',
        sa.Column('seq', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('audit_id', sa.String(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('workflow_step', sa.String(), nullable=False),
        sa.Column('policy_result', sa.String(), nullable=False),
        sa.Column('action_taken', sa.String(), nullable=True),
        sa.Column('prev_hash', sa.String(), nullable=False),
        sa.Column('record_hash', sa.String(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['request_id'], ['service_requests.request_id']),
        sa.PrimaryKeyConstraint('seq'),
        sa.UniqueConstraint('audit_id', name='uq_audit_logs_audit_id'),
        sa.UniqueConstraint('record_hash', name='uq_audit_logs_record_hash'),
    )
    op.create_index('ix_audit_logs_request_id', 'audit_logs', ['request_id'])

    with op.batch_alter_table('service_requests') as batch_op:
        batch_op.add_column(sa.Column('idempotency_key', sa.String(), nullable=False, server_default=''))
        batch_op.create_index('ix_service_requests_idempotency_key', ['idempotency_key'], unique=False)
        batch_op.create_unique_constraint('uq_idempotency_per_intent', ['idempotency_key', 'intent'])


def downgrade() -> None:
    with op.batch_alter_table('service_requests') as batch_op:
        batch_op.drop_constraint('uq_idempotency_per_intent', type_='unique')
        batch_op.drop_index('ix_service_requests_idempotency_key')
        batch_op.drop_column('idempotency_key')

    op.drop_table('audit_logs')
    op.create_table(
        'audit_logs',
        sa.Column('audit_id', sa.String(), nullable=False),
        sa.Column('request_id', sa.String(), nullable=False),
        sa.Column('workflow_step', sa.String(), nullable=False),
        sa.Column('policy_result', sa.String(), nullable=False),
        sa.Column('action_taken', sa.String(), nullable=True),
        sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['request_id'], ['service_requests.request_id']),
        sa.PrimaryKeyConstraint('audit_id'),
    )
