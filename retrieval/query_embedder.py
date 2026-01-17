# retrieval/query_embedder.py

from indexing.embedding_device import EmbeddingService
import numpy as np

class QueryEmbedder:
    def __init__(self, model_name="BAAI/bge-m3"):
        self.embedder = EmbeddingService(model_name)

    def embed(self, query: str) -> np.ndarray:
        """
        Convert user query into vector.
        Output shape: (1, dim)
        """
        vec = self.embedder.embed_query(query)
        return np.array([vec]).astype("float32")