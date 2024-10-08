import sqlalchemy as sa

from alembic import op

from lib.util_datetime import tzware_datetime
from lib.util_sqlalchemy import AwareDateTime


"""
update db for users

Revision ID: b3d93dbb9288
Revises: 0b9c78ed7013
Create Date: 2024-06-25 16:16:04.272116
"""

# Revision identifiers, used by Alembic.
revision = 'b3d93dbb9288'
down_revision = '0b9c78ed7013'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('previous_plan', sa.String(length=128), nullable=True))
    op.add_column('users', sa.Column('last_search_on', AwareDateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'last_search_on')
    op.drop_column('users', 'previous_plan')
    # ### end Alembic commands ###
