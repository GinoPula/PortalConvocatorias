"""cuestionario de perfil por cargo

Revision ID: a91c5e3b7d20
Revises: 78e7cf8262b6
Create Date: 2026-09-25 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a91c5e3b7d20'
down_revision = '78e7cf8262b6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('postulants', sa.Column('evaluaciones_perfil', sa.JSON(), nullable=False, server_default='{}'))
    op.add_column('positions', sa.Column('perfil_codigo', sa.String(), nullable=False, server_default=''))


def downgrade() -> None:
    op.drop_column('positions', 'perfil_codigo')
    op.drop_column('postulants', 'evaluaciones_perfil')
