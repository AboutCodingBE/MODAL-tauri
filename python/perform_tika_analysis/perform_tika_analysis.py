import os
import uuid
from shared.database import get_session
from file_repository import FileRepository
from tika_extractor import TIKA_text_extract
from text_functions import normalize_newlines, get_word_count, file_filter, path_filter
from tika_repository import TikaRepository 

class PerformTikaAnalysis:
    """Flow controller for running the tika analysis on selected folder."""

    def __init__(self):
        self._fileRepo = FileRepository()

    def _ensure_single_value(self, value):
        """
        Zorgt ervoor dat we één waarde overhouden. 
        Lijsten worden gereduceerd tot het eerste element.
        Lege strings worden None (SQL NULL).
        """
        if isinstance(value, list):
            value = value[0] if value else None
        
        if value == "" or value is None:
            return None
            
        return str(value).strip()

    def execute(self, archiveuuid) -> None | str:
        files = self._fileRepo.get_by_archive(archiveuuid)
        num_tot_files, num_processed_files, num_extract_texts = 0, 0, 0
        
        with get_session() as session:
            tika_repo = TikaRepository(session)
            for file in files:
                file_path = file["path"]
                file_name = file["name"]
                file_id = file["id"]
                num_tot_files += 1
                print(f"Processing file {num_tot_files}: {file_path}")

                if file_filter(file_name) and path_filter(file_path):
                    num_processed_files += 1
                    tika = TIKA_text_extract(file_path)
                    
                    # Check of we een geldige tuple terugkrijgen met 6 elementen
                    if not isinstance(tika, (tuple, list)) or len(tika) < 6:
                        print(f"{file_name} unable to perform Tika analysis (Invalid Tika output).")
                        continue

                    # Data opschonen met onze helper
                    mime_type = self._ensure_single_value(tika[0])
                    content = tika[1] # Content laten we als tekst (geen lijst verwacht)
                    
                    # Parser is vaak een lijst, die maken we plat naar een string voor de tekstkolom
                    parsers = tika[2]
                    tika_parser = ", ".join(parsers) if isinstance(parsers, list) else str(parsers)
                    
                    lang = self._ensure_single_value(tika[3])
                    creation_date = self._ensure_single_value(tika[4])
                    creator = self._ensure_single_value(tika[5])

                    if content and len(str(content).strip()) > 0:
                        num_extract_texts += 1
                        clean_content = normalize_newlines(content)
                        word_count = get_word_count(clean_content)
                    else:
                        clean_content = None
                        word_count = 0

                    try:
                        # We sturen nu 'None' door waar eerst een lege string of lijst stond
                        tika_repo.persist(
                            file_id, 
                            mime_type, 
                            tika_parser, 
                            clean_content, 
                            lang, 
                            word_count, 
                            creator, 
                            creation_date
                        )
                        print(f"{file_name} written to {file_id}")
                    except Exception as e:
                        print(f"Fout bij opslaan van {file_name}: {e}")
                        session.rollback() # Voorkom dat de sessie corrupt raakt bij een error
                else:
                    print(f"{file_name} is ignored.")