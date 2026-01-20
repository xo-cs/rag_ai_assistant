from pydantic import BaseModel, Field
from typing import List


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=1000)
    top_k: int = Field(default=5, ge=1, le=50)


class SourceChunk(BaseModel):
    chunk_id: str
    document: str


class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceChunk]
