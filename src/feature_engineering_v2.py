"""
Updated Feature Engineering Module for Wings R Us Recommendation System
Adapted for real data structure
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from collections import defaultdict, Counter
import warnings
warnings.filterwarnings('ignore')

class FeatureEngineer:
    """
    Creates features for the recommendation system using real data structure
    """
    
    def __init__(self):
        self.item_frequency = {}
        self.item_cooccurrence = {}
        self.customer_preferences = {}
        self.channel_patterns = {}
    
    def create_features(self, data: Dict[str, pd.DataFrame]) -> Dict[str, any]:
        """
        Create all features needed for recommendation
        
        Args:
            data: Dictionary containing all cleaned DataFrames
            
        Returns:
            Dictionary containing engineered features
        """
        print("Creating features from test data and supporting datasets...")
        
        features = {}
        
        # Since order_data.csv is very large, we'll work primarily with test_data_question
        # and extract patterns from the test data and supporting datasets
        
        # Extract item frequency from test data
        features['item_frequency'] = self._calculate_item_frequency_from_test(data['test'])
        
        # Calculate item co-occurrence from test data
        features['item_cooccurrence'] = self._calculate_item_cooccurrence_from_test(data['test'])
        
        # Analyze customer preferences
        features['customer_preferences'] = self._analyze_customer_preferences_from_test(data['test'])
        
        # Analyze channel patterns
        features['channel_patterns'] = self._analyze_channel_patterns(data['test'])
        
        # Create item categories
        features['item_categories'] = self._categorize_items_from_test(data['test'])
        
        # Create market basket rules
        features['market_basket'] = self._create_market_basket_rules_from_test(data['test'])
        
        print("✅ Feature engineering completed")
        return features
    
    def _calculate_item_frequency_from_test(self, test_df: pd.DataFrame) -> Dict[str, float]:
        """Calculate frequency of each item from test data"""
        print("  Calculating item frequencies from test data...")
        
        all_items = []
        item_columns = ['item1', 'item2', 'item3']
        
        for col in item_columns:
            if col in test_df.columns:
                items = test_df[col].dropna().astype(str)
                items = items[items != 'nan']
                all_items.extend(items.tolist())
        
        if not all_items:
            return {}
        
        total_items = len(all_items)
        item_counts = Counter(all_items)
        item_frequency = {item: count/total_items for item, count in item_counts.items()}
        
        print(f"    Found {len(item_frequency)} unique items")
        return item_frequency
    
    def _calculate_item_cooccurrence_from_test(self, test_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Calculate how often items appear together in test orders"""
        print("  Calculating item co-occurrence from test data...")
        
        cooccurrence = defaultdict(lambda: defaultdict(int))
        total_pairs = 0
        
        item_columns = ['item1', 'item2', 'item3']
        
        for idx, row in test_df.iterrows():
            # Get items in this order
            order_items = []
            for col in item_columns:
                if col in row and pd.notna(row[col]) and str(row[col]) != 'nan':
                    order_items.append(str(row[col]))
            
            # Calculate co-occurrence for this order
            for i, item1 in enumerate(order_items):
                for j, item2 in enumerate(order_items):
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
    
    def _analyze_customer_preferences_from_test(self, test_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze preferences by customer type from test data"""
        print("  Analyzing customer preferences from test data...")
        
        if 'CUSTOMER_TYPE' not in test_df.columns:
            return {}
        
        preferences = {}
        item_columns = ['item1', 'item2', 'item3']
        
        for customer_type in test_df['CUSTOMER_TYPE'].unique():
            if pd.notna(customer_type):
                type_orders = test_df[test_df['CUSTOMER_TYPE'] == customer_type]
                
                # Collect all items for this customer type
                all_items = []
                for col in item_columns:
                    if col in type_orders.columns:
                        items = type_orders[col].dropna().astype(str)
                        items = items[items != 'nan']
                        all_items.extend(items.tolist())
                
                if all_items:
                    item_counts = Counter(all_items)
                    total_items = len(all_items)
                    preferences[customer_type] = {item: count/total_items for item, count in item_counts.items()}
        
        print(f"    Analyzed preferences for {len(preferences)} customer types")
        return preferences
    
    def _analyze_channel_patterns(self, test_df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """Analyze ordering patterns by channel"""
        print("  Analyzing channel patterns...")
        
        patterns = {}
        item_columns = ['item1', 'item2', 'item3']
        
        if 'ORDER_CHANNEL_NAME' in test_df.columns:
            for channel in test_df['ORDER_CHANNEL_NAME'].unique():
                if pd.notna(channel):
                    channel_orders = test_df[test_df['ORDER_CHANNEL_NAME'] == channel]
                    
                    # Collect all items for this channel
                    all_items = []
                    for col in item_columns:
                        if col in channel_orders.columns:
                            items = channel_orders[col].dropna().astype(str)
                            items = items[items != 'nan']
                            all_items.extend(items.tolist())
                    
                    if all_items:
                        item_counts = Counter(all_items)
                        total_items = len(all_items)
                        patterns[channel] = {item: count/total_items for item, count in item_counts.items()}
        
        print(f"    Analyzed patterns for {len(patterns)} channels")
        return patterns
    
    def _create_market_basket_rules_from_test(self, test_df: pd.DataFrame) -> Dict[str, List[Tuple[str, float]]]:
        """Create association rules from test data"""
        print("  Creating market basket rules from test data...")
        
        item_columns = ['item1', 'item2', 'item3']
        
        # Calculate support for each item
        all_items = []
        for col in item_columns:
            if col in test_df.columns:
                items = test_df[col].dropna().astype(str)
                items = items[items != 'nan']
                all_items.extend(items.tolist())
        
        if not all_items:
            return {}
        
        item_support = Counter(all_items)
        total_orders = len(test_df)
        item_support = {item: count/total_orders for item, count in item_support.items()}
        
        # Calculate confidence rules
        rules = defaultdict(list)
        
        for idx, row in test_df.iterrows():
            order_items = []
            for col in item_columns:
                if col in row and pd.notna(row[col]) and str(row[col]) != 'nan':
                    order_items.append(str(row[col]))
            
            # Generate rules for this order
            for i, item_a in enumerate(order_items):
                for j, item_b in enumerate(order_items):
                    if i != j:
                        # Calculate confidence based on co-occurrence
                        cooccurrence_prob = 1.0 / len(order_items)  # Simple confidence
                        if cooccurrence_prob > 0.1:
                            rules[item_a].append((item_b, cooccurrence_prob))
        
        # Aggregate and sort rules
        aggregated_rules = {}
        for item, rule_list in rules.items():
            rule_counter = defaultdict(float)
            for target_item, confidence in rule_list:
                rule_counter[target_item] += confidence
            
            # Average the confidences and sort
            avg_rules = [(item, conf/len([r for r in rule_list if r[0] == item])) 
                        for item, conf in rule_counter.items()]
            aggregated_rules[item] = sorted(avg_rules, key=lambda x: x[1], reverse=True)[:10]
        
        print(f"    Created rules for {len(aggregated_rules)} items")
        return aggregated_rules
    
    def _categorize_items_from_test(self, test_df: pd.DataFrame) -> Dict[str, str]:
        """Categorize items based on their names from test data"""
        print("  Categorizing items from test data...")
        
        all_items = set()
        item_columns = ['item1', 'item2', 'item3']
        
        for col in item_columns:
            if col in test_df.columns:
                items = test_df[col].dropna().astype(str)
                items = items[items != 'nan']
                all_items.update(items.tolist())
        
        categories = {}
        
        # Enhanced category keywords for Wings R Us
        category_keywords = {
            'wings': ['wing', 'buffalo', 'grilled', 'spicy', 'mild', 'honey', 'bbq', 'hot'],
            'chicken': ['chicken', 'strips', 'tender', 'crispy', 'fried'],
            'fries': ['fries', 'buffalo fries'],
            'sides': ['corn', 'onion', 'rings', 'salad', 'coleslaw', 'bread'],
            'dips_sauces': ['dip', 'sauce', 'ranch', 'blue cheese', 'honey mustard'],
            'drinks': ['drink', 'soda', 'cola', 'sprite', 'juice', 'water', 'oz'],
            'combos': ['combo'],
            'subs': ['sub', 'sandwich']
        }
        
        for item in all_items:
            if item and item != 'nan':
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
