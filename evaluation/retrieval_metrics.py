# evaluation/retrieval_metrics.py

import json
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
        """
        Calculate Hit Rate @ K with detailed performance metrics
        """
        total_queries = len(test_queries)
        hits = 0
        
        results = []
        
        # Aggregate metrics
        all_precision = []
        all_recall = []
        all_f1 = []
        all_ndcg = []
        all_ap = []
        
        for item in test_queries:
            query = item["query"]
            relevant_docs = set(item["relevant_docs"])
            
            # Retrieve documents
            retrieval_result = self.pipeline.run(query)
            retrieved_chunks = retrieval_result["retrieved_chunks"]
            
            # --- FIX START: Deduplicate Documents ---
            # We only care about the FIRST time a document appears.
            # If we retrieve 3 chunks from 'pdf1.pdf', it counts as 1 retrieval at the highest rank.
            raw_docs = [chunk["document_name"] for chunk in retrieved_chunks]
            retrieved_docs = []
            seen = set()
            for doc in raw_docs:
                if doc not in seen:
                    retrieved_docs.append(doc)
                    seen.add(doc)
            # --- FIX END ---
            
            # Check if ANY relevant doc is in retrieved docs
            hit = len(relevant_docs & set(retrieved_docs)) > 0
            
            if hit:
                hits += 1
            
            # Calculate detailed metrics for this query
            metrics_detail = PerformanceMetrics.calculate_all_metrics(
                retrieved_docs, 
                relevant_docs, 
                k=self.top_k
            )
            
            # Aggregate for averaging
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
        """
        Mean Reciprocal Rank - bonus metric
        """
        reciprocal_ranks = []
        
        for item in test_queries:
            query = item["query"]
            relevant_docs = set(item["relevant_docs"])
            
            retrieval_result = self.pipeline.run(query)
            retrieved_chunks = retrieval_result["retrieved_chunks"]
            
            # Find position of first relevant doc
            rank = 0
            # Deduplicate for MRR as well
            seen_docs = set()
            current_rank = 1
            
            for chunk in retrieved_chunks:
                doc_name = chunk["document_name"]
                if doc_name in seen_docs:
                    continue
                seen_docs.add(doc_name)
                
                if doc_name in relevant_docs:
                    rank = current_rank
                    break
                current_rank += 1
            
            if rank > 0:
                reciprocal_ranks.append(1.0 / rank)
            else:
                reciprocal_ranks.append(0.0)
        
        mrr = sum(reciprocal_ranks) / len(reciprocal_ranks)
        return mrr * 100


def run_evaluation():
    """
    Run full evaluation and print results
    """
    print("🔍 Loading test queries...\n")
    
    with open("evaluation/test_queries.json", "r", encoding="utf-8") as f:
        test_queries = json.load(f)
    
    print(f"📊 Evaluating with {len(test_queries)} test queries\n")
    
    evaluator = RetrievalEvaluator(top_k=10)
    
    print("🧮 Calculating metrics...\n")
    metrics = evaluator.calculate_hit_rate(test_queries)
    
    print("=" * 80)
    print("📈 EVALUATION RESULTS")
    print("=" * 80)
    print(f"Hit Rate @ {metrics['k']}: {metrics['hit_rate']:.2f}%")
    print(f"Total Queries: {metrics['total_queries']}")
    print(f"Successful Hits: {metrics['total_hits']}")
    print(f"Misses: {metrics['total_queries'] - metrics['total_hits']}")
    print("\n" + "-" * 80)
    print("DETAILED METRICS")
    print("-" * 80)
    print(f"Average Precision @ {metrics['k']}: {metrics['avg_precision']*100:.2f}%")
    print(f"Average Recall @ {metrics['k']}: {metrics['avg_recall']*100:.2f}%")
    print(f"Average F1 @ {metrics['k']}: {metrics['avg_f1']*100:.2f}%")
    print(f"Average NDCG @ {metrics['k']}: {metrics['avg_ndcg']*100:.2f}%")
    print(f"Mean Average Precision (MAP): {metrics['map']*100:.2f}%")
    print("=" * 80)
    
    # Calculate MRR
    mrr = evaluator.calculate_mrr(test_queries)
    print(f"\n📍 Mean Reciprocal Rank (MRR): {mrr:.2f}%")
    
    # Save results to file
    with open("evaluation/evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump({
            "hit_rate": metrics["hit_rate"],
            "mrr": mrr,
            "k": metrics["k"],
            "total_queries": metrics["total_queries"],
            "avg_precision": metrics["avg_precision"],
            "avg_recall": metrics["avg_recall"],
            "avg_f1": metrics["avg_f1"],
            "avg_ndcg": metrics["avg_ndcg"],
            "map": metrics["map"],
            "details": metrics["details"]
        }, f, indent=2, ensure_ascii=False)
    
    print("\n💾 Results saved to evaluation/evaluation_results.json")
    
    return metrics


if __name__ == "__main__":
    run_evaluation()