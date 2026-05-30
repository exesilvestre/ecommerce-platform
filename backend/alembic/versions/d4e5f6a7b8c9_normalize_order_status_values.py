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
    op.execute(
        "ALTER TYPE orderstatus RENAME VALUE 'awaiting_payment' TO 'AWAITING_PAYMENT'"
    )


def downgrade() -> None:
    op.execute(
        "ALTER TYPE orderstatus RENAME VALUE 'AWAITING_PAYMENT' TO 'awaiting_payment'"
    )
