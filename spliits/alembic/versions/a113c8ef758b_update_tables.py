"""update tables

Revision ID: a113c8ef758b
Revises: fdaed1d146b6
Create Date: 2026-06-17 03:09:21.703078

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a113c8ef758b'
down_revision: Union[str, Sequence[str], None] = 'fdaed1d146b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
