from fastapi import APIRouter, HTTPException, Depends
from models.query_models import QueryRequest, QueryResponse
from service.rag_service import RAGService

router = APIRouter(prefix="/api", tags=["query"])


def get_rag_service() -> RAGService:
    """Dependency injection for RAGService - creates instance per request."""
    return RAGService()


@router.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest, service: RAGService = Depends(get_rag_service)) -> QueryResponse:
    """
    Execute RAG query.
    
    Args:
        request: QueryRequest with question and top_k
        
    Returns:
        QueryResponse with answer and sources
        
    Raises:
        HTTPException: On any processing error
    """
    try:
        response = service.query(
            question=request.question,
            top_k=request.top_k
        )
        return response
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
