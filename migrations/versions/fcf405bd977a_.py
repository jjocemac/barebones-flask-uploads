"""empty message

Revision ID: fcf405bd977a
Revises: 5d7fe68dfe4b
Create Date: 2018-07-26 17:32:27.120066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fcf405bd977a'
down_revision = '5d7fe68dfe4b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('dropbox',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('filename', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('dropbox')
    # ### end Alembic commands ###
