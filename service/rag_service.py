from repository.faiss_repository import FAISSRepository
from repository.metadata_repository import MetadataRepository
from service.embedding_service import EmbeddingService
from service.llm_service import LLMService
from models.query_models import QueryResponse, SourceChunk
from config.settings import settings


class RAGService:
    def __init__(self):
        self.faiss_repo = FAISSRepository()
        self.metadata_repo = MetadataRepository()
        self.embedding_service = EmbeddingService()
        self.llm_service = LLMService()
    
    def query(self, question: str, top_k: int = None) -> QueryResponse:
        """
        Execute RAG query pipeline.
        
        Args:
            question: User query
            top_k: Number of chunks to retrieve
            
        Returns:
            QueryResponse with answer and sources
        """
        if top_k is None:
            top_k = settings.default_top_k
        
        # Step 1: Generate query embedding
        query_embedding = self.embedding_service.embed(question)
        
        # Step 2: Retrieve top-k chunks from FAISS
        chunk_ids, distances = self.faiss_repo.search(query_embedding, top_k)
        
        # Step 3: Fetch chunk metadata from MySQL
        chunk_metadata = self.metadata_repo.get_chunk_metadata(chunk_ids)
        
        # Step 4: Build grounded prompt
        context = self._build_context(chunk_metadata)
        prompt = self._build_prompt(question, context)
        
        # Step 5: Call local LLM
        answer = self.llm_service.generate(prompt)
        
        # Step 6: Format response
        sources = [
            SourceChunk(
                chunk_id=str(chunk["chunk_id"]),
                document=chunk["document_name"]
            )
            for chunk in chunk_metadata
        ]
        
        return QueryResponse(answer=answer, sources=sources)
    
    def _build_context(self, chunk_metadata: list) -> str:
        """Build context from retrieved chunks."""
        context_parts = []
        for i, chunk in enumerate(chunk_metadata, 1):
            context_parts.append(
                f"[Document {i}] {chunk['document_name']}\n{chunk['chunk_text']}"
            )
        return "\n\n".join(context_parts)
    
    def _build_prompt(self, question: str, context: str) -> str:
        """Build deterministic prompt format."""
        prompt = f"""You are a helpful assistant. Use the provided context to answer the question.

Context:
{context}

Question: {question}

Answer:"""
        return prompt
