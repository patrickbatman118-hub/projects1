"""Add pools table

Revision ID: fdaed1d146b6
Revises: c9c6dc99de9b
Create Date: 2026-06-17 01:12:22.220544

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fdaed1d146b6'
down_revision: Union[str, Sequence[str], None] = 'c9c6dc99de9b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
def upgrade():
    op.add_column(
        'users', 
        sa.Column(
            'disabled', 
            sa.Boolean(), 
            nullable=False, 
            server_default='false'  # This is the fix!
        )
    )