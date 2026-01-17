from retrieval.retrieval_pipeline import RetrievalPipeline

pipeline = RetrievalPipeline(faiss_index_path="data/faiss_index.bin", top_k=5)

query = "What is a transformer in power grid?"

result = pipeline.run(query)

print("\n=== RETRIEVED DOCUMENTS ===")
for r in result["retrieved_chunks"]:
    print(f"- {r['document_name']} | chunk_id: {r['chunk_id']}")

print("\n=== GENERATED PROMPT ===\n")
print(result["prompt"])