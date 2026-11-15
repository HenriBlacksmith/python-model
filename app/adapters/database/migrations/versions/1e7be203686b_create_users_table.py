"""create users table

Revision ID: 1e7be203686b
Revises:
Create Date: 2026-11-07 14:21:25.444598

"""

lazy from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1e7be203686b"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
    CREATE TABLE users (
        id UUID PRIMARY KEY,
        name VARCHAR NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL
    );""")

    op.execute("CREATE UNIQUE INDEX name_unique_idx ON users (name);")

    op.execute("""
    CREATE FUNCTION set_updated_at() RETURNS trigger
    LANGUAGE plpgsql AS
    $$BEGIN
        NEW.updated_at := current_timestamp;
        RETURN NEW;
    END;$$;
    """)
    op.execute("""
    CREATE TRIGGER users_update_trigger
    BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE PROCEDURE set_updated_at();
    """)
    op.execute("""
    CREATE OR REPLACE FUNCTION user_events() RETURNS TRIGGER AS $$
    DECLARE
        payload JSON;
        record_data JSON;
    BEGIN
         IF (TG_OP = 'DELETE') THEN
            record_data = row_to_json(OLD);
        ELSE
            record_data = row_to_json(NEW);
        END IF;
        payload = json_build_object('action', TG_OP, 'data', record_data);
        PERFORM pg_notify('user_events', payload::text);
      RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """)
    op.execute("""
    CREATE TRIGGER user_events_trigger
    AFTER INSERT OR UPDATE OR DELETE ON users
    FOR EACH ROW EXECUTE FUNCTION user_events();
    """)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TRIGGER IF EXISTS users_update_trigger ON users;")
    op.execute("DROP FUNCTION IF EXISTS set_updated_at();")
    op.execute("DROP TABLE IF EXISTS users;")
