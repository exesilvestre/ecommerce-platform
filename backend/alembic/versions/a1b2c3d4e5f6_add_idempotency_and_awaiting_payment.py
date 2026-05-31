"""add idempotency status column and awaiting_payment order status

Revision ID: a1b2c3d4e5f6
Revises: b876009f0bc8
Create Date: 2026-05-29 12:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "b876009f0bc8"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.execute("ALTER TYPE orderstatus ADD VALUE IF NOT EXISTS 'AWAITING_PAYMENT'")

    op.execute(
        "ALTER TABLE idempotency_keys "
        "ADD COLUMN IF NOT EXISTS status VARCHAR(20) NOT NULL DEFAULT 'completed'"
    )
    op.alter_column(
        "idempotency_keys",
        "response_status",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "idempotency_keys",
        "response_body",
        existing_type=sa.Text(),
        nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "idempotency_keys",
        "response_body",
        existing_type=sa.Text(),
        nullable=False,
    )
    op.alter_column(
        "idempotency_keys",
        "response_status",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.drop_column("idempotency_keys", "status")
