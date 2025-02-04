"""empty message

Revision ID: 5378fc1ad1f1
Revises: ac535a89afe2
Create Date: 2025-01-21 18:03:09.350296

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5378fc1ad1f1'
down_revision = 'ac535a89afe2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('training_request',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('gender', sa.String(length=10), nullable=False),
    sa.Column('organization', sa.String(length=200), nullable=False),
    sa.Column('organization_address', sa.String(length=500), nullable=False),
    sa.Column('job_title', sa.String(length=100), nullable=False),
    sa.Column('email', sa.String(length=120), nullable=False),
    sa.Column('street_address', sa.String(length=500), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('telephone', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('upcoming_training_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['upcoming_training_id'], ['upcoming_training.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('training_request')
    # ### end Alembic commands ###
