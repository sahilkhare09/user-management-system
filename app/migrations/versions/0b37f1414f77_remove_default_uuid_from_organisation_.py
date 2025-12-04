"""Remove default UUID from organisation_id and department_id

Revision ID: 0b37f1414f77
Revises: e549f01d7a69
Create Date: 2025-12-01 16:44:18.055500

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0b37f1414f77"
down_revision: Union[str, Sequence[str], None] = "e549f01d7a69"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
