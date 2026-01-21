# retrieval/hybrid_retriever.py

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from database.metadata_store import MetadataStore
from typing import List, Dict


class HybridRetriever:
    """
    Hybrid retrieval using Reciprocal Rank Fusion (RRF) - the industry standard
    """
    
    def __init__(self, 
                 faiss_index_path="data/faiss_index.bin",
                 top_k=5,
                 rrf_k=60, 
                 **kwargs):
        """
        rrf_k: RRF smoothing constant (60 is industry standard)
        """
        # Load FAISS index
        self.index = faiss.read_index(faiss_index_path)
        
        # Connect to MySQL
        self.metadata_store = MetadataStore()
        
        self.top_k = top_k
        self.rrf_k = rrf_k
        
        # Load all chunks for BM25
        self._load_bm25_index()
    
    def _load_bm25_index(self):
        """
        Load all chunks and build BM25 index
        """
        print("📚 Building BM25 index from database...")
        
        # Fetch all chunks from MySQL
        query = "SELECT vector_id, chunk_text, document_name FROM document_chunks ORDER BY vector_id"
        self.metadata_store.cursor.execute(query)
        all_chunks = self.metadata_store.cursor.fetchall()
        
        # Tokenize texts for BM25
        self.chunk_map = {}  # vector_id -> chunk info
        tokenized_corpus = []
        
        for chunk in all_chunks:
            vector_id = chunk['vector_id']
            
            # Simple but effective tokenization
            tokens = chunk['chunk_text'].lower().split()
            
            tokenized_corpus.append(tokens)
            self.chunk_map[vector_id] = {
                'text': chunk['chunk_text'],
                'document_name': chunk['document_name']
            }
        
        # Build BM25 index
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.vector_ids = list(self.chunk_map.keys())
        
        print(f"✅ BM25 index built with {len(tokenized_corpus)} chunks")
    
    def _reciprocal_rank_fusion(self, vector_ranks: Dict[int, int], bm25_ranks: Dict[int, int]) -> List[int]:
        """
        Combine rankings using Reciprocal Rank Fusion (RRF)
        RRF Score = sum(1 / (k + rank)) for each retrieval method
        
        This is the industry-standard method that ignores raw scores
        and focuses on rank positions instead.
        """
        rrf_scores = {}
        
        # Add vector search ranks
        for vector_id, rank in vector_ranks.items():
            rrf_scores[vector_id] = 1.0 / (self.rrf_k + rank)
        
        # Add BM25 ranks
        for vector_id, rank in bm25_ranks.items():
            if vector_id in rrf_scores:
                rrf_scores[vector_id] += 1.0 / (self.rrf_k + rank)
            else:
                rrf_scores[vector_id] = 1.0 / (self.rrf_k + rank)
        
        # Sort by RRF score (higher is better)
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top-k vector IDs
        return [vid for vid, _ in sorted_results[:self.top_k]]
    
    def search(self, query_vector: np.ndarray, query_text: str):
        """
        Hybrid search using RRF to combine BM25 and vector search
        """
        # 1. FAISS vector search - get top 20 candidates
        k_retrieve = min(20, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k_retrieve)
        
        # Create rank map for vector search (rank 1 = best)
        vector_ranks = {}
        for rank, idx in enumerate(indices[0], start=1):
            if idx != -1:
                vector_ranks[int(idx)] = rank
        
        # 2. BM25 search - get top 20 candidates
        query_tokens = query_text.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        
        # Get top-k BM25 results
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:k_retrieve]
        
        # Create rank map for BM25 (rank 1 = best)
        bm25_ranks = {}
        for rank, idx in enumerate(bm25_top_indices, start=1):
            vector_id = self.vector_ids[idx]
            bm25_ranks[vector_id] = rank
        
        # 3. Combine using RRF
        top_vector_ids = self._reciprocal_rank_fusion(vector_ranks, bm25_ranks)
        
        if not top_vector_ids:
            return []
        
        # 4. Fetch metadata from MySQL
        results = self.metadata_store.fetch_by_vector_ids(top_vector_ids)
        
        # Sort results to match RRF order
        results_dict = {r['vector_id']: r for r in results}
        sorted_results = [results_dict[vid] for vid in top_vector_ids if vid in results_dict]
        
        return sorted_results