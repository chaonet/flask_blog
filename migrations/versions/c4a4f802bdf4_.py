"""empty message

Revision ID: c4a4f802bdf4
Revises: c1b387222189
Create Date: 2015-12-18 17:55:52.512077

"""

# revision identifiers, used by Alembic.
revision = 'c4a4f802bdf4'
down_revision = 'c1b387222189'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('confirmed', sa.Boolean(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'confirmed')
    ### end Alembic commands ###
