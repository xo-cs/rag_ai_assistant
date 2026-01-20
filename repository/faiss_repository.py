import faiss
import numpy as np
from typing import List, Tuple
from config.settings import settings


class FAISSRepository:
    def __init__(self):
        self.index = None
        self.load_index()
    
    def load_index(self):
        """Load FAISS index from disk."""
        try:
            self.index = faiss.read_index(settings.faiss_index_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load FAISS index: {str(e)}")
    
    def search(self, query_embedding: np.ndarray, k: int) -> Tuple[List[int], List[float]]:
        """
        Search for top-k similar vectors in FAISS index.
        
        Args:
            query_embedding: Query vector (1, embedding_dim)
            k: Number of results
            
        Returns:
            Tuple of (chunk_ids, distances)
        """
        if self.index is None:
            raise RuntimeError("FAISS index not loaded")
        
        # Ensure query is float32 and properly shaped
        query_embedding = np.array([query_embedding], dtype=np.float32)
        
        distances, indices = self.index.search(query_embedding, k)
        
        return indices[0].tolist(), distances[0].tolist()
