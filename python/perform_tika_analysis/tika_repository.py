import uuid

from datetime import datetime, timezone

from sqlalchemy.orm import Session

from shared.models import TikaAnalysis, File

BATCH_SIZE = 500


class TikaRepository:
    """Persists file/directory entries in batches of 500.

    Resolves '_parent_path' references to real parent_ids as entries are saved,
    relying on the parent-first ordering guaranteed by FolderAnalysis.
    UUIDs are generated in Python so no flush-per-row is needed to retrieve IDs.
    """

    def __init__(self, session: Session):
        self._session = session

    def persist(self, file_id: str, mime_type:str, tika_parser:str, content:str, language:str, word_count:int, author:str, content_created_at:datetime) -> TikaAnalysis:
        analysis = TikaAnalysis(file_id=file_id,mime_type=mime_type,tika_parser=tika_parser, content=content, language=language, word_count=word_count, author=author, content_created_at=content_created_at)
        analysis.analyzed_at = datetime.now(timezone.utc)
        self._session.add(analysis)
        self._session.flush()
        return analysis