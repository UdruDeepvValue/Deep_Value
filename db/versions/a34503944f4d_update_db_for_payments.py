import sqlalchemy as sa

from alembic import op

from lib.util_datetime import tzware_datetime
from lib.util_sqlalchemy import AwareDateTime


"""
update db for payments

Revision ID: a34503944f4d
Revises: 
Create Date: 2024-06-16 20:18:05.125648
"""

# Revision identifiers, used by Alembic.
revision = 'a34503944f4d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
