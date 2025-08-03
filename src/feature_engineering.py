"""
Feature Engineering Module for Wings R Us Recommendation System
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    """
    Creates features for the recommendation system
    """
    
    def __init__(self):
        self.item_frequency = {}
        self.item_cooccurrence = {}
        self.customer_preferences = {}
        self.store_patterns = {}
    
    def create_features(self, data: Dict[str, pd.DataFrame]) -> Dict[str, any]:
        """
        Create all features needed for recommendation
        
        Args:
            data: Dictionary containing all cleaned DataFrames
            
        Returns:
            Dictionary containing engineered features
        """
        print("Creating features...")
        
        features = {}
        
        # Extract basic features
        features['item_frequency'] = self._calculate_item_frequency(data['orders'])
        features['item_cooccurrence'] = self._calculate_item_cooccurrence(data['orders'])
        features['customer_preferences'] = self._analyze_customer_preferences(data['orders'], data['customers'])
        features['store_patterns'] = self._analyze_store_patterns(data['orders'], data['stores'])
        features['market_basket'] = self._create_market_basket_rules(data['orders'])
        
        # Create item categories (if not provided, infer from names)
        features['item_categories'] = self._categorize_items(data['orders'])
        
        print("✅ Feature engineering completed")
        return features
    
    def _calculate_item_frequency(self, orders_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate frequency of each item"""
        print("  Calculating item frequencies...")
        
        if 'item_name' not in orders_df.columns:
            print("    Warning: 'item_name' column not found")
            return {}
        
        total_items = len(orders_df)
        item_counts = orders_df['item_name'].value_counts()
        item_frequency = (item_counts / total_items).to_dict()
        
        print(f"    Found {len(item_frequency)} unique items")
        return item_frequency
    
    def _calculate_item_cooccurrence(self, orders_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate how often items appear together in orders"""
        print("  Calculating item co-occurrence...")
        
        if 'order_id' not in orders_df.columns or 'item_name' not in orders_df.columns:
            print("    Warning: Required columns not found")
            return {}
        
        # Group items by order
        order_items = orders_df.groupby('order_id')['item_name'].apply(list).to_dict()
        
        cooccurrence = defaultdict(lambda: defaultdict(int))
        total_pairs = 0
        
        # Calculate co-occurrence for each order
        for order_id, items in order_items.items():
            unique_items = list(set(items))  # Remove duplicates within order
            
            # For each pair of items in the order
            for i, item1 in enumerate(unique_items):
                for j, item2 in enumerate(unique_items):
                    if i != j:  # Don't count item with itself
                        cooccurrence[item1][item2] += 1
                        total_pairs += 1
        
        # Convert to probabilities
        cooccurrence_prob = {}
        for item1, item2_dict in cooccurrence.items():
            cooccurrence_prob[item1] = {}
            for item2, count in item2_dict.items():
                cooccurrence_prob[item1][item2] = count / total_pairs if total_pairs > 0 else 0
        
        print(f"    Calculated co-occurrence for {len(cooccurrence_prob)} items")
        return dict(cooccurrence_prob)
    
    def _analyze_customer_preferences(self, orders_df: pd.DataFrame, customers_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze preferences by customer type"""
        print("  Analyzing customer preferences...")
        
        if 'customer_id' not in orders_df.columns:
            print("    Warning: 'customer_id' column not found in orders")
            return {}
        
        # Merge orders with customer data
        if 'customer_id' in customers_df.columns:
            merged_df = orders_df.merge(customers_df, on='customer_id', how='left')
        else:
            print("    Warning: 'customer_id' column not found in customers")
            return {}
        
        preferences = {}
        
        # Analyze by customer type
        if 'customer_type' in merged_df.columns and 'item_name' in merged_df.columns:
            for customer_type in merged_df['customer_type'].unique():
                if pd.notna(customer_type):
                    type_orders = merged_df[merged_df['customer_type'] == customer_type]
                    item_counts = type_orders['item_name'].value_counts()
                    total_items = len(type_orders)
                    
                    preferences[customer_type] = (item_counts / total_items).to_dict()
        
        print(f"    Analyzed preferences for {len(preferences)} customer types")
        return preferences
    
    def _analyze_store_patterns(self, orders_df: pd.DataFrame, stores_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze ordering patterns by store/channel"""
        print("  Analyzing store patterns...")
        
        patterns = {}
        
        # Merge with store data if available
        if 'store_id' in orders_df.columns and 'store_id' in stores_df.columns:
            merged_df = orders_df.merge(stores_df, on='store_id', how='left')
            
            # Analyze by channel
            if 'channel' in merged_df.columns and 'item_name' in merged_df.columns:
                for channel in merged_df['channel'].unique():
                    if pd.notna(channel):
                        channel_orders = merged_df[merged_df['channel'] == channel]
                        item_counts = channel_orders['item_name'].value_counts()
                        total_items = len(channel_orders)
                        
                        patterns[channel] = (item_counts / total_items).to_dict()
        
        print(f"    Analyzed patterns for {len(patterns)} channels")
        return patterns
    
    def _create_market_basket_rules(self, orders_df: pd.DataFrame) -> Dict[str, List[Tuple[str, float]]]:
        """Create association rules (simplified market basket analysis)"""
        print("  Creating market basket rules...")
        
        if 'order_id' not in orders_df.columns or 'item_name' not in orders_df.columns:
            return {}
        
        # Group items by order
        order_items = orders_df.groupby('order_id')['item_name'].apply(list).to_dict()
        
        # Calculate support for each item
        item_support = defaultdict(int)
        total_orders = len(order_items)
        
        for items in order_items.values():
            for item in set(items):
                item_support[item] += 1
        
        # Convert to probabilities
        item_support = {item: count/total_orders for item, count in item_support.items()}
        
        # Calculate confidence: P(B|A) = P(A,B) / P(A)
        rules = defaultdict(list)
        
        for order_id, items in order_items.items():
            unique_items = list(set(items))
            
            for i, item_a in enumerate(unique_items):
                for j, item_b in enumerate(unique_items):
                    if i != j:
                        # Calculate confidence
                        confidence = self.item_cooccurrence.get(item_a, {}).get(item_b, 0) / item_support.get(item_a, 0.001)
                        
                        if confidence > 0.1:  # Minimum confidence threshold
                            rules[item_a].append((item_b, confidence))
        
        # Sort rules by confidence
        for item in rules:
            rules[item] = sorted(rules[item], key=lambda x: x[1], reverse=True)[:10]  # Top 10 rules per item
        
        print(f"    Created rules for {len(rules)} items")
        return dict(rules)
    
    def _categorize_items(self, orders_df: pd.DataFrame) -> Dict[str, str]:
        """Categorize items based on their names (wings, drinks, sides, etc.)"""
        print("  Categorizing items...")
        
        if 'item_name' not in orders_df.columns:
            return {}
        
        categories = {}
        
        # Define category keywords
        category_keywords = {
            'wings': ['wing', 'chicken', 'buffalo', 'bbq', 'hot', 'mild', 'spicy'],
            'drinks': ['drink', 'soda', 'cola', 'sprite', 'juice', 'water', 'beer', 'coffee', 'tea'],
            'sides': ['fries', 'onion', 'rings', 'salad', 'coleslaw', 'bread', 'dip', 'sauce'],
            'desserts': ['ice cream', 'cake', 'cookie', 'brownie', 'pie', 'dessert']
        }
        
        items = orders_df['item_name'].unique()
        
        for item in items:
            if pd.notna(item):
                item_lower = str(item).lower()
                categorized = False
                
                for category, keywords in category_keywords.items():
                    if any(keyword in item_lower for keyword in keywords):
                        categories[item] = category
                        categorized = True
                        break
                
                if not categorized:
                    categories[item] = 'other'
        
        print(f"    Categorized {len(categories)} items")
        return categories
