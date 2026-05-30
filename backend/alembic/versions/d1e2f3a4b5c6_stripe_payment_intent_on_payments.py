"""stripe payment intent on payments

Revision ID: d1e2f3a4b5c6
Revises: c7d8e9f0a1b2
Create Date: 2026-05-30 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "d1e2f3a4b5c6"
down_revision: Union[str, Sequence[str], None] = "c7d8e9f0a1b2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("payment_intent_id", sa.String(), nullable=True))
    op.create_index(
        "ix_payments_payment_intent_id",
        "payments",
        ["payment_intent_id"],
        unique=True,
    )
    op.drop_column("payments", "credit_card_number")
    op.drop_column("payments", "credit_card_expiration_date")


def downgrade() -> None:
    op.add_column(
        "payments",
        sa.Column("credit_card_expiration_date", sa.String(), nullable=False, server_default=""),
    )
    op.add_column(
        "payments",
        sa.Column("credit_card_number", sa.String(), nullable=False, server_default=""),
    )
    op.alter_column("payments", "credit_card_number", server_default=None)
    op.alter_column("payments", "credit_card_expiration_date", server_default=None)
    op.drop_index("ix_payments_payment_intent_id", table_name="payments")
    op.drop_column("payments", "payment_intent_id")
