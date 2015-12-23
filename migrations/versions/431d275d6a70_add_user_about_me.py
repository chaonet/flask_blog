"""add user.about_me

Revision ID: 431d275d6a70
Revises: ee9c55ba9b22
Create Date: 2015-12-22 15:38:08.164066

"""

# revision identifiers, used by Alembic.
revision = '431d275d6a70'
down_revision = 'ee9c55ba9b22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('about_me', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'about_me')
    ### end Alembic commands ###