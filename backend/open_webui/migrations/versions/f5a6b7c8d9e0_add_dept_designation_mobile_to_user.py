"""add department, designation, mobile_number to user

Revision ID: f5a6b7c8d9e0
Revises: 461111b60977
Create Date: 2026-08-25 14:30:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = 'f5a6b7c8d9e0'
down_revision: Union[str, None] = '461111b60977'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_cols = {c['name'] for c in inspector.get_columns('user')}

    with op.batch_alter_table('user') as batch_op:
        if 'department' not in existing_cols:
            batch_op.add_column(sa.Column('department', sa.Text(), nullable=True))
        if 'designation' not in existing_cols:
            batch_op.add_column(sa.Column('designation', sa.Text(), nullable=True))
        if 'mobile_number' not in existing_cols:
            batch_op.add_column(sa.Column('mobile_number', sa.Text(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.drop_column('mobile_number')
        batch_op.drop_column('designation')
        batch_op.drop_column('department')
