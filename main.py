"""
Wings R Us Recommendation System - Main Execution Script
"""

import pandas as pd
import numpy as np
from src.data_preprocessing import DataPreprocessor
from src.feature_engineering_v2 import FeatureEngineer
from src.recommendation_engine import RecommendationEngine
from src.evaluation import ModelEvaluator
import os

def main():
    """
    Main function to run the Wings R Us recommendation system pipeline
    """
    print("🍗 Wings R Us Recommendation System")
    print("=" * 50)
    
    # Define data paths
    data_paths = {
        'orders': 'data/order_data.csv',
        'customers': 'data/customer_data.csv', 
        'stores': 'data/store_data.csv',
        'test': 'data/test_data_question.csv'
    }
    
    # Check if data files exist
    print("📁 Checking data files...")
    missing_files = []
    for name, path in data_paths.items():
        if not os.path.exists(path):
            missing_files.append(path)
            print(f"❌ Missing: {path}")
        else:
            print(f"✅ Found: {path}")
    
    if missing_files:
        print(f"\n⚠️  Please place the following files in the data/ folder:")
        for file in missing_files:
            print(f"   - {file}")
        return
    
    try:
        # Step 1: Data Preprocessing
        print("\n🔧 Step 1: Data Preprocessing...")
        preprocessor = DataPreprocessor()
        data = preprocessor.load_and_clean_data(data_paths)
        print("✅ Data preprocessing completed")
        
        # Step 2: Feature Engineering
        print("\n⚙️  Step 2: Feature Engineering...")
        feature_engineer = FeatureEngineer()
        features = feature_engineer.create_features(data)
        print("✅ Feature engineering completed")
        
        # Step 3: Model Training
        print("\n🤖 Step 3: Training Recommendation Model...")
        recommendation_engine = RecommendationEngine()
        recommendation_engine.train(features)
        print("✅ Model training completed")
        
        # Step 4: Generate Predictions
        print("\n🎯 Step 4: Generating Recommendations...")
        test_data = data['test']
        predictions = recommendation_engine.predict(test_data, features)
        print("✅ Predictions generated")
        
        # Step 5: Save Results
        print("\n💾 Step 5: Saving Results...")
        output_file = 'output/wings_r_us_recommendations.xlsx'
        recommendation_engine.save_predictions(predictions, output_file)
        print(f"✅ Results saved to {output_file}")
        
        # Step 6: Evaluation (if ground truth available)
        print("\n📊 Step 6: Model Evaluation...")
        evaluator = ModelEvaluator()
        if 'missing_item' in test_data.columns:
            recall_score = evaluator.calculate_recall_at_k(predictions, test_data['missing_item'], k=3)
            print(f"📈 Recall@3 Score: {recall_score:.4f}")
        else:
            print("ℹ️  No ground truth available for evaluation")
        
        print("\n🎉 Pipeline completed successfully!")
        print(f"📄 Check your recommendations in: {output_file}")
        
    except Exception as e:
        print(f"\n❌ Error occurred: {str(e)}")
        print("Please check your data files and try again.")

if __name__ == "__main__":
    main()
