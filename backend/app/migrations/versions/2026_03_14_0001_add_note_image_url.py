"""add image_url to notes

Revision ID: 7b9f6d2a1c3b
Revises: 06a05227515c
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7b9f6d2a1c3b'
down_revision: Union[str, Sequence[str], None] = '06a05227515c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('notes', sa.Column('image_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('notes', 'image_url')
