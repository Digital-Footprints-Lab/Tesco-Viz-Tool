import json
import pandas as pd
from pprint import pprint
from pandas import json_normalize
# import plotly.express as px
# import plotly.subplots
# import plotly.graph_objs as go


# reading the JSON file
# with open('Tesco_Customer_Data_Laura.json', 'r') as f:
#     tesco_clubcard_data = json.load(f)

def clubcard_pipeline(tesco_clubcard_data: dict):
    """
    This function processes the Tesco Clubcard data and returns two DataFrames with the following columns:
    product_data: name,quantity,channel,price,basket_id,product_id
    purchase_data: basketValueGross,purchaseType,overallBasketSavings,storeId,timeStamp,basketValueNet,storeFormat,basket_id,year,month,day,hour,minute,second,date,time
    """

    # Isolating the 'purchase' layer
    purchase_data = tesco_clubcard_data.get('Purchase', {})

    # Flattening the list of lists to a single list of dictionaries
    flattened_purchase_data = [item for sublist in purchase_data for item in sublist]

    # Initialize empty DataFrames for purchases and products
    purchase_df = pd.DataFrame()
    product_df = pd.DataFrame()

    # Generate basket IDs
    basket_id = 0

    # Loop through the flattened list of dictionaries to create the basket_id
    for p in flattened_purchase_data:
        # Increment basket ID
        basket_id += 1
        
        # Extract common basket-level information
        base_data = {k: v for k, v in p.items() if k not in ['paymentType', 'product']}

        # Generate a unique basket ID and add it to base_data
        base_data['basket_id'] = f'B{basket_id}'
        base_df = pd.DataFrame(base_data, index=[basket_id])

        # Concat base_df to the bottom of purcahse_df
        purchase_df = pd.concat([purchase_df, base_df], ignore_index=True)
        
        # Flatten 'product' and add 'basket_id' column
        product_data = json_normalize(p['product'], sep='_')
        product_data['basket_id'] = f'B{basket_id}'
        
        # Add this DataFrame to the product DataFrame
        product_df = pd.concat([product_df, product_data], ignore_index=True)

    purchase_df.drop(['storeName', 'storeAddress'], axis=1, inplace=True)

    # Create a mapping of product names to IDs. This assumes that you've standardized your product names as mentioned above.
    unique_product_names = product_df['name'].unique()
    product_id_map = {name: f"P{i+1}" for i, name in enumerate(unique_product_names)}

    # Map the product names to IDs and create a new column
    product_df['product_id'] = product_df['name'].map(product_id_map)

    # Convert the 'timeStamp' column to datetime format without specifying a format
    purchase_df['timeStamp'] = pd.to_datetime(purchase_df['timeStamp'], errors='coerce')

    # Extracting the various components
    purchase_df['year'] = purchase_df['timeStamp'].dt.year
    purchase_df['month'] = purchase_df['timeStamp'].dt.month
    purchase_df['day'] = purchase_df['timeStamp'].dt.day
    purchase_df['hour'] = purchase_df['timeStamp'].dt.hour
    purchase_df['minute'] = purchase_df['timeStamp'].dt.minute
    purchase_df['second'] = purchase_df['timeStamp'].dt.second

    # Dropping columns from product_df
    product_df.drop(['weightInGrams', 'volumeInLitres'], axis=1, inplace=True)

    # Dropping the column from purchase_df
    purchase_df.drop(['says'], axis=1, inplace=True)

    product_df['quantity'] = pd.to_numeric(product_df['quantity'], errors='coerce')
    product_df['price'] = pd.to_numeric(product_df['price'], errors='coerce')
    product_df['name'] = product_df['name'].astype('string')

    # Convert to float
    purchase_df['basketValueGross'] = pd.to_numeric(purchase_df['basketValueGross'], errors='coerce')
    purchase_df['basketValueNet'] = pd.to_numeric(purchase_df['basketValueNet'], errors='coerce')
    purchase_df['overallBasketSavings'] = pd.to_numeric(purchase_df['overallBasketSavings'], errors='coerce')

    #Convert the 'date' column to a datetime data type to enable date-based calculations and sorting
    purchase_df['date'] = purchase_df[['year', 'month', 'day']].astype(str).agg('-'.join, axis=1)

    # Convert the 'time' column to a timedelta data type to enable time-based calculations and sorting
    purchase_df['time'] = pd.to_timedelta(purchase_df['hour'], unit='h') + pd.to_timedelta(purchase_df['minute'], unit='m') + pd.to_timedelta(purchase_df['second'], unit='s')

    return purchase_df, product_df

def kpi_calculator(purchase_df: pd.DataFrame):
    """
    Takes in the purchased_df and outputs: 
    "Total Money Spent", "Total Savings", "Average Basket Value"
    4.1 in the original notebook
    """
    total_money_spent = purchase_df['basketValueNet'].sum()
    total_savings = purchase_df['overallBasketSavings'].sum()
    average_basket_value = purchase_df.groupby('basket_id')['basketValueNet'].sum().mean()

    return total_money_spent, total_savings, average_basket_value

def most_frequent_products(product_df: pd.DataFrame, n: int = 10):
    """
    Takes in the product_df and outputs the n most frequent products
    Default n = 10, checks if this is more than the number of products available
    4.2 in the original notebook
    """
    most_frequent_products = product_df['name'].value_counts().reset_index()
    most_frequent_products.columns = ['Product Name', 'Frequency']

    if n > len(most_frequent_products):
        n = len(most_frequent_products)
        print(f"Only {n} products are available in the dataset.")
    
    top_n_products = product_df['name'].value_counts().iloc[:n].reset_index()
    top_n_products.columns = ['Product Name', 'No. of Purchases']

    return most_frequent_products, top_n_products

def store_purchase_count(purchase_df: pd.DataFrame):
    """
    Takes in the purchase_df and outputs the number of purchases made at each store
    4.3 in the original notebook
    """
    store_purchase_count = purchase_df['storeId'].value_counts().reset_index()
    store_purchase_count.columns = ['Store ID', 'Number of Purchases']

    return store_purchase_count

def price_change_analysis(purchase_df: pd.DataFrame, product_df: pd.DataFrame):
    """
    Takes in the purchase_df and product_df and outputs the price change analysis
    4.4 in the original notebook
    """
    merged_df = pd.merge(purchase_df, product_df, on='basket_id')
    product_names = merged_df['name'].unique()
    # Only need name, timeStamp, price
    product_df = product_df[['name', 'price', 'timeStamp']]

    return product_df

def monthly_frequency(purchase_df: pd.DataFrame):
    """
    Takes in the purchase_df and outputs the monthly frequency of purchases
    4.5 in the original notebook
    """
    # Group by month and year and count the number of visits
    monthly_visits = purchase_df.groupby(['year', 'month']).size().reset_index(name='Visits')

    # Create a combined column for month and year
    monthly_visits['MonthYear'] = monthly_visits.apply(lambda row: f"{int(row['year'])}-{int(row['month']):02d}", axis=1)

    return monthly_visits