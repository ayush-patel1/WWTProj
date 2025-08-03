"""
Recommendation Engine for Wings R Us
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class RecommendationEngine:
    """
    Main recommendation engine that combines multiple approaches
    """
    
    def __init__(self):
        self.features = None
        self.trained = False
        self.item_similarity = {}
        self.popularity_scores = {}
        
    def train(self, features: Dict[str, Any]) -> None:
        """
        Train the recommendation model using engineered features
        
        Args:
            features: Dictionary containing all engineered features
        """
        print("Training recommendation model...")
        
        self.features = features
        
        # Calculate item similarity matrix
        self._calculate_item_similarity()
        
        # Calculate popularity scores
        self._calculate_popularity_scores()
        
        self.trained = True
        print("✅ Model training completed")
    
    def predict(self, test_data: pd.DataFrame, features: Dict[str, Any]) -> pd.DataFrame:
        """
        Generate recommendations for test data
        
        Args:
            test_data: DataFrame with partial orders
            features: Engineered features
            
        Returns:
            DataFrame with recommendations
        """
        if not self.trained:
            raise ValueError("Model must be trained before making predictions")
        
        print("Generating recommendations...")
        
        recommendations = []
        
        for idx, row in test_data.iterrows():
            # Extract items in the partial order
            order_items = self._extract_order_items(row)
            
            # Generate 3 recommendations
            recs = self._recommend_items(order_items, exclude_items=order_items)
            
            # Ensure we have exactly 3 recommendations
            while len(recs) < 3:
                recs.append("popular_item_fallback")  # Fallback
            
            recommendations.append({
                'CUSTOMER_ID': row.get('CUSTOMER_ID', idx),
                'ORDER_ID': row.get('ORDER_ID', idx),
                'item1': row.get('item1', ''),
                'item2': row.get('item2', ''),
                'item3': row.get('item3', ''),
                'RECOMMENDATION 1': recs[0],
                'RECOMMENDATION 2': recs[1], 
                'RECOMMENDATION 3': recs[2]
            })
        
        print(f"✅ Generated recommendations for {len(recommendations)} orders")
        return pd.DataFrame(recommendations)
    
    def _extract_order_items(self, order_row: pd.Series) -> List[str]:
        """Extract items from a test order row"""
        items = []
        
        # Look for item columns in the actual data structure
        item_columns = ['item1', 'item2', 'item3']
        
        for col in item_columns:
            if col in order_row.index:
                item = order_row[col]
                if pd.notna(item) and str(item).strip() and str(item) != 'nan':
                    items.append(str(item).strip())
        
        return items
    
    def _recommend_items(self, order_items: List[str], exclude_items: List[str] = None) -> List[str]:
        """
        Generate item recommendations based on current order items
        
        Args:
            order_items: List of items currently in the order
            exclude_items: Items to exclude from recommendations
            
        Returns:
            List of recommended items
        """
        if exclude_items is None:
            exclude_items = []
        
        recommendations = {}
        
        # Method 1: Co-occurrence based recommendations
        cooccurrence_recs = self._get_cooccurrence_recommendations(order_items, exclude_items)
        for item, score in cooccurrence_recs:
            recommendations[item] = recommendations.get(item, 0) + score * 0.4
        
        # Method 2: Market basket rules
        basket_recs = self._get_market_basket_recommendations(order_items, exclude_items)
        for item, score in basket_recs:
            recommendations[item] = recommendations.get(item, 0) + score * 0.3
        
        # Method 3: Category complementarity
        category_recs = self._get_category_recommendations(order_items, exclude_items)
        for item, score in category_recs:
            recommendations[item] = recommendations.get(item, 0) + score * 0.2
        
        # Method 4: Popularity fallback
        popularity_recs = self._get_popularity_recommendations(exclude_items)
        for item, score in popularity_recs:
            recommendations[item] = recommendations.get(item, 0) + score * 0.1
        
        # Sort by combined score and return top 3
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        return [item for item, score in sorted_recs[:3]]
    
    def _get_cooccurrence_recommendations(self, order_items: List[str], exclude_items: List[str]) -> List[Tuple[str, float]]:
        """Get recommendations based on item co-occurrence"""
        recommendations = defaultdict(float)
        
        cooccurrence = self.features.get('item_cooccurrence', {})
        
        for item in order_items:
            if item in cooccurrence:
                for related_item, score in cooccurrence[item].items():
                    if related_item not in exclude_items:
                        recommendations[related_item] += score
        
        return list(recommendations.items())
    
    def _get_market_basket_recommendations(self, order_items: List[str], exclude_items: List[str]) -> List[Tuple[str, float]]:
        """Get recommendations based on market basket rules"""
        recommendations = defaultdict(float)
        
        market_basket = self.features.get('market_basket', {})
        
        for item in order_items:
            if item in market_basket:
                for related_item, confidence in market_basket[item]:
                    if related_item not in exclude_items:
                        recommendations[related_item] += confidence
        
        return list(recommendations.items())
    
    def _get_category_recommendations(self, order_items: List[str], exclude_items: List[str]) -> List[Tuple[str, float]]:
        """Get recommendations based on category complementarity"""
        recommendations = defaultdict(float)
        
        item_categories = self.features.get('item_categories', {})
        
        # Determine categories in current order
        order_categories = set()
        for item in order_items:
            if item in item_categories:
                order_categories.add(item_categories[item])
        
        # Recommend items from complementary categories
        complementary_categories = self._get_complementary_categories(order_categories)
        
        for item, category in item_categories.items():
            if item not in exclude_items and category in complementary_categories:
                # Score based on item frequency within category
                item_freq = self.features.get('item_frequency', {}).get(item, 0)
                recommendations[item] += item_freq * 0.5
        
        return list(recommendations.items())
    
    def _get_complementary_categories(self, order_categories: set) -> set:
        """Determine complementary categories for an order"""
        # Define complementary category rules
        complementary_rules = {
            'wings': ['drinks', 'sides'],
            'drinks': ['wings', 'sides', 'desserts'],
            'sides': ['wings', 'drinks'],
            'desserts': ['drinks']
        }
        
        complementary = set()
        for category in order_categories:
            if category in complementary_rules:
                complementary.update(complementary_rules[category])
        
        # If no specific categories, recommend popular categories
        if not complementary:
            complementary = {'wings', 'drinks', 'sides'}
        
        return complementary
    
    def _get_popularity_recommendations(self, exclude_items: List[str]) -> List[Tuple[str, float]]:
        """Get recommendations based on item popularity"""
        recommendations = []
        
        item_frequency = self.features.get('item_frequency', {})
        
        for item, freq in item_frequency.items():
            if item not in exclude_items:
                recommendations.append((item, freq))
        
        # Return top 10 most popular items
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:10]
    
    def _calculate_item_similarity(self) -> None:
        """Calculate similarity between items"""
        print("  Calculating item similarity...")
        # This could be enhanced with more sophisticated similarity metrics
        pass
    
    def _calculate_popularity_scores(self) -> None:
        """Calculate popularity scores for items"""
        print("  Calculating popularity scores...")
        
        item_frequency = self.features.get('item_frequency', {})
        
        # Normalize popularity scores
        max_freq = max(item_frequency.values()) if item_frequency else 1
        self.popularity_scores = {item: freq/max_freq for item, freq in item_frequency.items()}
    
    def save_predictions(self, predictions: pd.DataFrame, output_file: str) -> None:
        """
        Save predictions to Excel file
        
        Args:
            predictions: DataFrame with recommendations
            output_file: Path to output Excel file
        """
        try:
            predictions.to_excel(output_file, index=False)
            print(f"✅ Predictions saved to {output_file}")
        except Exception as e:
            print(f"❌ Error saving predictions: {str(e)}")
            # Fallback to CSV
            csv_file = output_file.replace('.xlsx', '.csv')
            predictions.to_csv(csv_file, index=False)
            print(f"✅ Predictions saved to {csv_file} (CSV format)")
