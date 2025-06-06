"""Adiciona user_id em Notificacao

Revision ID: 0558bcce7a8d
Revises: 4c47cf53b12d
Create Date: 2025-06-04 16:20:51.727473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0558bcce7a8d'
down_revision = '4c47cf53b12d'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notificacao', schema=None) as batch_op:
        batch_op.add_column(sa.Column('user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_notificacao_user_id', 'user', ['user_id'], ['id'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('notificacao', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('user_id')

    # ### end Alembic commands ###
