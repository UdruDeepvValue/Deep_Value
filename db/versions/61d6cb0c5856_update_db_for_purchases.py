"""update db for Purchases

Revision ID: 61d6cb0c5856
Revises: 3c81ba899c85
Create Date: 2024-08-19 18:39:26.153624

"""
from alembic import op
import sqlalchemy as sa
import lib.util_sqlalchemy


# revision identifiers, used by Alembic.
revision = '61d6cb0c5856'
down_revision = '3c81ba899c85'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('purchases',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('product', sa.String(length=128), nullable=True),
    sa.Column('description', sa.String(length=128), nullable=True),
    sa.Column('period_start_on', sa.Date(), nullable=True),
    sa.Column('period_end_on', sa.Date(), nullable=True),
    sa.Column('currency', sa.String(length=8), nullable=True),
    sa.Column('tax', sa.Integer(), nullable=True),
    sa.Column('tax_percent', sa.Float(), nullable=True),
    sa.Column('total', sa.Integer(), nullable=True),
    sa.Column('cc_brand', sa.String(length=32), nullable=True),
    sa.Column('last4', sa.String(length=4), nullable=True),
    sa.Column('exp_date', sa.Date(), nullable=True),
    sa.Column('created_on', lib.util_sqlalchemy.AwareDateTime(), nullable=True),
    sa.Column('updated_on', lib.util_sqlalchemy.AwareDateTime(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_purchases_exp_date'), 'purchases', ['exp_date'], unique=False)
    op.create_index(op.f('ix_purchases_product'), 'purchases', ['product'], unique=False)
    op.create_index(op.f('ix_purchases_user_id'), 'purchases', ['user_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_purchases_user_id'), table_name='purchases')
    op.drop_index(op.f('ix_purchases_product'), table_name='purchases')
    op.drop_index(op.f('ix_purchases_exp_date'), table_name='purchases')
    op.drop_table('purchases')
    # ### end Alembic commands ###
