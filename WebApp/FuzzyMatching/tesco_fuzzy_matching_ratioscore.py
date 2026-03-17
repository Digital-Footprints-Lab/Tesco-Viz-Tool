import pandas as pd
from thefuzz import fuzz
from thefuzz import process

import pandas as pd 
import json
import pandas as pd
from pprint import pprint
from pandas import json_normalize

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

        # Concat base_df to the bottom of purchase_df
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

    # Convert the 'date' column to a datetime data type to enable date-based calculations and sorting
    purchase_df['date'] = purchase_df[['year', 'month', 'day']].astype(str).agg('-'.join, axis=1)

    # Convert the 'time' column to a timedelta data type to enable time-based calculations and sorting
    purchase_df['time'] = pd.to_timedelta(purchase_df['hour'], unit='h') + pd.to_timedelta(purchase_df['minute'], unit='m') + pd.to_timedelta(purchase_df['second'], unit='s')

    return product_df

def categorize_products(df_products, df_categories):
    # Check if the required columns exist
    if 'Product' not in df_products.columns or 'Product' not in df_categories.columns or 'Category' not in df_categories.columns:
        raise KeyError("Ensure 'Product' column exists in both dataframes and 'Category' column exists in df_categories")

    # Create a dictionary of categories for quick lookup
    category_dict = df_categories.set_index('Product')['Category'].to_dict()

    # Function to get the best match category for a product
    def get_category(product):
        best_match = process.extractOne(product, category_dict.keys(), scorer=fuzz.ratio)
        if best_match:
            return category_dict[best_match[0]], best_match[1], best_match[0]
        return None, None, None

    # Create a copy of the DataFrame to avoid SettingWithCopyWarning
    df_products_copy = df_products.copy()

    # Apply the function to the 'Product' column to get the 'Category', 'Score', and 'Matched Product'
    df_products_copy[['Category', 'Score', 'Matched Product']] = df_products_copy['Product'].apply(lambda x: pd.Series(get_category(x)))
    return df_products_copy

# Reading the JSON file
with open("C:\\Users\\ob24562\\OneDrive - University of Bristol\\Documents\\Python_Code\\ClubCard_data\\Tesco-Customer-Data-LAURA.json", 'r') as f:
    tesco_clubcard_data = json.load(f)

cat_df = pd.read_csv("C:\\Users\\ob24562\\OneDrive - University of Bristol\\Documents\\Python_Code\\Seedcorn_project\\Tesco_Categories\\Tesco_categories_and_products.csv")
my_shopping = clubcard_pipeline(tesco_clubcard_data)
my_products = my_shopping.rename(columns={"name": "Product"})

# Categorize products and get scores
categorized_products = categorize_products(my_products[['Product']], cat_df)

# Stitch this back to original dataframe information
my_products = my_products.merge(categorized_products[['Product', 'Category', 'Score', 'Matched Product']], on='Product', how='left')

# Remove duplicates
my_products = my_products.drop_duplicates(subset=['Product'])

# Save the new dataframe to a CSV file
my_products.to_csv("Seedcorn_project\\my_category_data_plusscore.csv", index=False)