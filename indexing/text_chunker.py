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
    Returns chunks formatted for database insertion.
    Each chunk should have:
    - chunk_id (unique string)
    - vector_id (will be set later after FAISS indexing)
    - document_name (file name)
    - page_or_section (page number if available)
    - chunk_text (the actual text)
    """
    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        doc_name = Path(doc["source"]).name  # Extract filename
        
        # Try to extract page number from source if available
        page_section = None
        if "page" in doc.get("metadata", {}):
            page_section = f"Page {doc['metadata'].get('page')}"
        elif hasattr(doc, 'metadata') and doc.metadata:
            # Try other metadata formats
            page_section = doc.metadata.get("page_number", doc.metadata.get("page", None))
        
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) < min_chunk_length:
                continue  # DROP tiny chunks

            # Create unique chunk ID (you can use doc_id + index or UUID)
            chunk_id = f"{doc_name}_{i}_{uuid.uuid4().hex[:8]}"
            
            # Format for database
            chunk_data = {
                "chunk_id": chunk_id,
                "vector_id": -1,  # Will be updated after FAISS indexing
                "document_name": doc_name,
                "page_or_section": page_section,
                "chunk_text": chunk
            }
            
            all_chunks.append(chunk_data)

    return all_chunks


def prepare_for_database(chunks):
    """
    Convert chunks to database-ready format.
    Returns list of tuples for batch insertion.
    """
    db_records = []
    for chunk in chunks:
        record = (
            chunk["chunk_id"],
            chunk["vector_id"],  # This will be -1 initially
            chunk["document_name"],
            chunk.get("page_or_section"),
            chunk["chunk_text"]
        )
        db_records.append(record)
    return db_records


if __name__ == "__main__":
    # Test the chunker
    docs = load_documents(DATA_DIR)
    chunks = chunk_documents(docs)

    print(f"Total documents: {len(docs)}")
    print(f"Total chunks: {len(chunks)}")

    if chunks:
        print("\n📋 Sample chunk (database format):")
        print(f"chunk_id: {chunks[0]['chunk_id']}")
        print(f"document_name: {chunks[0]['document_name']}")
        print(f"page_or_section: {chunks[0]['page_or_section']}")
        print(f"text (first 200 chars): {chunks[0]['chunk_text'][:200]}...")
    
    # Print database-ready format
    db_records = prepare_for_database(chunks[:3])  # First 3 only for demo
    print(f"\n📦 First 3 records ready for database insertion:")
    for i, record in enumerate(db_records):
        print(f"Record {i+1}: {record}")