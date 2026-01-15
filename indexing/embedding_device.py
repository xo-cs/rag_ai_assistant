# indexing/embedding_service.py

from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    """
    Vector Embedding Service
    Uses BAAI/bge-m3 for multilingual dense retrieval
    """

    def __init__(self, model_name: str = "BAAI/bge-m3"):
        self.model = SentenceTransformer(
            model_name,
            trust_remote_code=True  # required for bge-m3
        )

    def embed_chunks(self, chunks):
        """
        Embed document chunks for indexing.
        chunks: List[dict] with key 'text'
        """
        texts = [c["text"] for c in chunks]

        embeddings = self.model.encode(
            texts,
            batch_size=16,
            show_progress_bar=True,
            normalize_embeddings=True
        )

        return np.array(embeddings)

    def embed_query(self, query: str):
        """
        Embed user query for retrieval.
        """
        embedding = self.model.encode(
            query,
            normalize_embeddings=True
        )

        return embedding