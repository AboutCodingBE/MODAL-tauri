from shared.in_memory_store import archives


class ArchiveRepository:
    def get_all(self) -> list[dict]:
        """Return all archives ordered by creation date descending."""
        return [
            {
                "id": a["id"],
                "name": a["name"],
                "created_at": a["created_at"],
                "analysis_status": a["analysis_status"],
                "file_count": a["file_count"],
            }
            for a in sorted(
                archives.values(),
                key=lambda x: x["created_at"],
                reverse=True,
            )
        ]
