"""CUSTOM (not upstream): add openvpn to coretype enum

See CONTRIBUTING-custom.md — this migration is specific to this fork and
should never be proposed upstream as-is (upstream may add its own
mtproto/singbox-style core types with their own migration; this one only
adds ours).

Revision ID: a1b2c3d4e5f6
Revises: 7c4bd5128e62
Create Date: 2026-09-10 00:00:00.000000

"""

from alembic import op


# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "7c4bd5128e62"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Postgres enums can't have a value added inside the same transaction
    # that will use it, and ALTER TYPE ... ADD VALUE cannot run inside a
    # transaction block at all on older Postgres — ADD VALUE IF NOT EXISTS
    # (PG12+) sidesteps both. SQLite/MySQL store CoreType as a plain
    # string column, so this is a no-op there (see model definition).
    if op.get_bind().engine.name == "postgresql":
        op.execute("COMMIT")
        op.execute("ALTER TYPE coretype ADD VALUE IF NOT EXISTS 'openvpn'")


def downgrade() -> None:
    # Postgres cannot drop a single value from an enum type without
    # recreating the type; every core_configs row must already be off
    # 'openvpn' before attempting this downgrade, or it will fail — left
    # manual/unimplemented deliberately rather than silently destructive.
    pass
