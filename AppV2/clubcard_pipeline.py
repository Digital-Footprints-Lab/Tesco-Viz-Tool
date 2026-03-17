import json
import pandas as pd
from pprint import pprint
from pandas import json_normalize
# import geopandas
from rapidfuzz import fuzz, process

# import plotly.express as px
# import plotly.subplots
# import plotly.graph_objs as go


def clubcard_process(tesco_clubcard_data: dict):
    """
    This function processes the Tesco Clubcard data and returns two DataFrames
    
    purchase_data: basketValueGross,purchaseType,overallBasketSavings,storeId,timeStamp,
    basketValueNet,storeFormat,basket_id,year,month,day,hour,minute,second,date,time

    product_data: name,quantity,channel,price,basket_id,product_id
    """

    # Isolating the 'purchase' layer
    purchase_data = tesco_clubcard_data.get('purchases', {})

    # Flattening the list of lists to a single list of dictionaries
    #flattened_purchase_data = purchase_data ###'no need to flatten as already flattened'
    
    # Initialize empty DataFrames for purchases and products
    purchase_df = pd.DataFrame()
    product_df = pd.DataFrame()

    # Generate basket IDs
    basket_id = 0
    
    # Loop through the flattened list of dictionaries to create the basket_id
    for p in purchase_data:
        # Increment basket ID
        basket_id += 1
        
        # Extract common basket-level information
        base_data = {k: v for k, v in p.items() if k not in ['payment', 'items']} ###product changed to items

        # Generate a unique basket ID and add it to base_data
        base_data['basket_id'] = f'B{basket_id}'
        base_df = pd.DataFrame(base_data, index=[basket_id])

        # Concat base_df to the bottom of purcahse_df
        purchase_df = pd.concat([purchase_df, base_df], ignore_index=True)
        
        # Flatten 'product' and add 'basket_id' column ##### 'products' changed to 'items'
        product_data = json_normalize(p['items'], sep='_')
        product_data['basket_id'] = f'B{basket_id}'
        
        # Add this DataFrame to the product DataFrame
        product_df = pd.concat([product_df, product_data], ignore_index=True)

    #purchase_df.drop(['storeName', 'storeAddress'], axis=1, inplace=True)

    # Create a mapping of product names to IDs. This assumes that you've standardized your product names as mentioned above.
    unique_product_names = product_df['name'].unique()
    product_id_map = {name: f"P{i+1}" for i, name in enumerate(unique_product_names)}

    # Map the product names to IDs and create a new column
    product_df['product_id'] = product_df['name'].map(product_id_map)

    # Convert the 'timeStamp' column to datetime format without specifying a format
    purchase_df['timestamp'] = pd.to_datetime(purchase_df['timestamp'], errors='coerce') ###'timeStamp' now is 'timestamp'

    purchase_df = purchase_df.sort_values(by='timestamp', ascending=True)

    # Extracting the various components
    purchase_df['year'] = purchase_df['timestamp'].dt.year
    purchase_df['month'] = purchase_df['timestamp'].dt.month
    purchase_df['day'] = purchase_df['timestamp'].dt.day
    purchase_df['hour'] = purchase_df['timestamp'].dt.hour
    purchase_df['minute'] = purchase_df['timestamp'].dt.minute
    purchase_df['second'] = purchase_df['timestamp'].dt.second

    # Dropping columns from product_df
    # NEW - sometimes weight isn't there if no loose items purchased, so check column exists first, then drop if present.

    columns_to_drop = [col for col in ['volume', 'weight'] if col in product_df.columns]
    product_df.drop(columns=columns_to_drop, axis=1, inplace=True)

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

def most_frequent_products_calc(product_df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes in the product_df and outputs the list of products by frequency
    4.2 in the original notebook
    """
    most_frequent_products = product_df['name'].value_counts().reset_index()
    most_frequent_products.columns = ['Product Name', 'Frequency']

    return most_frequent_products


# def store_purchase_counter(purchase_df: pd.DataFrame):
#     """
#     Takes in the purchase_df and outputs the number of purchases made at each store
#     4.3 in the original notebook
#     """
#     store_purchase_count = purchase_df['storeId'].value_counts().reset_index()
#     store_purchase_count.columns = ['Store ID', 'Number of Purchases']
#     #print(store_purchase_count)

#     return store_purchase_count

def price_change_analysis(purchase_df: pd.DataFrame, product_df: pd.DataFrame):
    """
    Takes in the purchase_df and product_df and outputs the price change analysis
    4.4 in the original notebook
    """
    merged_df = pd.merge(purchase_df, product_df, on='basket_id')
    product_names = merged_df['name'].unique()
    # Only need name, timeStamp, price
    merged_df = merged_df[['name', 'price', 'timestamp']]

    # Remove any row with 'name' == "Home Delivery Substitution Refund"
    merged_df = merged_df[merged_df['name'] != "Home Delivery Substitution Refund"]
    # Drop NaNs
    merged_df = merged_df.dropna()
    return merged_df

def item_price_change(price_change: pd.DataFrame):
    """
    Takes in the price_change dataframe and outputs the item price change analysis
    """
    product_counts = price_change['name'].value_counts()
    product_counts = product_counts[product_counts > 1]
    product_names = product_counts.index.unique()

    # Find the smallest and largest price for each product
    price_change['price'] = price_change['price'].astype(float)
    price_change = price_change[price_change['name'].isin(product_names)]
    
    # Want a new dataframe called item_change which has 1 row per item with the max and min price and the times of those prices
    price_change = price_change.groupby(['name', 'price', 'timestamp']).size().reset_index(name='count')
    price_change = price_change.groupby('name').agg({'price': ['min', 'max'], 'timestamp': ['min', 'max']}).reset_index()
    price_change.columns = ['name', 'min_price', 'max_price', 'min_date', 'max_date']
    # Convert min_date and max_date to just be the date
    price_change['min_date'] = price_change['min_date'].dt.date
    price_change['max_date'] = price_change['max_date'].dt.date
    # Make a column called price_difference
    price_change['Price_Difference'] = price_change['max_price'] - price_change['min_price']
    price_change['Price_Percent_Change'] = (price_change['Price_Difference'] / price_change['min_price']) * 100
        
    return price_change


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

def TotalYearSpend(purchase_df: pd.DataFrame, Year: int):
    """
    Takes in the purchase_df and year and returns the total spend for that year by month
    """
    # make sure the "year" column is an integer or NaN
    purchase_df['year'] = pd.to_numeric(purchase_df['year'], errors='coerce')
    purchase_year = purchase_df[purchase_df['year'] == Year]
    by_month = purchase_year.groupby('month')['basketValueGross'].sum()
    
    # Change the index numbers to the corresponding month
    by_month.index = by_month.index.map({1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})
    # Fill in any missing indexes with 0
    by_month = by_month.reindex(['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'], fill_value=0)
    
    return by_month

# def store_location_map(store_loc: pd.DataFrame, person_info:pd.DataFrame):
#     """
#     Takes in tesco store location dataframe and a dataframe about shopping info
#     Matches by Store ID column and creates a geopandas dataframe for easy plotting
#     """
#     assert "Store ID" in store_loc.columns, "Store ID column not found in store_loc dataframe"
#     assert "Store ID" in person_info.columns, "Store ID column not found in person_info dataframe"

#     store_loc["Store ID"] = store_loc["Store ID"].astype(int)
#     person_info["Store ID"] = person_info["Store ID"].astype(int)
#     # Make Store ID the index of the store_loc dataframe
#     store_loc = store_loc.set_index("Store ID")
#     # Make Store ID the index of the person_info dataframe
#     person_info = person_info.set_index("Store ID")

#     # Join the two dataframes on the Store ID index

#     new_df = store_loc.join(person_info)

#     new_df["Number of Purchases"] = new_df["Number of Purchases"].fillna(0)
#     # Order the columns by Number of Purchases descending
#     new_df = new_df.sort_values("Number of Purchases", ascending=False)

#     # Drop NaNs
#     new_df = new_df.dropna()

#     gdf = geopandas.GeoDataFrame(new_df, geometry=geopandas.points_from_xy(new_df.lon, new_df.lat), crs="EPSG:4326")
    
#     return gdf

## Fuzzy matching stuff

cat_df = pd.read_csv("Tesco_categories_and_products.csv")

def fuzzy_match(product_name, cat_df: pd.DataFrame):
    """
    Takes in a product name and a category_df and returns the closest match in the category_df and a fuzzy score
    A score of 100 means a perfect match
    """
    if product_name in cat_df["Product"].values:
        category = cat_df[cat_df["Product"] == product_name]["Category"].values[0]
        score = 100
    else:
        match, score, index = process.extract(product_name, cat_df["Product"].values, limit=1)[0]
        category = cat_df[cat_df["Product"] == match]["Category"].values[0]
    return category, score

def speedy_fuzzy_match(product_df: pd.DataFrame, cat_df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts the unique lists of products from product_df then applies fuzzy_match to each product
    Then recombines it at the other end
    Faster than looping through the whole dataframe
    """
    # "name" is the column name for the product names
    unique_products = product_df.drop_duplicates(subset="name")
    # Fuzzy match on only the unqiue products
    unique_products["Category"], unique_products["Score"] = zip(*unique_products["name"].apply(fuzzy_match, cat_df=cat_df))
    # Recombine with the original product_df
    product_df["Category"], product_df["Score"] = zip(*product_df["name"].apply(lambda x: unique_products[unique_products["name"] == x][["Category", "Score"]].values[0]))
    
    return product_df

def return_category(product_df: pd.DataFrame, unique_products: pd.DataFrame):
    """
    Takes in the product_df and unique_products and returns the category for each product
    """
    # For each product in the product_df, find the category in the unique_products dataframe
    # If there is no such product or the Score is below 80, return "Unknown"
    product_df["Category"] = product_df["name"].apply(lambda x: unique_products[unique_products["name"] == x]["Category"].values[0] if x in unique_products["name"].values and unique_products[unique_products["name"] == x]["Score"].values[0] > 80 else "Unknown")
    
    return product_df





# Commented out code to run the pipeline stuff inside the Python file, you also have to load in the JSON file first!

## reading the JSON file
# with open('PipelineDONTUPLOAD\Tesco_Customer_Data_Laura.json', 'r') as f:
#     tesco_clubcard_data = json.load(f)

# purchase_df, product_df = clubcard_process(tesco_clubcard_data)
# total_money_spent, total_savings, average_basket_value = kpi_calculator(purchase_df)
# most_frequent_products = most_frequent_products_calc(product_df)
# store_purchase_count = store_purchase_counter(purchase_df)
# monthly_visits = monthly_frequency(purchase_df)

# store_purchase_count.to_csv('PipelineDONTUPLOAD\store_purchase_count.csv', index=False)
