"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-04

"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "0001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "archives",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("root_path", sa.String(1000), nullable=False),
        sa.Column("analysis_status", sa.String(20), nullable=False, server_default="pending"),
        sa.Column("analysis_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("analysis_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("file_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("directory_count", sa.Integer, nullable=False, server_default="0"),
        sa.Column("total_size_bytes", sa.BigInteger, nullable=False, server_default="0"),
        sa.UniqueConstraint("root_path", name="uq_archives_root_path"),
        sa.CheckConstraint(
            "analysis_status IN ('pending', 'in_progress', 'completed', 'failed')",
            name="ck_archives_analysis_status",
        ),
    )
    op.create_index("idx_archives_status", "archives", ["analysis_status"])
    op.create_index("idx_archives_created", "archives", ["created_at"])

    op.create_table(
        "files",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("archive_id", UUID(as_uuid=True), sa.ForeignKey("archives.id", ondelete="CASCADE"), nullable=False),
        sa.Column("parent_id", UUID(as_uuid=True), sa.ForeignKey("files.id", ondelete="CASCADE"), nullable=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("full_path", sa.String(2000), nullable=False),
        sa.Column("relative_path", sa.String(2000), nullable=False),
        sa.Column("is_directory", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("extension", sa.String(50), nullable=True),
        sa.Column("size_bytes", sa.BigInteger, nullable=True),
        sa.Column("sha256_hash", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("modified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("discovered_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint(
            "(is_directory = true AND extension IS NULL AND size_bytes IS NULL) OR (is_directory = false)",
            name="ck_files_directory_fields",
        ),
    )
    op.create_index("idx_files_archive", "files", ["archive_id"])
    op.create_index("idx_files_parent", "files", ["parent_id"])
    op.create_index("idx_files_path", "files", ["archive_id", "relative_path"])
    op.create_index("idx_files_type", "files", ["is_directory"])
    op.create_index(
        "idx_files_extension", "files", ["extension"],
        postgresql_where=sa.text("extension IS NOT NULL"),
    )
    op.create_index(
        "idx_files_hash", "files", ["sha256_hash"],
        postgresql_where=sa.text("sha256_hash IS NOT NULL"),
    )


def downgrade() -> None:
    op.drop_table("files")
    op.drop_table("archives")
