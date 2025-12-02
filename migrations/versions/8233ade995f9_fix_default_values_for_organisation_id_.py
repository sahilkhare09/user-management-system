"""Fix default values for organisation_id and department_id

Revision ID: 8233ade995f9
Revises: 0b37f1414f77
Create Date: 2025-12-01 16:49:39.917304

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8233ade995f9'
down_revision: Union[str, Sequence[str], None] = '0b37f1414f77'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    # Remove server default UUID values
    op.alter_column(
        'users',
        'organisation_id',
        server_default=None,
        existing_type=sa.dialects.postgresql.UUID(),
        nullable=True
    )

    op.alter_column(
        'users',
        'department_id',
        server_default=None,
        existing_type=sa.dialects.postgresql.UUID(),
        nullable=True
    )


def downgrade():
    op.alter_column(
        'users',
        'organisation_id',
        server_default=sa.text("uuid_generate_v4()"),
        existing_type=sa.dialects.postgresql.UUID(),
        nullable=True
    )

    op.alter_column(
        'users',
        'department_id',
        server_default=sa.text("uuid_generate_v4()"),
        existing_type=sa.dialects.postgresql.UUID(),
        nullable=True
    )