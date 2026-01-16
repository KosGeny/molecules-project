"""Initial migration

Revision ID: 001_initial
Revises:
Create Date: 2025-01-02 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa


revision = "001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "molecules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("smiles", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_smiles", "molecules", ["smiles"])
    op.create_index("ix_molecules_id", "molecules", ["id"])


def downgrade():
    op.drop_index("ix_molecules_id", table_name="molecules")
    op.drop_index("idx_smiles", table_name="molecules")
    op.drop_table("molecules")
