import uuid
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor

class TikaRepository:
    def __init__(self, db_config):
        """
        Initialize the repository with database connection settings.
        :param db_config: dict containing host, database, user, password
        """
        self.config = db_config

    def _get_connection(self):
        return psycopg2.connect(**self.config)

    def get_file_id_by_path(self, full_path):
        """
        Finds the UUID of a file based on its absolute path.
        Required to link the Tika analysis to the correct record in the 'files' table.
        """
        query = "SELECT id FROM files WHERE full_path = %s;"
        conn = self._get_connection()
        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, (full_path,))
                result = cur.fetchone()
                return result['id'] if result else None
        finally:
            conn.close()

    def save_analysis(self, file_id, tika_data):
        """
        Saves extracted Tika metadata and content into the 'file_analyses' table.
        Uses an UPSERT strategy (ON CONFLICT) to update existing analyses.
        """
        query = """
            INSERT INTO file_analyses (
                id, file_id, mime_type, tika_parser, content, 
                language, word_count, author, content_created_at, analyzed_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (file_id) DO UPDATE SET
                content = EXCLUDED.content,
                word_count = EXCLUDED.word_count,
                analyzed_at = NOW();
        """
        
        analysis_id = str(uuid.uuid4())
        
        # Prepare values, ensuring complex types like lists are converted to strings
        values = (
            analysis_id,
            file_id,
            tika_data.get('mime_type'),
            str(tika_data.get('tika_parser')), 
            tika_data.get('content'),
            tika_data.get('language'),
            tika_data.get('word_count'),
            tika_data.get('author'),
            tika_data.get('content_created_at'),
            datetime.now()
        )

        conn = self._get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute(query, values)
            conn.commit()
            return analysis_id
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()