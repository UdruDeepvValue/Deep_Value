import sqlalchemy as sa

from alembic import op

from lib.util_datetime import tzware_datetime
from lib.util_sqlalchemy import AwareDateTime


"""
update db for users

Revision ID: a4952e83514d
Revises: b3d93dbb9288
Create Date: 2024-06-27 15:00:42.601058
"""

# Revision identifiers, used by Alembic.
revision = 'a4952e83514d'
down_revision = 'b3d93dbb9288'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###
