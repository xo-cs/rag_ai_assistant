import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from app.services.rag_service import RAGService
from app.repositories.mysql_repository import DatabaseConnectionError, DatabaseOperationError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])


class DocumentRequest(BaseModel):
    """Request model for document storage."""
    doc_id: str
    title: str
    content: str
    embedding_id: str


class DocumentResponse(BaseModel):
    """Response model for document operations."""
    success: bool
    message: str
    doc_id: Optional[str] = None


class DocumentMetadata(BaseModel):
    """Document metadata response."""
    doc_id: str
    title: str
    content: str
    metadata: Optional[dict] = None


class SearchRequest(BaseModel):
    """Request model for document search."""
    query: str
    limit: int = 10


def get_rag_service() -> RAGService:
    """Factory function to create RAGService per request."""
    service = RAGService()
    return service


@router.post("/store", response_model=DocumentResponse)
async def store_document(
    request: DocumentRequest,
    service: RAGService = Depends(get_rag_service)
) -> DocumentResponse:
    """
    Store a document with metadata and embedding reference.
    Service and database connection are created per request.
    """
    try:
        result = service.store_document(
            request.doc_id,
            request.title,
            request.content,
            request.embedding_id
        )
        service.cleanup()
        return DocumentResponse(**result)
    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later."
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to store document. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@router.get("/retrieve/{doc_id}", response_model=DocumentMetadata)
async def retrieve_document(
    doc_id: str,
    service: RAGService = Depends(get_rag_service)
) -> DocumentMetadata:
    """Retrieve document metadata by ID."""
    try:
        result = service.retrieve_document(doc_id)
        service.cleanup()
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {doc_id} not found."
            )
        return DocumentMetadata(**result)
    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later."
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve document. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@router.post("/search")
async def search_documents(
    request: SearchRequest,
    service: RAGService = Depends(get_rag_service)
) -> dict:
    """Search documents by query text."""
    try:
        results = service.search_documents(request.query, request.limit)
        service.cleanup()
        return {
            "query": request.query,
            "count": len(results),
            "documents": results
        }
    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later."
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to search documents. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )


@router.delete("/delete/{doc_id}", response_model=DocumentResponse)
async def delete_document(
    doc_id: str,
    service: RAGService = Depends(get_rag_service)
) -> DocumentResponse:
    """Delete document metadata by ID."""
    try:
        success = service.delete_document(doc_id)
        service.cleanup()
        return DocumentResponse(
            success=success,
            message="Document deleted successfully",
            doc_id=doc_id
        )
    except DatabaseConnectionError as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database service unavailable. Please try again later."
        )
    except DatabaseOperationError as e:
        logger.error(f"Database operation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete document. Please try again."
        )
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred."
        )
