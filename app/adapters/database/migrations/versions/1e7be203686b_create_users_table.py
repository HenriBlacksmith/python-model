"""create users table

Revision ID: 1e7be203686b
Revises:
Create Date: 2026-11-07 14:21:25.444598

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e7be203686b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String, nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    pass
