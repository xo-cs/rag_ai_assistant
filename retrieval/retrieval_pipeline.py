# retrieval/retrieval_pipeline.py

from retrieval.query_embedder import QueryEmbedder
from retrieval.retriever import Retriever

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


class RetrievalPipeline:
    def __init__(self, 
                 faiss_index_path="faiss_index.bin",
                 top_k=5):

        self.embedder = QueryEmbedder()
        self.retriever = Retriever(
            faiss_index_path=faiss_index_path,
            top_k=top_k
        )

    def run(self, query: str):
        """
        Full RAG retrieval flow (without LLM yet):
        1) Embed query
        2) Retrieve chunks
        3) Build prompt
        """

        print("\n🔍 Embedding query...")
        query_vec = self.embedder.embed(query)

        print("🔎 Searching FAISS + MySQL...")
        retrieved_chunks = self.retriever.search(query_vec)

        if not retrieved_chunks:
            return "No relevant documents found."

        print("🧠 Building RAG prompt...")
        prompt = build_prompt(query, retrieved_chunks)

        return {
            "retrieved_chunks": retrieved_chunks,
            "prompt": prompt
        }