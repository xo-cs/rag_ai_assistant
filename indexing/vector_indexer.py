# indexing/vector_indexer.py

import faiss
import numpy as np
from pathlib import Path

VECTOR_DIM = 1024  # bge-m3 dimension


class VectorIndexer:
    def __init__(self, index_path: str = "data/faiss_index.bin"):
        self.index_path = index_path
        Path("data").mkdir(exist_ok=True)

        # Create empty FAISS index
        self.index = faiss.IndexFlatL2(VECTOR_DIM)

    def add_vectors(self, vectors: np.ndarray):
        """
        Add embeddings to FAISS index.
        Returns assigned vector IDs.
        """
        vectors = np.array(vectors).astype("float32")

        start_id = self.index.ntotal  # current size before adding
        self.index.add(vectors)
        end_id = self.index.ntotal

        # Return list of new vector IDs
        return list(range(start_id, end_id))

    def save_index(self):
        faiss.write_index(self.index, self.index_path)

    def load_index(self):
        self.index = faiss.read_index(self.index_path)

    def get_index(self):
        return self.index