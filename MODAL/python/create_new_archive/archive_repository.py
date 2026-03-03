from datetime import datetime, timezone

from shared.in_memory_store import archives, next_archive_id


class ArchiveRepository:
    def persist(self, name: str, root_path: str) -> dict:
        """Persist a new archive and return the stored record."""
        archive_id = next_archive_id()
        record = {
            "id": archive_id,
            "name": name,
            "root_path": root_path,
            "analysis_status": "pending",
            "analysis_started_at": None,
            "analysis_completed_at": None,
            "error_message": None,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "description": None,
            "file_count": 0,
            "directory_count": 0,
            "total_size_bytes": 0,
        }
        archives[archive_id] = record
        return record

    def update_status(self, archive_id: int, status: str, error_message: str | None = None) -> None:
        archive = archives[archive_id]
        archive["analysis_status"] = status
        if status == "in_progress":
            archive["analysis_started_at"] = datetime.now(timezone.utc).isoformat()
        elif status in ("completed", "failed"):
            archive["analysis_completed_at"] = datetime.now(timezone.utc).isoformat()
        if error_message is not None:
            archive["error_message"] = error_message

    def update_statistics(self, archive_id: int, file_count: int, directory_count: int, total_size_bytes: int) -> None:
        archive = archives[archive_id]
        archive["file_count"] = file_count
        archive["directory_count"] = directory_count
        archive["total_size_bytes"] = total_size_bytes
