# evaluation/retrieval_metrics.py

import json
import time
from tqdm import tqdm # <--- Progress Bar
from retrieval.retrieval_pipeline import RetrievalPipeline
from evaluation.performance_metrics import PerformanceMetrics
from typing import List, Dict

class RetrievalEvaluator:
    def __init__(self, faiss_index_path="data/faiss_index.bin", top_k=10):
        self.pipeline = RetrievalPipeline(
            faiss_index_path=faiss_index_path,
            top_k=top_k
        )
        self.top_k = top_k
    
    def calculate_hit_rate(self, test_queries: List[Dict]) -> Dict:
        total_queries = len(test_queries)
        hits = 0
        results = []
        
        # Metrics
        all_precision = []
        all_recall = []
        all_f1 = []
        all_ndcg = []
        all_ap = []
        
        print(f"🚀 Starting Evaluation on {total_queries} queries...")
        
        # Use TQDM for a nice progress bar
        for item in tqdm(test_queries, desc="Evaluating"):
            query = item["query"]
            relevant_docs = set(item["relevant_docs"])
            
            # Retrieve
            retrieval_result = self.pipeline.run(query)
            retrieved_chunks = retrieval_result["retrieved_chunks"]
            
            # Deduplicate
            raw_docs = [chunk["document_name"] for chunk in retrieved_chunks]
            retrieved_docs = []
            seen = set()
            for doc in raw_docs:
                if doc not in seen:
                    retrieved_docs.append(doc)
                    seen.add(doc)
            
            # Check Hit
            hit = len(relevant_docs & set(retrieved_docs)) > 0
            if hit:
                hits += 1
            
            # Calculate Metrics
            metrics_detail = PerformanceMetrics.calculate_all_metrics(
                retrieved_docs, 
                relevant_docs, 
                k=self.top_k
            )
            
            all_precision.append(metrics_detail["precision@k"])
            all_recall.append(metrics_detail["recall@k"])
            all_f1.append(metrics_detail["f1@k"])
            all_ndcg.append(metrics_detail["ndcg@k"])
            all_ap.append(metrics_detail["average_precision"])
            
            results.append({
                "query": query,
                "relevant_docs": list(relevant_docs),
                "retrieved_docs": retrieved_docs,
                "hit": hit,
                "metrics": metrics_detail
            })
        
        hit_rate = (hits / total_queries) * 100
        
        return {
            "hit_rate": hit_rate,
            "total_queries": total_queries,
            "total_hits": hits,
            "k": self.top_k,
            "avg_precision": sum(all_precision) / len(all_precision),
            "avg_recall": sum(all_recall) / len(all_recall),
            "avg_f1": sum(all_f1) / len(all_f1),
            "avg_ndcg": sum(all_ndcg) / len(all_ndcg),
            "map": sum(all_ap) / len(all_ap),
            "details": results
        }
    
    def calculate_mrr(self, test_queries: List[Dict]) -> float:
        reciprocal_ranks = []
        for item in test_queries:
            query = item["query"]
            relevant_docs = set(item["relevant_docs"])
            retrieval_result = self.pipeline.run(query)
            retrieved_chunks = retrieval_result["retrieved_chunks"]
            
            rank = 0
            seen_docs = set()
            current_rank = 1
            for chunk in retrieved_chunks:
                doc_name = chunk["document_name"]
                if doc_name in seen_docs: continue
                seen_docs.add(doc_name)
                if doc_name in relevant_docs:
                    rank = current_rank
                    break
                current_rank += 1
            
            if rank > 0:
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)
        
        return (sum(reciprocal_ranks) / len(reciprocal_ranks)) * 100

def run_evaluation():
    with open("evaluation/test_queries.json", "r", encoding="utf-8") as f:
        test_queries = json.load(f)
    
    evaluator = RetrievalEvaluator(top_k=10)
    metrics = evaluator.calculate_hit_rate(test_queries)
    
    print("\n" + "=" * 60)
    print("📈 EVALUATION RESULTS")
    print("=" * 60)
    print(f"Hit Rate @ {metrics['k']}: {metrics['hit_rate']:.2f}%")
    print(f"MAP: {metrics['map']*100:.2f}%")
    print(f"NDCG @ {metrics['k']}: {metrics['avg_ndcg']*100:.2f}%")
    
    mrr = evaluator.calculate_mrr(test_queries)
    print(f"MRR: {mrr:.2f}%")
    print("=" * 60)
    
    with open("evaluation/evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_evaluation()