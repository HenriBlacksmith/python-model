"""create users table

Revision ID: 1e7be203686b
Revises:
Create Date: 2026-11-07 14:21:25.444598

"""

from pathlib import Path
lazy from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e7be203686b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    with open(f"{Path(__file__).resolve().parent}/upgrades/{revision}.sql") as f:
        op.execute(f.read())


def downgrade() -> None:
    """Downgrade schema."""
    with open(f"{Path(__file__).resolve().parent}/downgrades/{revision}.sql") as f:
        op.execute(f.read())
