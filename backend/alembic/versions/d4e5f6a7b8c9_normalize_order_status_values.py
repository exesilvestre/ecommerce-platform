"""normalize order status enum values to uppercase

Revision ID: d4e5f6a7b8c9
Revises: c7d8e9f0a1b2
Create Date: 2026-05-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c7d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # No-op if fresh install already has AWAITING_PAYMENT from a1b2c3d4e5f6.
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM pg_enum e
                JOIN pg_type t ON e.enumtypid = t.oid
                WHERE t.typname = 'orderstatus'
                  AND e.enumlabel = 'awaiting_payment'
            ) THEN
                ALTER TYPE orderstatus RENAME VALUE 'awaiting_payment' TO 'AWAITING_PAYMENT';
            END IF;
        END
        $$;
        """
    )


def downgrade() -> None:
    op.execute(
        "ALTER TYPE orderstatus RENAME VALUE 'AWAITING_PAYMENT' TO 'awaiting_payment'"
    )
