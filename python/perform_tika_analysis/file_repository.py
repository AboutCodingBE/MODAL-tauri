from sqlalchemy import select

from shared.database import get_session
from shared.models import File


class FileRepository:
    #Returns all files (not folders) associated with an archive
    def get_by_archive(self,archive_id) -> list[dict]:
        #print(archive_id)
        with get_session() as session:
            files = session.execute(
                select(File)
            ).scalars().all()
            match=[]
            for a in files:
                #print(str(a.archive_id)+ " EN " + archive_id)
                if str(a.archive_id)==str(archive_id) and not a.is_directory:
                    match.append({"path": str(a.full_path),"name": str(a.name),"id": str(a.id)})
                    #print(a.name)
            return match
