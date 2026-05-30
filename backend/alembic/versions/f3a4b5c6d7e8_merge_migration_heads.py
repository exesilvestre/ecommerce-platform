"""merge alembic heads

Revision ID: f3a4b5c6d7e8
Revises: d4e5f6a7b8c9, e2f3a4b5c6d7
Create Date: 2026-05-30 20:00:00.000000

"""
from typing import Sequence, Union


revision: str = "f3a4b5c6d7e8"
down_revision: Union[str, Sequence[str], None] = ("d4e5f6a7b8c9", "e2f3a4b5c6d7")
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
