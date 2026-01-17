# retrieval/retriever.py

import faiss
import numpy as np
from database.metadata_store import MetadataStore

class Retriever:
    def __init__(self, 
                 faiss_index_path="faiss_index.bin",
                 top_k=5):
        # Load FAISS index built during indexing
        self.index = faiss.read_index(faiss_index_path)

        # Connect to MySQL metadata store
        self.metadata_store = MetadataStore()

        self.top_k = top_k

    def search(self, query_vector: np.ndarray):
        """
        1) Search FAISS
        2) Get vector IDs
        3) Fetch metadata from MySQL
        """

        # Step 1: FAISS search
        distances, indices = self.index.search(query_vector, self.top_k)

        vector_ids = indices[0].tolist()

        # Remove invalid IDs
        vector_ids = [vid for vid in vector_ids if vid != -1]

        if not vector_ids:
            return []

        # Step 2: Fetch chunk metadata from MySQL
        results = self.metadata_store.fetch_by_vector_ids(vector_ids)

        return results