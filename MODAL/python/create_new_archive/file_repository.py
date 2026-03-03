from shared.in_memory_store import files, next_file_id

BATCH_SIZE = 500


class FileRepository:
    """Persists file/directory entries in batches of 500.

    Resolves '_parent_path' references to real parent_ids as entries are saved,
    relying on the parent-first ordering guaranteed by FolderAnalysis.
    """

    def persist_all(self, entries: list[dict]) -> None:
        path_to_id: dict[str, int] = {}

        for batch_start in range(0, len(entries), BATCH_SIZE):
            batch = entries[batch_start: batch_start + BATCH_SIZE]
            self._persist_batch(batch, path_to_id)

    def _persist_batch(self, batch: list[dict], path_to_id: dict[str, int]) -> None:
        for entry in batch:
            file_id = next_file_id()
            parent_path = entry.pop("_parent_path", None)
            parent_id = path_to_id.get(parent_path) if parent_path else None

            record = {**entry, "id": file_id, "parent_id": parent_id}
            files[file_id] = record
            path_to_id[entry["full_path"]] = file_id
