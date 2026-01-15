from metadata_store import MetadataStore

db = MetadataStore()

test_chunk = {
    "chunk_id": "test_chunk_python",
    "vector_id": 99,
    "document_name": "test_doc.pdf",
    "page_or_section": "Page 1",
    "chunk_text": "This chunk was inserted from Python."
}

db.insert_chunk_metadata(test_chunk)

rows = db.fetch_by_vector_ids([99])
print(rows)

db.close()