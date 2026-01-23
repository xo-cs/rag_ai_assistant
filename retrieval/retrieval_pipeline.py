# retrieval/retrieval_pipeline.py

from retrieval.query_embedder import QueryEmbedder
from retrieval.hybrid_retriever import HybridRetriever
from generation.query_processor import QueryProcessor # <--- NEW

class RetrievalPipeline:
    def __init__(self, 
                 faiss_index_path="data/faiss_index.bin",
                 top_k=10):
        self.embedder = QueryEmbedder()
        self.retriever = HybridRetriever(
            faiss_index_path=faiss_index_path,
            top_k=top_k
        )
        self.query_processor = QueryProcessor() # <--- NEW

    def run(self, query: str, target_document: str = None):
        """
        Full retrieval flow: Expand -> Embed -> Search -> Rerank
        """
        # 1. Expand Query (Add synonyms/keywords)
        expanded_query = self.query_processor.expand_query(query)
        
        # 2. Embed the EXPANDED query
        query_vec = self.embedder.embed(expanded_query)

        # 3. Search using the EXPANDED query text (for BM25) and vector
        retrieved_chunks = self.retriever.search(
            query_vec, 
            expanded_query, 
            target_document=target_document
        )

        return {
            "retrieved_chunks": retrieved_chunks,
            "original_query": query,
            "expanded_query": expanded_query
        }