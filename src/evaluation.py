"""
Model Evaluation Module for Wings R Us Recommendation System
"""

import pandas as pd
import numpy as np
from typing import List, Union
import warnings
warnings.filterwarnings('ignore')

class ModelEvaluator:
    """
    Evaluates recommendation model performance
    """
    
    def __init__(self):
        pass
    
    def calculate_recall_at_k(self, predictions: pd.DataFrame, ground_truth: pd.Series, k: int = 3) -> float:
        """
        Calculate Recall@K metric
        
        Args:
            predictions: DataFrame with recommendation columns
            ground_truth: Series with true missing items
            k: Number of recommendations to consider (default: 3)
            
        Returns:
            Recall@K score
        """
        print(f"Calculating Recall@{k}...")
        
        if len(predictions) != len(ground_truth):
            print("❌ Length mismatch between predictions and ground truth")
            return 0.0
        
        correct_predictions = 0
        total_predictions = len(predictions)
        
        # Get recommendation columns
        rec_columns = [col for col in predictions.columns if 'RECOMMENDATION' in col.upper()]
        rec_columns = rec_columns[:k]  # Take only first k recommendations
        
        for idx, row in predictions.iterrows():
            true_item = ground_truth.iloc[idx]
            
            if pd.notna(true_item):
                true_item = str(true_item).strip().lower()
                
                # Check if true item is in any of the k recommendations
                found = False
                for col in rec_columns:
                    pred_item = row[col]
                    if pd.notna(pred_item):
                        pred_item = str(pred_item).strip().lower()
                        if pred_item == true_item:
                            found = True
                            break
                
                if found:
                    correct_predictions += 1
        
        recall_score = correct_predictions / total_predictions if total_predictions > 0 else 0.0
        
        print(f"  Correct predictions: {correct_predictions}/{total_predictions}")
        print(f"  Recall@{k}: {recall_score:.4f}")
        
        return recall_score
    
    def calculate_precision_at_k(self, predictions: pd.DataFrame, ground_truth: pd.Series, k: int = 3) -> float:
        """
        Calculate Precision@K metric
        
        Args:
            predictions: DataFrame with recommendation columns
            ground_truth: Series with true missing items
            k: Number of recommendations to consider
            
        Returns:
            Precision@K score
        """
        print(f"Calculating Precision@{k}...")
        
        # For this specific problem, Precision@K is the same as Recall@K
        # since we're predicting exactly one missing item
        return self.calculate_recall_at_k(predictions, ground_truth, k)
    
    def calculate_hit_rate(self, predictions: pd.DataFrame, ground_truth: pd.Series, k: int = 3) -> float:
        """
        Calculate Hit Rate@K (same as Recall@K for this problem)
        
        Args:
            predictions: DataFrame with recommendation columns
            ground_truth: Series with true missing items
            k: Number of recommendations to consider
            
        Returns:
            Hit Rate@K score
        """
        return self.calculate_recall_at_k(predictions, ground_truth, k)
    
    def analyze_recommendation_patterns(self, predictions: pd.DataFrame) -> dict:
        """
        Analyze patterns in recommendations
        
        Args:
            predictions: DataFrame with recommendations
            
        Returns:
            Dictionary with analysis results
        """
        print("Analyzing recommendation patterns...")
        
        analysis = {}
        
        # Get recommendation columns
        rec_columns = [col for col in predictions.columns if 'RECOMMENDATION' in col.upper()]
        
        # Most frequently recommended items
        all_recommendations = []
        for col in rec_columns:
            all_recommendations.extend(predictions[col].dropna().tolist())
        
        from collections import Counter
        item_counts = Counter(all_recommendations)
        analysis['most_recommended'] = dict(item_counts.most_common(10))
        
        # Diversity of recommendations
        unique_items = len(set(all_recommendations))
        total_recommendations = len(all_recommendations)
        analysis['diversity'] = unique_items / total_recommendations if total_recommendations > 0 else 0
        
        # Coverage (how many different items are recommended)
        analysis['coverage'] = unique_items
        
        print(f"  Most recommended items: {list(analysis['most_recommended'].keys())[:5]}")
        print(f"  Recommendation diversity: {analysis['diversity']:.4f}")
        print(f"  Item coverage: {analysis['coverage']} unique items")
        
        return analysis
    
    def generate_evaluation_report(self, predictions: pd.DataFrame, ground_truth: pd.Series = None) -> dict:
        """
        Generate comprehensive evaluation report
        
        Args:
            predictions: DataFrame with recommendations
            ground_truth: Optional series with true missing items
            
        Returns:
            Dictionary with evaluation metrics
        """
        print("\n📊 Generating Evaluation Report...")
        print("=" * 50)
        
        report = {}
        
        # Basic statistics
        report['total_predictions'] = len(predictions)
        report['recommendation_columns'] = [col for col in predictions.columns if 'RECOMMENDATION' in col.upper()]
        
        # Pattern analysis
        report['patterns'] = self.analyze_recommendation_patterns(predictions)
        
        # Performance metrics (if ground truth available)
        if ground_truth is not None:
            report['recall_at_1'] = self.calculate_recall_at_k(predictions, ground_truth, k=1)
            report['recall_at_2'] = self.calculate_recall_at_k(predictions, ground_truth, k=2)
            report['recall_at_3'] = self.calculate_recall_at_k(predictions, ground_truth, k=3)
            
            print(f"\n📈 Performance Metrics:")
            print(f"  Recall@1: {report['recall_at_1']:.4f}")
            print(f"  Recall@2: {report['recall_at_2']:.4f}")
            print(f"  Recall@3: {report['recall_at_3']:.4f}")
        
        return report
    
    def save_evaluation_report(self, report: dict, output_file: str) -> None:
        """
        Save evaluation report to file
        
        Args:
            report: Evaluation report dictionary
            output_file: Path to output file
        """
        try:
            import json
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            print(f"✅ Evaluation report saved to {output_file}")
        except Exception as e:
            print(f"❌ Error saving report: {str(e)}")
