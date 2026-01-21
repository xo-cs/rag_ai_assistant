# retrieval/hybrid_retrieval_pipeline.py

from retrieval.query_embedder import QueryEmbedder
from retrieval.hybrid_retriever import HybridRetriever

def build_prompt(query: str, retrieved_chunks: list) -> str:
    """
    Assemble retrieved context into a single prompt.
    """
    context = ""

    for i, chunk in enumerate(retrieved_chunks):
        context += f"\n--- Chunk {i+1} ---\n"
        context += f"Document: {chunk['document_name']}\n"
        context += f"Text:\n{chunk['chunk_text']}\n"

    prompt = f"""
You are an AI assistant for PowerSync.

Use ONLY the context below to answer the question.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:
"""
    return prompt


class HybridRetrievalPipeline:
    def __init__(self, 
                 faiss_index_path="data/faiss_index.bin",
                 top_k=5,
                 rrf_k=60):
        self.embedder = QueryEmbedder()
        self.retriever = HybridRetriever(
            faiss_index_path=faiss_index_path,
            top_k=top_k,
            rrf_k=rrf_k
        )

    def run(self, query: str):
        """
        Full RAG retrieval flow with hybrid search
        """
        print("\n🔍 Embedding query...")
        query_vec = self.embedder.embed(query)

        print("🔎 Hybrid search (BM25 + Vector)...")
        retrieved_chunks = self.retriever.search(query_vec, query)

        if not retrieved_chunks:
            return "No relevant documents found."

        print("🧠 Building RAG prompt...")
        prompt = build_prompt(query, retrieved_chunks)

        return {
            "retrieved_chunks": retrieved_chunks,
            "prompt": prompt
        }