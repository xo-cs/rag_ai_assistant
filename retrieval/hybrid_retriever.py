# retrieval/hybrid_retriever.py

import faiss
import numpy as np
import torch
from rank_bm25 import BM25Okapi
from database.metadata_store import MetadataStore
from sentence_transformers import CrossEncoder
from typing import List, Dict, Optional
import os

class HybridRetriever:
    def __init__(self, 
                 faiss_index_path="data/faiss_index.bin",
                 top_k=10, 
                 rrf_k=60, 
                 **kwargs):
        self.metadata_store = MetadataStore()
        self.top_k = top_k
        self.rrf_k = rrf_k
        
        if os.path.exists(faiss_index_path):
            self.index = faiss.read_index(faiss_index_path)
        else:
            self.index = None
            print("⚠️ Warning: FAISS index not found.")

        # --- OPTIMIZATION: USE MPS (GPU) ---
        device = "cpu"
        if torch.backends.mps.is_available():
            device = "mps"
            print("⚡ Reranker using MPS (Mac GPU) acceleration")
        elif torch.cuda.is_available():
            device = "cuda"
        
        print("🧠 Loading Reranker Model...")
        self.reranker = CrossEncoder('BAAI/bge-reranker-v2-m3', default_activation_function=None, device=device)

        self._load_bm25_index()
    
    def _load_bm25_index(self):
        print("📚 Building BM25 index...")
        query = "SELECT vector_id, chunk_text, document_name FROM document_chunks ORDER BY vector_id"
        self.metadata_store.cursor.execute(query)
        all_chunks = self.metadata_store.cursor.fetchall()
        
        self.chunk_map = {} 
        tokenized_corpus = []
        
        if not all_chunks:
            self.bm25 = None
            self.vector_ids = []
            return

        for chunk in all_chunks:
            vector_id = chunk['vector_id']
            tokens = chunk['chunk_text'].lower().split()
            tokenized_corpus.append(tokens)
            
            self.chunk_map[vector_id] = {
                'text': chunk['chunk_text'], 
                'document_name': chunk['document_name']
            }
        
        self.bm25 = BM25Okapi(tokenized_corpus)
        self.vector_ids = list(self.chunk_map.keys())
        print(f"✅ BM25 index built with {len(tokenized_corpus)} chunks")
    
    def _reciprocal_rank_fusion(self, vector_ranks: Dict[int, int], bm25_ranks: Dict[int, int]) -> List[int]:
        rrf_scores = {}
        for vector_id, rank in vector_ranks.items():
            rrf_scores[vector_id] = 1.0 / (self.rrf_k + rank)
        for vector_id, rank in bm25_ranks.items():
            if vector_id in rrf_scores:
                rrf_scores[vector_id] += 1.0 / (self.rrf_k + rank)
            else:
                rrf_scores[vector_id] = 1.0 / (self.rrf_k + rank)
        sorted_results = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
        return [vid for vid, _ in sorted_results]
    
    def search(self, query_vector: np.ndarray, query_text: str, target_document: Optional[str] = None):
        if not self.index or not self.bm25:
            return []

        # --- LATENCY FIX ---
        # Reduced from 150 to 50. 
        # This makes the Reranker run 3x faster.
        k_retrieve = 50 
        k_retrieve = min(k_retrieve, self.index.ntotal)
        
        if k_retrieve == 0: return []

        # Vector Search
        distances, indices = self.index.search(query_vector, k_retrieve)
        vector_ranks = {int(idx): rank for rank, idx in enumerate(indices[0], start=1) if idx != -1}
        
        # BM25 Search
        query_tokens = query_text.lower().split()
        bm25_scores = self.bm25.get_scores(query_tokens)
        bm25_top_indices = np.argsort(bm25_scores)[::-1][:k_retrieve]
        bm25_ranks = {self.vector_ids[idx]: rank for rank, idx in enumerate(bm25_top_indices, start=1)}
        
        # Fusion
        ranked_vector_ids = self._reciprocal_rank_fusion(vector_ranks, bm25_ranks)
        
        # Fetch Content
        results = self.metadata_store.fetch_by_vector_ids(ranked_vector_ids)
        results_dict = {r['vector_id']: r for r in results}
        
        # Filter Candidates
        candidates = []
        for vid in ranked_vector_ids:
            if vid in results_dict:
                chunk = results_dict[vid]
                if target_document and chunk['document_name'] != target_document:
                    continue
                candidates.append(chunk)

        if not candidates:
            return []

        # 2. RERANKING (GPU Accelerated)
        rerank_pairs = [[query_text, c['chunk_text']] for c in candidates]
        
        # Predict scores
        scores = self.reranker.predict(rerank_pairs, batch_size=32, show_progress_bar=False)
        
        for i, chunk in enumerate(candidates):
            chunk['score'] = scores[i]
            
        # Sort by Reranker Score
        reranked_results = sorted(candidates, key=lambda x: x['score'], reverse=True)
        
        return reranked_results[:self.top_k]