# indexing/text_chunker.py

from pathlib import Path
import uuid
from indexing.document_loader import load_documents, DATA_DIR

def chunk_text(text: str, chunk_size: int = 600, overlap: int = 200):
    """
    Splits text into overlapping chunks.
    Overlap is CRITICAL for context preservation at boundaries.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        
        # Only add if chunk has meaningful content
        if len(chunk.strip()) > 50:
            chunks.append(chunk.strip())
        
        start = end - overlap
        if start < 0: start = 0
        
        # Break loop if we are at the end
        if end >= text_length:
            break

    return chunks

def chunk_documents(documents, min_chunk_length: int = 100):
    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        doc_name = doc.get("document_name", Path(doc["source"]).name)
        page_num = doc.get("page_num") 
        
        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc_name}_p{page_num}_{i}_{uuid.uuid4().hex[:6]}"
            page_section = f"Page {page_num}" if page_num else "N/A"
            
            chunk_data = {
                "chunk_id": chunk_id,
                "vector_id": -1,
                "document_name": doc_name,
                "page_or_section": page_section,
                "chunk_text": chunk
            }
            all_chunks.append(chunk_data)

    return all_chunks