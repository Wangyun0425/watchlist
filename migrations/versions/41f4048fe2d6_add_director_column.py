"""add director column

Revision ID: 41f4048fe2d6
Revises: ef1c6363c0f7
Create Date: 2023-12-03 02:24:50.925016

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '41f4048fe2d6'
down_revision = 'ef1c6363c0f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movie_info', schema=None) as batch_op:
        batch_op.add_column(sa.Column('director', sa.String(length=255), nullable=True))
        batch_op.alter_column('movie_name',
               existing_type=sa.VARCHAR(length=20),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('movie_info', schema=None) as batch_op:
        batch_op.alter_column('movie_name',
               existing_type=sa.String(length=255),
               type_=sa.VARCHAR(length=20),
               existing_nullable=False)
        batch_op.drop_column('director')

    # ### end Alembic commands ###
