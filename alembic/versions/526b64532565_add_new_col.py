"""add new col

Revision ID: 526b64532565
Revises: 33f95373b11d
Create Date: 2025-01-19 22:30:31.038959

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '526b64532565'
down_revision: Union[str, None] = '33f95373b11d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('totp_secret', sa.LargeBinary(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'totp_secret')
    # ### end Alembic commands ###
