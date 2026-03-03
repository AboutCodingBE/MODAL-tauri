from create_new_archive.archive_repository import ArchiveRepository
from create_new_archive.folder_analysis import FolderAnalysis
from create_new_archive.file_repository import FileRepository
from shared import in_memory_store


class CreateArchive:
    """Flow controller for creating a new archive and running the initial folder analysis."""

    def __init__(self):
        self._archive_repo = ArchiveRepository()
        self._folder_analysis = FolderAnalysis()
        self._file_repo = FileRepository()

    def execute(self, name: str, path: str) -> None | str:
        """
        Validates inputs, persists the archive, then runs and persists the folder analysis.

        Returns None on success, or an error message string on failure.
        """
        # --- Validation ---
        if not name or not name.strip():
            return "Archiefnaam mag niet leeg zijn."
        if not path or not path.strip():
            return "Mappad mag niet leeg zijn."

        name = name.strip()
        path = path.strip()

        # --- Persist archive (separate transaction, provides the archive_id) ---
        try:
            archive = self._archive_repo.persist(name, path)
        except Exception as e:
            return f"Fout bij opslaan archief: {e}"

        archive_id = archive["id"]

        # --- Run folder analysis ---
        try:
            entries = self._folder_analysis.analyze(archive_id, path)
        except Exception as e:
            self._archive_repo.update_status(archive_id, "failed", error_message=str(e))
            return f"Fout bij analyseren map: {e}"

        # --- Persist entries in batches ---
        try:
            self._file_repo.persist_all(entries)
        except Exception as e:
            self._archive_repo.update_status(archive_id, "failed", error_message=str(e))
            return f"Fout bij opslaan bestanden: {e}"

        # --- Update archive statistics ---
        file_count = sum(1 for e in entries if not e.get("is_directory", True))
        directory_count = sum(1 for e in entries if e.get("is_directory", False))
        total_size = sum(e.get("size_bytes") or 0 for e in entries)

        self._archive_repo.update_statistics(archive_id, file_count, directory_count, total_size)

        in_memory_store.save()
        return None
