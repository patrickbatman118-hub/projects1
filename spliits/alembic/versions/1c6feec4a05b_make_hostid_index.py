"""Make hostid index

Revision ID: 1c6feec4a05b
Revises: 112e4d8732ae
Create Date: 2026-06-17 09:14:27.975917

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c6feec4a05b'
down_revision: Union[str, Sequence[str], None] = '112e4d8732ae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
