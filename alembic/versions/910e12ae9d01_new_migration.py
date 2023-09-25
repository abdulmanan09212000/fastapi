"""New Migration

Revision ID: 910e12ae9d01
Revises: 56c05a296e4f
Create Date: 2023-04-13 12:29:27.800464

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '910e12ae9d01'
down_revision = '56c05a296e4f'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('token', sa.Column('token', sa.String(), nullable=True))
    op.create_unique_constraint(None, 'token', ['token'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'token', type_='unique')
    op.drop_column('token', 'token')
    # ### end Alembic commands ###