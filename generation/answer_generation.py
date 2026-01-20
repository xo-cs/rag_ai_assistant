# generation/answer_generation.py

from generation.llm_builder import LLMBuilder
from generation.prompt_builder import build_rag_prompt
from retrieval.retrieval_pipeline import RetrievalPipeline

class AnswerGenerator:
    def __init__(self, faiss_index_path="data/faiss_index.bin", top_k=5):
        self.retrieval_pipeline = RetrievalPipeline(
            faiss_index_path=faiss_index_path,
            top_k=top_k
        )
        self.llm = LLMBuilder(model_name="llama3.1:8b")
    
    def generate_answer(self, query: str):
        """
        Full RAG pipeline: Retrieve + Generate
        """
        print(f"\n🔍 Query: {query}\n")
        
        # Step 1: Retrieve relevant chunks
        print("📚 Retrieving relevant documents...")
        retrieval_result = self.retrieval_pipeline.run(query)
        
        if not retrieval_result["retrieved_chunks"]:
            return {
                "query": query,
                "answer": "No relevant documents found in the database.",
                "sources": []
            }
        
        print(f"✅ Found {len(retrieval_result['retrieved_chunks'])} relevant chunks\n")
        
        # Step 2: Build RAG prompt
        print("🧠 Building prompt...")
        prompt = build_rag_prompt(query, retrieval_result["retrieved_chunks"])
        
        # Step 3: Generate answer with LLM
        print("🤖 Generating answer with Llama 3.1-8B...\n")
        answer = self.llm.generate(prompt)
        
        return {
            "query": query,
            "answer": answer,
            "sources": [
                {
                    "document": chunk["document_name"],
                    "chunk_id": chunk["chunk_id"],
                    "page_or_section": chunk.get("page_or_section", "N/A")
                }
                for chunk in retrieval_result["retrieved_chunks"]
            ]
        }


# Test function
if __name__ == "__main__":
    print("🚀 Starting RAG Answer Generation Test...\n")
    
    generator = AnswerGenerator()
    
    # Test query
    query = "What are the challenges of renewable energy in power systems?"
    result = generator.generate_answer(query)
    
    print("\n" + "=" * 80)
    print("📝 ANSWER:")
    print("=" * 80)
    print(result["answer"])
    print("\n" + "=" * 80)
    print("📚 SOURCES:")
    print("=" * 80)
    for i, source in enumerate(result["sources"], 1):
        print(f"{i}. Document: {source['document']}")
        print(f"   Chunk ID: {source['chunk_id']}")
        print(f"   Section: {source['page_or_section']}\n")