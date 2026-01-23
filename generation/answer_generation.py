# generation/answer_generation.py

from generation.llm_builder import LLMBuilder
from generation.prompt_builder import build_rag_prompt
from retrieval.retrieval_pipeline import RetrievalPipeline

class AnswerGenerator:
    def __init__(self, faiss_index_path="data/faiss_index.bin", top_k=10):
        # Set top_k to 10 to maximize Hit Rate
        self.retrieval_pipeline = RetrievalPipeline(
            faiss_index_path=faiss_index_path,
            top_k=top_k
        )
        self.llm = LLMBuilder() 
    
    def generate_answer(self, query: str, model_name: str = "qwen2.5:3b", target_document: str = None):
        print(f"\n🔍 Query: {query} | Model: {model_name} | Doc: {target_document}\n")
        
        retrieval_result = self.retrieval_pipeline.retriever.search(
            self.retrieval_pipeline.embedder.embed(query), 
            query,
            target_document=target_document
        )
        
        if not retrieval_result:
            return {
                "query": query,
                "answer": "No relevant information found in the selected scope.",
                "sources": []
            }
        
        print(f"✅ Retrieved {len(retrieval_result)} chunks for context.")
        
        print("🧠 Building prompt...")
        prompt = build_rag_prompt(query, retrieval_result)
        
        print(f"🤖 Generating answer with {model_name}...\n")
        answer = self.llm.generate(prompt, model_name=model_name)
        
        return {
            "query": query,
            "answer": answer,
            "sources": [
                {
                    "document": chunk["document_name"],
                    "chunk_id": chunk["chunk_id"],
                    "page_or_section": chunk.get("page_or_section", "N/A")
                }
                for chunk in retrieval_result
            ]
        }