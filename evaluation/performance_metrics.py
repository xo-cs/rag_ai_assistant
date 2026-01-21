# evaluation/performance_metrics.py

import numpy as np
from typing import List, Dict, Set


class PerformanceMetrics:
    """
    Calculate various retrieval performance metrics (all return 0-1 range)
    """
    
    @staticmethod
    def precision_at_k(retrieved: List[str], relevant: Set[str], k: int = 5) -> float:
        """Precision@K: fraction of retrieved docs that are relevant"""
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & relevant)
        return relevant_retrieved / k if k > 0 else 0.0
    
    @staticmethod
    def recall_at_k(retrieved: List[str], relevant: Set[str], k: int = 5) -> float:
        """Recall@K: fraction of relevant docs that were retrieved"""
        retrieved_k = retrieved[:k]
        relevant_retrieved = len(set(retrieved_k) & relevant)
        return relevant_retrieved / len(relevant) if len(relevant) > 0 else 0.0
    
    @staticmethod
    def f1_at_k(retrieved: List[str], relevant: Set[str], k: int = 5) -> float:
        """F1@K: Harmonic mean of Precision and Recall"""
        precision = PerformanceMetrics.precision_at_k(retrieved, relevant, k)
        recall = PerformanceMetrics.recall_at_k(retrieved, relevant, k)
        
        if precision + recall == 0:
            return 0.0
        
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def average_precision(retrieved: List[str], relevant: Set[str]) -> float:
        """
        Average Precision for Information Retrieval
        FIXED: Only considers retrieved documents, not all possible documents
        Returns 0-1 range
        
        Formula: AP = (sum of P@k * rel(k)) / number of relevant docs
        where P@k is precision at position k, rel(k) is 1 if doc at k is relevant
        """
        if not relevant or not retrieved:
            return 0.0
        
        num_relevant = 0
        sum_precisions = 0.0
        
        # Iterate through retrieved documents
        for i, doc in enumerate(retrieved, 1):
            if doc in relevant:
                num_relevant += 1
                # Precision at this position
                precision_at_i = num_relevant / i
                sum_precisions += precision_at_i
        
        # Average over number of relevant docs (min of relevant docs and retrieved docs)
        total_relevant = len(relevant)
        
        if num_relevant == 0:
            return 0.0
        
        # CRITICAL FIX: Divide by total relevant, not num_relevant
        return sum_precisions / total_relevant
    
    @staticmethod
    def ndcg_at_k(retrieved: List[str], relevant: Set[str], k: int = 5) -> float:
        """
        Normalized Discounted Cumulative Gain@K
        Returns 0-1 range
        """
        retrieved_k = retrieved[:k]
        
        # Calculate DCG (binary relevance: 1 if relevant, 0 if not)
        dcg = 0.0
        for i, doc in enumerate(retrieved_k, 1):
            if doc in relevant:
                dcg += 1.0 / np.log2(i + 1)
        
        # Calculate IDCG (ideal DCG - all relevant docs at top, UP TO K!)
        idcg = 0.0
        num_ideal = min(len(relevant), k)
        for i in range(1, num_ideal + 1):
            idcg += 1.0 / np.log2(i + 1)
        
        if idcg == 0:
            return 1.0 if dcg == 0 else 0.0
        
        ndcg = dcg / idcg
        return min(ndcg, 1.0)  # Cap at 1.0
    
    @staticmethod
    def reciprocal_rank(retrieved: List[str], relevant: Set[str]) -> float:
        """Reciprocal Rank: 1 / rank of first relevant doc"""
        for i, doc in enumerate(retrieved, 1):
            if doc in relevant:
                return 1.0 / i
        return 0.0
    
    @staticmethod
    def calculate_all_metrics(retrieved: List[str], relevant: Set[str], k: int = 5) -> Dict:
        """
        Calculate all metrics at once
        All metrics return values between 0 and 1
        """
        return {
            "precision@k": PerformanceMetrics.precision_at_k(retrieved, relevant, k),
            "recall@k": PerformanceMetrics.recall_at_k(retrieved, relevant, k),
            "f1@k": PerformanceMetrics.f1_at_k(retrieved, relevant, k),
            "ndcg@k": PerformanceMetrics.ndcg_at_k(retrieved, relevant, k),
            "average_precision": PerformanceMetrics.average_precision(retrieved, relevant),
            "reciprocal_rank": PerformanceMetrics.reciprocal_rank(retrieved, relevant)
        }


def test_metrics():
    """Test the metrics with sample data"""
    print("=" * 60)
    print("PERFORMANCE METRICS TEST")
    print("=" * 60)
    
    # Test case 1: Perfect ranking
    retrieved1 = ["doc2", "doc4", "doc6", "doc1", "doc3"]
    relevant1 = {"doc2", "doc4", "doc6"}
    metrics1 = PerformanceMetrics.calculate_all_metrics(retrieved1, relevant1, k=5)
    print(f"\nTest 1 - Perfect ranking (all relevant at top):")
    print(f"Retrieved: {retrieved1}")
    print(f"Relevant: {relevant1}")
    for metric_name, value in metrics1.items():
        print(f"  {metric_name}: {value:.4f} ({value*100:.2f}%)")
    
    # Test case 2: Mixed ranking
    retrieved2 = ["doc1", "doc2", "doc3", "doc4", "doc5"]
    relevant2 = {"doc2", "doc4", "doc6"}
    metrics2 = PerformanceMetrics.calculate_all_metrics(retrieved2, relevant2, k=5)
    print(f"\nTest 2 - Mixed ranking:")
    print(f"Retrieved: {retrieved2}")
    print(f"Relevant: {relevant2}")
    for metric_name, value in metrics2.items():
        print(f"  {metric_name}: {value:.4f} ({value*100:.2f}%)")
    
    print("=" * 60)


if __name__ == "__main__":
    test_metrics()