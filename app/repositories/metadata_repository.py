import os
import logging
from typing import Optional, Sequence, Dict, Any, cast, Union
import mysql.connector
from mysql.connector import Error

logger = logging.getLogger(__name__)

MySQLConnectionType = Union[mysql.connector.MySQLConnection, mysql.connector.pooling.PooledMySQLConnection]


class DatabaseConnectionError(Exception):
    pass


class DatabaseOperationError(Exception):
    pass


class MetadataRepository:
    """MySQL repository with lazy connection initialization."""

    def __init__(self) -> None:
        """Store connection parameters only. No connection created."""
        self.host: str = os.getenv("MYSQL_HOST", "localhost")
        self.user: str = os.getenv("MYSQL_USER", "root")
        self.password: str = os.getenv("MYSQL_PASSWORD", "")
        self.database: str = os.getenv("MYSQL_DATABASE", "rag_db")
        self.port: int = int(os.getenv("MYSQL_PORT", "3306"))
        self._connection: Optional[MySQLConnectionType] = None

    def _get_connection(self) -> MySQLConnectionType:
        """Lazily create and return MySQL connection. Never returns None."""
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
                logger.info("MySQL connection established")
            except Error as e:
                logger.error(f"MySQL connection failed: {str(e)}")
                raise DatabaseConnectionError(
                    f"Cannot connect to MySQL at {self.host}:{self.port}. {str(e)}"
                )
        return self._connection

    def save_chunk(self, chunk_id: str, content: str, vector_id: str, metadata: Dict[str, Any]) -> bool:
        """Save a text chunk with vector reference."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = """
                INSERT INTO chunks (chunk_id, content, vector_id, metadata)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE content=VALUES(content), metadata=VALUES(metadata)
            """
            cursor.execute(query, (chunk_id, content, vector_id, str(metadata)))
            logger.info(f"Saved chunk: {chunk_id}")
            return True
        except Error as e:
            logger.error(f"Failed to save chunk: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to save chunk: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def get_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve chunk metadata by ID."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM chunks WHERE chunk_id = %s"
            cursor.execute(query, (chunk_id,))
            result: Optional[Dict[str, Any]] = cast(Optional[Dict[str, Any]], cursor.fetchone())
            return result
        except Error as e:
            logger.error(f"Failed to get chunk: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to get chunk: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def search_chunks(self, query_text: str, limit: int = 20) -> Sequence[Dict[str, Any]]:
        """Search chunks by content."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            sql = "SELECT * FROM chunks WHERE content LIKE %s LIMIT %s"
            cursor.execute(sql, (f"%{query_text}%", limit))
            results: Sequence[Dict[str, Any]] = cast(Sequence[Dict[str, Any]], cursor.fetchall())
            return results
        except Error as e:
            logger.error(f"Failed to search chunks: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to search chunks: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete chunk by ID."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            query = "DELETE FROM chunks WHERE chunk_id = %s"
            cursor.execute(query, (chunk_id,))
            logger.info(f"Deleted chunk: {chunk_id}")
            return True
        except Error as e:
            logger.error(f"Failed to delete chunk: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to delete chunk: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def list_all_chunks(self, limit: int = 100) -> Sequence[Dict[str, Any]]:
        """List all chunks with pagination."""
        cursor: Optional[Any] = None
        try:
            conn = self._get_connection()
            cursor = conn.cursor(dictionary=True)
            query = "SELECT * FROM chunks LIMIT %s"
            cursor.execute(query, (limit,))
            results: Sequence[Dict[str, Any]] = cast(Sequence[Dict[str, Any]], cursor.fetchall())
            return results
        except Error as e:
            logger.error(f"Failed to list chunks: {str(e)}")
            self._connection = None
            raise DatabaseOperationError(f"Failed to list chunks: {str(e)}")
        finally:
            if cursor is not None:
                cursor.close()

    def close(self) -> None:
        """Close database connection if open."""
        if self._connection is not None and self._connection.is_connected():
            self._connection.close()
            logger.info("MySQL connection closed")
            self._connection = None
