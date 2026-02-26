"""add created_at to token_blacklist

Revision ID: a1b2c3d4e5f6
Revises: 6fab8f80ed40
Create Date: 2026-02-26 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '6fab8f80ed40'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'token_blacklist',
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_column('token_blacklist', 'created_at')
