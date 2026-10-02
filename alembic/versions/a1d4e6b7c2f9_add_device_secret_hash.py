"""add device_secret_hash

Revision ID: a1d4e6b7c2f9
Revises: 7f5c203f34e1
Create Date: 2026-10-02 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = 'a1d4e6b7c2f9'
down_revision: Union[str, Sequence[str], None] = '7f5c203f34e1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Nullable on purpose: guests created before this migration have no secret and claim one on next login.
    op.add_column('players', sa.Column('device_secret_hash', sa.String(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('players', 'device_secret_hash')
