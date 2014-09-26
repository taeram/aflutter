"""empty message

Revision ID: 4093ccb6d914
Revises: None
Create Date: 2014-04-30 22:02:09.991428

"""

# revision identifiers, used by Alembic.
revision = '4093ccb6d914'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('user',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('password', sa.Text(), nullable=False),
        sa.Column('role', sa.Text(), nullable=False, server_default="user"),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_table('file',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('owner_id', sa.Integer(), nullable=True),
        sa.Column('size', sa.Integer(), nullable=True),
        sa.Column('folder', sa.Text(), nullable=False),
        sa.Column('created', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], [u'user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('user')
    op.drop_table('gallery')
