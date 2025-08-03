# Wings R Us Recommendation System - Data Files

Please place your CSV data files in this directory:

## Required Files:
- `order_data.csv` - Historical order logs
- `customer_data.csv` - User profiles (guest/loyal/special)  
- `store_data.csv` - Store/channel metadata
- `test_data_question.csv` - Partial orders with 1 item removed (for evaluation)

## Expected Data Structure:

### order_data.csv
```
order_id,customer_id,store_id,item_name,quantity,price,order_date
1001,C001,S001,buffalo wings,1,12.99,2024-01-01
1001,C001,S001,cola,1,2.99,2024-01-01
...
```

### customer_data.csv
```
customer_id,customer_type,registration_date,total_orders
C001,loyal,2023-06-15,25
C002,guest,,1
...
```

### store_data.csv
```
store_id,store_name,channel,location,region
S001,Downtown Store,app,Downtown,North
S002,Mall Kiosk,kiosk,Shopping Mall,South
...
```

### test_data_question.csv
```
order_id,item_1,item_2,item_3,missing_item
T001,buffalo wings,fries,,cola
T002,mild wings,onion rings,sprite,
...
```

Once you place these files here, run the main script to start the recommendation system.
