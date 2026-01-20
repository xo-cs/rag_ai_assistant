import logging
from typing import Sequence, Dict, Any, Optional
from app.repositories.metadata_repository import (
    MetadataRepository,
    DatabaseConnectionError,
    DatabaseOperationError
)

logger = logging.getLogger(__name__)


class RAGService:
    """Service layer for RAG operations. No DB connections at instantiation."""

    def __init__(self) -> None:
        """Initialize service without creating repository or DB connections."""
        self._repository: Optional[MetadataRepository] = None

    def _get_repository(self) -> MetadataRepository:
        """Lazily initialize repository on first use."""
        if self._repository is None:
            self._repository = MetadataRepository()
        return self._repository

    def ingest_chunk(self, chunk_id: str, content: str, vector_id: str) -> Dict[str, Any]:
        """
        Store a text chunk with its vector reference.
        Database connection occurs on first call.
        """
        try:
            repo = self._get_repository()
            metadata: Dict[str, Any] = {"status": "indexed", "vector_id": vector_id}
            success = repo.save_chunk(chunk_id, content, vector_id, metadata)
            return {
                "success": success,
                "chunk_id": chunk_id,
                "message": "Chunk ingested successfully"
            }
        except DatabaseConnectionError as e:
            logger.error(f"Connection error during ingestion: {str(e)}")
            raise
        except DatabaseOperationError as e:
            logger.error(f"Operation error during ingestion: {str(e)}")
            raise

    def retrieve_chunk(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve chunk by ID."""
        try:
            repo = self._get_repository()
            return repo.get_chunk(chunk_id)
        except DatabaseConnectionError as e:
            logger.error(f"Connection error during retrieval: {str(e)}")
            raise
        except DatabaseOperationError as e:
            logger.error(f"Operation error during retrieval: {str(e)}")
            raise

    def search_knowledge_base(self, query: str, limit: int = 20) -> Sequence[Dict[str, Any]]:
        """Search knowledge base by query text."""
        try:
            repo = self._get_repository()
            return repo.search_chunks(query, limit)
        except DatabaseConnectionError as e:
            logger.error(f"Connection error during search: {str(e)}")
            raise
        except DatabaseOperationError as e:
            logger.error(f"Operation error during search: {str(e)}")
            raise

    def remove_chunk(self, chunk_id: str) -> bool:
        """Delete chunk from knowledge base."""
        try:
            repo = self._get_repository()
            return repo.delete_chunk(chunk_id)
        except DatabaseConnectionError as e:
            logger.error(f"Connection error during deletion: {str(e)}")
            raise
        except DatabaseOperationError as e:
            logger.error(f"Operation error during deletion: {str(e)}")
            raise

    def list_chunks(self, limit: int = 100) -> Sequence[Dict[str, Any]]:
        """List all chunks in knowledge base."""
        try:
            repo = self._get_repository()
            return repo.list_all_chunks(limit)
        except DatabaseConnectionError as e:
            logger.error(f"Connection error during listing: {str(e)}")
            raise
        except DatabaseOperationError as e:
            logger.error(f"Operation error during listing: {str(e)}")
            raise

    def cleanup(self) -> None:
        """Close repository connection if open."""
        if self._repository is not None:
            self._repository.close()
