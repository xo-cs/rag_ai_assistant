# indexing/text_chunker.py

from pathlib import Path
import uuid
from indexing.document_loader import load_documents, DATA_DIR


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100
):
    """
    Splits text into overlapping chunks.
    """
    chunks = []
    start = 0
    text_length = len(text)

    while start < text_length:
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk.strip())
        start = end - overlap

        if start < 0:
            start = 0

    return chunks


def chunk_documents(documents, min_chunk_length: int = 100):
    """
    Returns chunks formatted for database insertion with EXACT page numbers.
    """
    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        doc_name = doc.get("document_name", Path(doc["source"]).name)
        page_num = doc.get("page_number")  # Exact page number from PDF
        
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) < min_chunk_length:
                continue

            # Create unique chunk ID
            chunk_id = f"{doc_name}_page{page_num}_chunk{i}_{uuid.uuid4().hex[:6]}"
            
            # Use exact page number
            if page_num:
                page_section = f"Page {page_num}"
            else:
                page_section = "N/A"
            
            # Format for database
            chunk_data = {
                "chunk_id": chunk_id,
                "vector_id": -1,
                "document_name": doc_name,
                "page_or_section": page_section,
                "chunk_text": chunk
            }
            
            all_chunks.append(chunk_data)

    return all_chunks


def prepare_for_database(chunks):
    """
    Convert chunks to database-ready format.
    """
    db_records = []
    for chunk in chunks:
        record = (
            chunk["chunk_id"],
            chunk["vector_id"],
            chunk["document_name"],
            chunk.get("page_or_section"),
            chunk["chunk_text"]
        )
        db_records.append(record)
    return db_records


if __name__ == "__main__":
    docs = load_documents(DATA_DIR)
    chunks = chunk_documents(docs)

    print(f"Total document pages: {len(docs)}")
    print(f"Total chunks: {len(chunks)}")

    if chunks:
        print("\n📋 Sample chunk:")
        print(f"chunk_id: {chunks[0]['chunk_id']}")
        print(f"document_name: {chunks[0]['document_name']}")
        print(f"page_or_section: {chunks[0]['page_or_section']}")
        print(f"text preview: {chunks[0]['chunk_text'][:200]}...")