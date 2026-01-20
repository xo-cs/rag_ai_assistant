import os
import logging
from typing import Optional, Sequence, Dict, Any, cast, Union
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)

MySQLConnectionType = Union[mysql.connector.MySQLConnection, mysql.connector.pooling.PooledMySQLConnection]


class DatabaseConnectionError(Exception):
    """Raised when MySQL connection cannot be established."""
    pass


class DatabaseOperationError(Exception):
    """Raised when a database operation fails."""
    pass


class MySQLRepository:
    """Repository for MySQL metadata storage with lazy connection initialization."""

    def __init__(self) -> None:
        """Initialize repository with connection parameters (no connection created yet)."""
        self.host: str = os.getenv("MYSQL_HOST", "localhost")
        self.user: str = os.getenv("MYSQL_USER", "root")
        self.password: str = os.getenv("MYSQL_PASSWORD", "")
        self.database: str = os.getenv("MYSQL_DATABASE", "rag_db")
        self.port: int = int(os.getenv("MYSQL_PORT", "3306"))
        self._connection: Optional[MySQLConnectionType] = None

    def _get_connection(self) -> MySQLConnectionType:
        """
        Lazily establish and return a MySQL connection.
        Raises DatabaseConnectionError if connection fails.
        """
        if self._connection is None or not self._connection.is_connected():
            try:
                conn = mysql.connector.connect(
                    host=self.host,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                    port=self.port,
                    autocommit=True,
                    connection_timeout=10
                )
                self._connection = cast(MySQLConnectionType, conn)
                logger.info("MySQL connection established successfully")
            except Error as e:
                logger.error(f"Failed to connect to MySQL: {str(e)}")
                raise DatabaseConnectionError(
                    f"Cannot connect to MySQL at {self.host}:{self.port}. "
                    f"Ensure MySQL is running and credentials are correct. Error: {str(e)}"
                )
        return self._connection

    def insert_document_metadata(self, doc_id: str, title: str, content: str, metadata: Dict[str, Any]) -> bool:
        """Insert document metadata. Connects to MySQL on first call."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO documents (doc_id, title, content, metadata)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE title=VALUES(title), content=VALUES(content)
            """
            cursor.execute(query, (doc_id, title, content, str(metadata)))
            logger.info(f"Inserted metadata for document: {doc_id}")
            return True
        except Error as e:
            logger.error(f"Database insert error: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to insert document metadata: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def get_document_metadata(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve document metadata by doc_id."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM documents WHERE doc_id = %s"
            cursor.execute(query, (doc_id,))
            result: Optional[Dict[str, Any]] = cast(Optional[Dict[str, Any]], cursor.fetchone())
            return result
        except Error as e:
            logger.error(f"Database query error: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to retrieve document metadata: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def search_documents(self, query_text: str, limit: int = 10) -> Sequence[Dict[str, Any]]:
        """Search documents by title or content."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            sql = """
                SELECT * FROM documents 
                WHERE title LIKE %s OR content LIKE %s
                LIMIT %s
            """
            search_term = f"%{query_text}%"
            cursor.execute(sql, (search_term, search_term, limit))
            results: Sequence[Dict[str, Any]] = cast(Sequence[Dict[str, Any]], cursor.fetchall())
            return results
        except Error as e:
            logger.error(f"Database search error: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to search documents: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def delete_document(self, doc_id: str) -> bool:
        """Delete document metadata by doc_id."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "DELETE FROM documents WHERE doc_id = %s"
            cursor.execute(query, (doc_id,))
            logger.info(f"Deleted document: {doc_id}")
            return True
        except Error as e:
            logger.error(f"Database delete error: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to delete document: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def close(self) -> None:
        """Close MySQL connection if open."""
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
            logger.info("MySQL connection closed")
            self._connection = None
