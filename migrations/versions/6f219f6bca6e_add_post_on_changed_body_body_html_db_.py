"""add Post.on_changed_body, body_html, db.event.listen

Revision ID: 6f219f6bca6e
Revises: ac6e9871c9a4
Create Date: 2015-12-24 14:26:54.691432

"""

# revision identifiers, used by Alembic.
revision = '6f219f6bca6e'
down_revision = 'ac6e9871c9a4'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('body_html', sa.Text(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'body_html')
    ### end Alembic commands ###