# indexing/indexing_pipeline.py

from pathlib import Path

from indexing.document_loader import load_documents, DATA_DIR 
from indexing.text_chunker import chunk_documents
from indexing.embedding_device import EmbeddingService
from indexing.vector_indexer import VectorIndexer
from database.metadata_store import MetadataStore


def run_indexing():
    print("🚀 Starting full indexing pipeline...\n")

    # ---------- STEP 1: LOAD DOCUMENTS ----------
    docs = load_documents(DATA_DIR)
    print(f"📄 Loaded {len(docs)} documents")

    # ---------- STEP 2: CHUNK DOCUMENTS ----------
    chunks = chunk_documents(docs)
    print(f"🧩 Created {len(chunks)} chunks")

    if not chunks:
        print("❌ No chunks created — stopping.")
        return

    # ---------- STEP 3: EMBEDDINGS ----------
    embedder = EmbeddingService()

    print("\n🧠 Generating embeddings with BAAI/bge-m3...")
    embeddings = embedder.embed_chunks(chunks)
    print(f"Embeddings shape: {embeddings.shape}")

    # ---------- STEP 4: FAISS INDEXING ----------
    indexer = VectorIndexer(index_path="data/faiss_index.bin")

    print("\n📌 Adding vectors to FAISS index...")
    vector_ids = indexer.add_vectors(embeddings)

    # Assign vector IDs back to chunks
    for chunk, vid in zip(chunks, vector_ids):
        chunk["vector_id"] = vid

    print(f"Saved {len(vector_ids)} vectors to FAISS.")

    # ---------- STEP 5: SAVE TO MYSQL ----------
    print("\n💾 Saving chunk metadata to MySQL...")
    
    db = MetadataStore()
    
    for chunk in chunks:
        db.insert_chunk_metadata(chunk)
    
    db.close()
    
    print(f"✅ Saved {len(chunks)} chunks to MySQL database.")

    # Save FAISS index
    indexer.save_index()
    print("💾 FAISS index saved to data/faiss_index.bin")

    # ---------- STATS ----------
    lengths = [len(c["chunk_text"]) for c in chunks]
    print("\n📊 Chunk statistics:")
    print("Min length:", min(lengths))
    print("Max length:", max(lengths))
    print("Avg length:", sum(lengths) // len(lengths))

    # Show sample
    print("\n🧪 Sample chunk AFTER indexing:")
    print({
        "chunk_id": chunks[0]["chunk_id"],
        "vector_id": chunks[0]["vector_id"],
        "document": chunks[0]["document_name"],
        "text_preview": chunks[0]["chunk_text"][:200] + "..."
    })

    print("\n✅ INDEXING COMPLETE.")


if __name__ == "__main__":
    run_indexing()