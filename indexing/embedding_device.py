# indexing/embedding_device.py

from sentence_transformers import SentenceTransformer
import numpy as np
import torch

class EmbeddingService:
    """
    Vector Embedding Service
    Forced to CPU for stability on M1 Air (8GB).
    """

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        # FORCE CPU: MPS (GPU) causes swapping/freezing on 8GB RAM for large batches
        self.device = "cpu"
        print(f"💻 Using CPU for {model_name} (Stable Mode)")

        self.model = SentenceTransformer(
            model_name,
            trust_remote_code=True,
            device=self.device
        )

    def embed_chunks(self, chunks):
        """
        Embed document chunks for indexing.
        """
        texts = [c["chunk_text"] for c in chunks]

        # CPU handles smaller batches better
        embeddings = self.model.encode(
            texts,
            batch_size=16, 
            show_progress_bar=True,
            normalize_embeddings=True,
            device=self.device
        )

        return np.array(embeddings)

    def embed_query(self, query: str):
        """
        Embed user query for retrieval.
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True,
            device=self.device
        )
        
        return embedding