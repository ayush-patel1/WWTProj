"""
Data Preprocessing Module for Wings R Us Recommendation System
"""

import pandas as pd
import numpy as np
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

class DataPreprocessor:
    """
    Handles data loading, cleaning, and initial preprocessing
    """
    
    def __init__(self):
        self.data = {}
    
    def load_and_clean_data(self, data_paths: Dict[str, str]) -> Dict[str, pd.DataFrame]:
        """
        Load and clean all data files
        
        Args:
            data_paths: Dictionary with data file paths
            
        Returns:
            Dictionary containing cleaned DataFrames
        """
        print("Loading data files...")
        
        # Load all data files
        for name, path in data_paths.items():
            try:
                df = pd.read_csv(path)
                print(f"  - {name}: {df.shape[0]} rows, {df.shape[1]} columns")
                self.data[name] = df
            except Exception as e:
                print(f"  ❌ Error loading {path}: {str(e)}")
                raise
        
        # Clean each dataset
        self.data['orders'] = self._clean_order_data(self.data['orders'])
        self.data['customers'] = self._clean_customer_data(self.data['customers'])
        self.data['stores'] = self._clean_store_data(self.data['stores'])
        self.data['test'] = self._clean_test_data(self.data['test'])
        
        print("Data cleaning completed")
        return self.data
    
    def _clean_order_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean order data"""
        print("  Cleaning order data...")
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Handle missing values for essential columns
        essential_cols = ['ORDER_ID']
        for col in essential_cols:
            if col in df.columns:
                df = df.dropna(subset=[col])
        
        # Standardize text columns
        text_columns = ['ORDERS', 'ORDER_CHANNEL_NAME', 'ORDER_SUBCHANNEL_NAME', 'ORDER_OCCASION_NAME']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
        
        # Convert date columns if present
        date_columns = ['ORDER_CREATED_DATE', 'timestamp', 'date']
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Remove duplicates
        original_shape = df.shape[0]
        df = df.drop_duplicates()
        if df.shape[0] < original_shape:
            print(f"    Removed {original_shape - df.shape[0]} duplicate rows")
        
        return df
    
    def _clean_customer_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean customer data"""
        print("  Cleaning customer data...")
        
        df = df.copy()
        
        # Handle missing customer IDs
        df = df.dropna(subset=['CUSTOMER_ID'])
        
        # Standardize customer types
        if 'CUSTOMER_TYPE' in df.columns:
            df['CUSTOMER_TYPE'] = df['CUSTOMER_TYPE'].str.strip()
            # Map variations to standard types
            type_mapping = {
                'Guest': 'guest',
                'Registered': 'registered', 
                'Special': 'special'
            }
            df['CUSTOMER_TYPE'] = df['CUSTOMER_TYPE'].map(type_mapping).fillna('guest')
        
        return df
    
    def _clean_store_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean store data"""
        print("  Cleaning store data...")
        
        df = df.copy()
        
        # Handle missing store IDs
        df = df.dropna(subset=['STORE_NUMBER'])
        
        # Clean location data
        if 'CITY' in df.columns:
            df['CITY'] = df['CITY'].astype(str).str.strip()
        if 'STATE' in df.columns:
            df['STATE'] = df['STATE'].astype(str).str.strip()
        if 'POSTAL_CODE' in df.columns:
            df['POSTAL_CODE'] = df['POSTAL_CODE'].astype(str).str.strip()
        
        return df
    
    def _clean_test_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean test data"""
        print("  Cleaning test data...")
        
        df = df.copy()
        
        # Handle missing order IDs
        df = df.dropna(subset=['ORDER_ID'])
        
        # Standardize item names in item columns
        item_columns = ['item1', 'item2', 'item3']
        for col in item_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip()
                # Replace 'nan' string with actual NaN
                df[col] = df[col].replace('nan', np.nan)
        
        return df
    
    def get_data_summary(self) -> None:
        """Print summary of loaded data"""
        print("\n📊 Data Summary:")
        print("-" * 40)
        
        for name, df in self.data.items():
            print(f"{name.capitalize()} Data:")
            print(f"  Shape: {df.shape}")
            print(f"  Columns: {list(df.columns)}")
            if not df.empty:
                print(f"  Missing values: {df.isnull().sum().sum()}")
            print()
