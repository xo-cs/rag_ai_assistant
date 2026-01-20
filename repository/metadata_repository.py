import mysql.connector
from typing import Optional, Sequence, Dict, Any, cast
from config.settings import settings


class MetadataRepository:
    def __init__(self) -> None:
        self.connection: Optional[mysql.connector.MySQLConnection] = None
    
    def _get_connection(self) -> mysql.connector.MySQLConnection:
        """Lazily establish and return MySQL connection."""
        if self.connection is None or not self.connection.is_connected():
            try:
                conn = mysql.connector.connect(
                    host=settings.mysql_host,
                    user=settings.mysql_user,
                    password=settings.mysql_password,
                    database=settings.mysql_database,
                    port=settings.mysql_port
                )
                self.connection = cast(mysql.connector.MySQLConnection, conn)
            except Exception as e:
                raise RuntimeError(f"Failed to connect to MySQL: {str(e)}")
        return self.connection
    
    def get_chunk_metadata(self, chunk_ids: Sequence[int]) -> Sequence[Dict[str, Any]]:
        """
        Fetch chunk metadata by IDs.
        
        Expected table schema:
        chunks(id, chunk_text, document_id, ...)
        documents(id, name, ...)
        """
        if not chunk_ids:
            return []
        
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            
            placeholders = ",".join(["%s"] * len(chunk_ids))
            query = f"""
            SELECT c.id as chunk_id, c.chunk_text, d.name as document_name
            FROM chunks c
            JOIN documents d ON c.document_id = d.id
            WHERE c.id IN ({placeholders})
            ORDER BY FIELD(c.id, {placeholders})
            """
            
            params = list(chunk_ids) + list(chunk_ids)
            cursor.execute(query, params)
            results: Sequence[Dict[str, Any]] = cast(Sequence[Dict[str, Any]], cursor.fetchall())
            return results
        except Exception as e:
            raise RuntimeError(f"Failed to fetch chunk metadata: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection is not None and self.connection.is_connected():
            self.connection.close()
    
    def __del__(self):
        self.close()
