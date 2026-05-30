"""warehouse_inventory quantity non-negative check

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-05-30 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "d1e2f3a4b5c6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_check_constraint(
        "ck_warehouse_inventory_quantity_non_negative",
        "warehouse_inventory",
        "quantity >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_warehouse_inventory_quantity_non_negative",
        "warehouse_inventory",
        type_="check",
    )
