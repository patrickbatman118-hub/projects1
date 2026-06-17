"""pool

Revision ID: df48ba063e5c
Revises: af8daeb311bc
Create Date: 2026-06-17 03:20:02.138461

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'df48ba063e5c'
down_revision: Union[str, Sequence[str], None] = 'af8daeb311bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
