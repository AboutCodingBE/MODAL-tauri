
import os
from shared.database import get_session
from file_repository import FileRepository
from tika_extractor import TIKA_text_extract
from text_functions import normalize_newlines, get_word_count, file_filter, path_filter
from tika_repository import TikaRepository 
class PerformTikaAnalysis:
    """Flow controller for creating a new archive and running the initial folder analysis."""

    def __init__(self):
        self._fileRepo = FileRepository()

    def execute(self, archiveuuid) -> None | str:
        print("TEST")
        files = self._fileRepo.get_by_archive(archiveuuid)
        num_tot_files,num_processed_files,num_extract_texts=0,0,0
        
        with get_session() as session:
            tika_repo=TikaRepository(session)
            for file in files:
                file_path = file["path"]
                file_name = file["name"]
                file_id = file["id"]
                num_tot_files += 1
                print(f"Processing file {num_tot_files}: {file_path}")

                if file_filter(file_name) and path_filter(file_path):
                    print("A")
                    num_processed_files += 1
                    tika = TIKA_text_extract(file_path)
                    if not tika or len(tika) < 6: # Check if tika output is valid
                        raise ValueError("Unexpected TIKA output structure")

                    mime_type, content, tika_parser, lang, creation_date, creator = (
                        tika[0], tika[1], tika[2][1:], tika[3], tika[4], tika[5]
                    )
                    print("B")

                    if content and len(content) > 0:
                        num_extract_texts += 1

                    clean_content = normalize_newlines(content) # Remove multiple newlines from the text

                    word_count = get_word_count(clean_content) # Calculate word count
                    print("C")

                    tika_repo.persist(file_id,mime_type,tika_parser,content,lang,word_count,creator,creation_date)
                    print(f"{file} written to {file_id}")
                else:
                    print(f"{file} is ignored.")