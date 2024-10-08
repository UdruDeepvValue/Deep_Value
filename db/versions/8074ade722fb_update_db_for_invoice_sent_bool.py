"""update db for Invoice sent bool

Revision ID: 8074ade722fb
Revises: 0c5119767475
Create Date: 2024-08-19 19:15:29.578550

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8074ade722fb'
down_revision = '0c5119767475'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('purchases', sa.Column('invoice_sent', sa.Boolean(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('purchases', 'invoice_sent')
    # ### end Alembic commands ###
