# indexing/text_chunker.py

from pathlib import Path
from document_loader import load_documents, DATA_DIR


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
    all_chunks = []

    for doc in documents:
        chunks = chunk_text(doc["text"])
        for i, chunk in enumerate(chunks):
            chunk = chunk.strip()
            if len(chunk) < min_chunk_length:
                continue  # DROP tiny chunks

            all_chunks.append({
                "doc_id": doc["doc_id"],
                "chunk_id": f"{doc['doc_id']}_{i}",
                "text": chunk,
                "source": doc["source"]
            })

    return all_chunks



if name == "__main__":
    docs = load_documents(DATA_DIR)
    chunks = chunk_documents(docs)

    print(f"Total documents: {len(docs)}")
    print(f"Total chunks: {len(chunks)}")

    if chunks:
        print("\nSample chunk:\n")
        print(chunks[0]["text"][:500])
lengths = [len(c["text"]) for c in chunks]

print("Min length:", min(lengths))
print("Max length:", max(lengths))
print("Avg length:", sum(lengths) // len(lengths))