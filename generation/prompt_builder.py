# generation/prompt_builder.py

def build_rag_prompt(query: str, retrieved_chunks: list) -> str:
    """
    Assemble retrieved context into a single prompt for the LLM.
    """
    context = ""

    for i, chunk in enumerate(retrieved_chunks):
        context += f"\n--- Document {i+1} ---\n"
        context += f"Source: {chunk['document_name']}\n"
        if chunk.get('page_or_section'):
            context += f"Section: {chunk['page_or_section']}\n"
        context += f"Content:\n{chunk['chunk_text']}\n"

    # CHANGED: Added strict language instruction
    prompt = f"""You are a helpful AI assistant specializing in power grid and energy systems.

Use ONLY the information provided in the context below to answer the question. 
If the context doesn't contain relevant information, say "I don't have enough information in the provided documents to answer this question."

IMPORTANT INSTRUCTIONS:
1. Be precise and technical.
2. Cite which document you're referencing (e.g., "According to Document 1...").
3. **LANGUAGE:** Answer in the SAME language as the user's question. If the question is in Korean, you MUST answer in Korean.

CONTEXT:
{context}

QUESTION:
{query}

ANSWER:"""
    
    return prompt