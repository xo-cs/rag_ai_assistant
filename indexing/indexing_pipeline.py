# indexing/indexing_pipeline.py

import time
from pathlib import Path

from indexing.document_loader import load_documents, DATA_DIR 
from indexing.text_chunker import chunk_documents
from indexing.embedding_device import EmbeddingService
from indexing.vector_indexer import VectorIndexer
from database.metadata_store import MetadataStore

def run_indexing():
    print("🚀 Starting CLEAN Indexing Pipeline (No Context Generation)...\n")

    # 1. Load Documents
    docs = load_documents(DATA_DIR)
    print(f"📄 Loaded {len(docs)} pages")

    # 2. Chunk Documents
    chunks = chunk_documents(docs)
    print(f"🧩 Created {len(chunks)} chunks")

    if not chunks:
        print("❌ No chunks created.")
        return

    # 3. Embeddings (CPU/MPS)
    print("\n🧠 Generating embeddings (Raw Text)...")
    embedder = EmbeddingService()
    embeddings = embedder.embed_chunks(chunks)

    # 4. Save to FAISS & MySQL
    print("\n💾 Saving to Vector Store & Database...")
    
    indexer = VectorIndexer(index_path="data/faiss_index.bin")
    # Reset index for clean slate
    import faiss
    indexer.index = faiss.IndexFlatL2(1024) 
    vector_ids = indexer.add_vectors(embeddings)

    for chunk, vid in zip(chunks, vector_ids):
        chunk["vector_id"] = vid

    db = MetadataStore()
    # Clear old data
    db.cursor.execute("TRUNCATE TABLE document_chunks") 
    db.conn.commit()
    
    for chunk in chunks:
        # Pass empty string for context since we aren't using it
        chunk['chunk_context'] = "" 
        db.insert_chunk_metadata(chunk)
    
    db.close()
    indexer.save_index()
    print(f"\n✅ INDEXING COMPLETE. ({len(chunks)} chunks)")

if __name__ == "__main__":
    run_indexing()