import mysql.connector
from typing import Dict, List

class MetadataStore:
    def __init__(self):
        self.conn = mysql.connector.connect(
            host="127.0.0.1",
            port=3306,
            user="root",
            password="Abcd@1234",
            database="rag_metadata"
        )
        self.cursor = self.conn.cursor(dictionary=True)

    def get_existing_documents(self) -> set:
        """Returns a set of document names that are already indexed."""
        try:
            # Check if table exists first to avoid crashing on fresh install
            self.cursor.execute("SHOW TABLES LIKE 'document_chunks'")
            if not self.cursor.fetchone():
                return set()

            self.cursor.execute("SELECT DISTINCT document_name FROM document_chunks")
            results = self.cursor.fetchall()
            return {row['document_name'] for row in results}
        except Exception as e:
            print(f"⚠️ Warning checking existing docs: {e}")
            return set()

    def insert_chunk_metadata(self, metadata: Dict):
        query = """
        INSERT INTO document_chunks
        (chunk_id, vector_id, document_name, page_or_section, chunk_text, chunk_context)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            metadata["chunk_id"],
            metadata["vector_id"],
            metadata["document_name"],
            metadata.get("page_or_section"),
            metadata["chunk_text"],
            metadata.get("chunk_context", "")
        )
        self.cursor.execute(query, values)
        self.conn.commit()

    def fetch_by_vector_ids(self, vector_ids: List[int]):
        if not vector_ids:
            return []
            
        placeholders = ",".join(["%s"] * len(vector_ids))
        query = f"""
        SELECT * FROM document_chunks
        WHERE vector_id IN ({placeholders})
        """
        self.cursor.execute(query, vector_ids)
        return self.cursor.fetchall()

    def close(self):
        self.cursor.close()
        self.conn.close()