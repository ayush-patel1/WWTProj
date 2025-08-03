# Wings R Us - Personalized Recommendation System

## Project Overview
Build a personalized recommendation engine for Wings R Us (a Quick Service Restaurant) that suggests up to 3 complementary items (e.g., drinks, sides, wings) in real-time as the customer places an order.

## Objective
Increase average order value and customer satisfaction by predicting the 3 most likely missing items that would complete a partial order.

## Data Files
- `order_data.csv` – historical order logs
- `customer_data.csv` – user profiles (guest/loyal/special)
- `store_data.csv` – store/channel metadata
- `test_data_question.csv` – partial orders with 1 item removed (for evaluation)

## Task
For each partial order in test_data_question, predict the 3 most likely missing items that would complete the original order.

## Evaluation Metric
**Recall@3** – If any of the 3 predicted items matches the true missing item, the prediction is considered correct.

## Output
An Excel file with RECOMMENDATION 1, 2, and 3 columns for each order.

## Project Structure
```
wings-r-us-recommendation/
├── data/                          # Data files
├── src/                           # Source code
│   ├── data_preprocessing.py      # Data cleaning and preprocessing
│   ├── feature_engineering.py    # Feature creation
│   ├── recommendation_engine.py  # Main recommendation model
│   └── evaluation.py             # Model evaluation
├── models/                        # Saved models
├── output/                        # Output files
├── notebooks/                     # Jupyter notebooks for exploration
├── requirements.txt              # Python dependencies
└── main.py                       # Main execution script
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Place your data files in the `data/` folder:
   - order_data.csv
   - customer_data.csv
   - store_data.csv
   - test_data_question.csv

3. Run the main script:
```bash
python main.py
```

## Approach
1. **Data Exploration & Preprocessing**: Analyze the data structure and clean it
2. **Feature Engineering**: Create features for recommendation (customer profiles, order patterns, etc.)
3. **Model Development**: Build recommendation models (collaborative filtering, market basket analysis, etc.)
4. **Evaluation**: Test using Recall@3 metric
5. **Output Generation**: Create Excel file with recommendations
