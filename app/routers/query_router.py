import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.rag_service import RAGService
from app.repositories.metadata_repository import DatabaseConnectionError, DatabaseOperationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/knowledge", tags=["knowledge-base"])


class ChunkRequest(BaseModel):
    """Request model for chunk ingestion."""
    chunk_id: str
    content: str
    vector_id: str


class ChunkResponse(BaseModel):
    """Response model for chunk operations."""
    chunk_id: str
    content: Optional[str] = None
    vector_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class SearchRequest(BaseModel):
    """Request model for knowledge base search."""
    query: str
    limit: int = 20


class OperationResponse(BaseModel):
    """Generic operation response."""
    success: bool
    message: str
    chunk_id: Optional[str] = None


def get_rag_service() -> RAGService:
    """Factory to create RAGService per request. No DB connection at import time."""
    return RAGService()


@router.post("/ingest", response_model=OperationResponse)
async def ingest_chunk(
    request: ChunkRequest,
    service: RAGService = Depends(get_rag_service)
) -> OperationResponse:
    """Ingest a text chunk into the knowledge base."""
    try:
        result = service.ingest_chunk(request.chunk_id, request.content, request.vector_id)
        service.cleanup()
        return OperationResponse(**result)
    except DatabaseConnectionError as e:
        logger.error(f"Database unavailable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to ingest chunk"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/chunk/{chunk_id}", response_model=ChunkResponse)
async def get_chunk(
    chunk_id: str,
    service: RAGService = Depends(get_rag_service)
) -> ChunkResponse:
    """Retrieve a chunk by ID."""
    try:
        result = service.retrieve_chunk(chunk_id)
        service.cleanup()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Chunk {chunk_id} not found"
            )
        return ChunkResponse(**result)
    except DatabaseConnectionError as e:
        logger.error(f"Database unavailable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve chunk"
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post("/search")
async def search_knowledge_base(
    request: SearchRequest,
    service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """Search the knowledge base by query text."""
    try:
        results = service.search_knowledge_base(request.query, request.limit)
        service.cleanup()
        return {
            "query": request.query,
            "count": len(results),
            "chunks": list(results)
        }
    except DatabaseConnectionError as e:
        logger.error(f"Database unavailable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search knowledge base"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.delete("/chunk/{chunk_id}", response_model=OperationResponse)
async def delete_chunk(
    chunk_id: str,
    service: RAGService = Depends(get_rag_service)
) -> OperationResponse:
    """Delete a chunk from the knowledge base."""
    try:
        success = service.remove_chunk(chunk_id)
        service.cleanup()
        return OperationResponse(
            success=success,
            message="Chunk deleted successfully",
            chunk_id=chunk_id
        )
    except DatabaseConnectionError as e:
        logger.error(f"Database unavailable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete chunk"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.get("/list")
async def list_all_chunks(
    limit: int = 100,
    service: RAGService = Depends(get_rag_service)
) -> Dict[str, Any]:
    """List all chunks in the knowledge base."""
    try:
        chunks = service.list_chunks(limit)
        service.cleanup()
        return {
            "count": len(chunks),
            "chunks": list(chunks)
        }
    except DatabaseConnectionError as e:
        logger.error(f"Database unavailable: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable"
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list chunks"
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )
