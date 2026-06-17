"""Update tables

Revision ID: af8daeb311bc
Revises: a113c8ef758b
Create Date: 2026-06-17 03:17:37.317455

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af8daeb311bc'
down_revision: Union[str, Sequence[str], None] = 'a113c8ef758b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
