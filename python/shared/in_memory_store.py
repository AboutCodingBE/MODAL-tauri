"""
Shared in-memory store used by all features until the database is introduced (steps 5-6).

State is serialised to modal_store.json next to this file so it survives across
Python subprocess invocations (each Tauri invoke() spawns a fresh Python process).
The public API (archives, files, next_archive_id, next_file_id) is unchanged from
the pure in-memory version — callers just need to call save() after mutations.
"""
import json
from pathlib import Path

_STORE_FILE = Path(__file__).parent.parent / "modal_store.json"


def _load() -> tuple[dict, dict, int, int]:
    if _STORE_FILE.exists():
        data = json.loads(_STORE_FILE.read_text(encoding="utf-8"))
        return (
            {int(k): v for k, v in data.get("archives", {}).items()},
            {int(k): v for k, v in data.get("files", {}).items()},
            data.get("_next_archive_id", 1),
            data.get("_next_file_id", 1),
        )
    return {}, {}, 1, 1


archives, files, _next_archive_id, _next_file_id = _load()


def next_archive_id() -> int:
    global _next_archive_id
    id_ = _next_archive_id
    _next_archive_id += 1
    return id_


def next_file_id() -> int:
    global _next_file_id
    id_ = _next_file_id
    _next_file_id += 1
    return id_


def save() -> None:
    """Persist the current in-memory state to disk."""
    _STORE_FILE.write_text(
        json.dumps({
            "archives": archives,
            "files": files,
            "_next_archive_id": _next_archive_id,
            "_next_file_id": _next_file_id,
        }, default=str, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
