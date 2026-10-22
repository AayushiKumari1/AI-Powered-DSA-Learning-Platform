"""add group_key to community messages

Revision ID: 7f3a9d2d9c81
Revises: e4c0dc99d431
Create Date: 2026-04-03 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "7f3a9d2d9c81"
down_revision = "e4c0dc99d431"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("community_messages", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "group_key",
                sa.String(length=60),
                nullable=False,
                server_default=sa.text("'arrays'"),
            )
        )
        batch_op.create_index(batch_op.f("ix_community_messages_group_key"), ["group_key"], unique=False)

    op.execute(
        sa.text(
            "UPDATE community_messages "
            "SET group_key = 'arrays' "
            "WHERE group_key IS NULL OR group_key = ''"
        )
    )


def downgrade():
    with op.batch_alter_table("community_messages", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_community_messages_group_key"))
        batch_op.drop_column("group_key")
