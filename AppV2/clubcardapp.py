import streamlit as st
import json
import pandas as pd
import plotly.express as px
import clubcard_pipeline as cp
import streamlit_option_menu
from streamlit_option_menu import option_menu

# Upload the Tesco Clubcard data
st.set_page_config(layout="wide")
purchase_df, product_df = None, None
uploaded_file = st.file_uploader("Upload your Tesco clubcard data here", type="json")

with st.sidebar:
        # Makes the side bar have a title and an options menu
        st.sidebar.title('Shopping Trolley Secrets')
        selected = option_menu(
        menu_title = 'Menu',
        options = ["Overview", "Spending", "Products types", "Price changes", "App Guide"],
        #icons = [":moneybag:", ":apple:",":convenience_store:"],
        #menu_icon = "cast",
        default_index = -1)
        # Default index is -1 so that the landing page is the App Guide


if uploaded_file is not None:
          
    with st.spinner("Loading..."):
        # Does a little loading thing whilst the data is being processed
        tesco_clubcard_data = json.load(uploaded_file)
        purchase_df, product_df = cp.clubcard_process(tesco_clubcard_data)
    
        total_money_spent, total_savings, average_basket_value = cp.kpi_calculator(purchase_df)
        
        most_frequent_products = cp.most_frequent_products_calc(product_df)
        
        #store_purchase_count = cp.store_purchase_counter(purchase_df)
        #st.write(store_purchase_count)

        monthly_visits = cp.monthly_frequency(purchase_df)

        price_change = cp.price_change_analysis(purchase_df, product_df)

        #store_loc = pd.read_csv("tesco_store_lat_lon.csv", index_col=0)
         
        #store_loc = store_loc.rename(columns={"Store Number": "Store ID"})

        #st.write(store_loc)
        
        #store_gdf = cp.store_location_map(store_loc, store_purchase_count)
        # Make a color column for the map, based on the number of purchases
        #non_zero_store_gdf = store_gdf[store_gdf["Number of Purchases"] != 0]
        # convert integer to RGB tuple for color
        
        item_change = cp.item_price_change(price_change)
        #st.write(item_change)
        #st.write(store_gdf)

        # Fuzzy matching
        #cat_df = pd.read_csv("Tesco_categories_and_products.csv")
        #products_with_categories = cp.speedy_fuzzy_match(product_df, cat_df)

        # Not fuzzy matching but category finding
        unique_products = pd.read_csv("unique_products.csv")
        products_df = cp.return_category(product_df, unique_products)
        
                
        
if purchase_df is not None and product_df is not None:
    # selected is the menu tab, so whichever tab is selected will show the corresponding data viz
    if selected == "Overview":

        # Find the earliest date and the latest date in the data
        earliest_year = purchase_df['year'].min()
        earliest_month = purchase_df[purchase_df['year'] == earliest_year]['month'].min()

        latest_year = purchase_df['year'].max()
        latest_month = purchase_df[purchase_df['year'] == latest_year]['month'].max()
        # Convert month number to month name
        month_dict = {1: "January", 2: "February", 3: "March", 4: "April", 5: "May", 6: "June", 7: "July", 8: "August", 9: "September", 10: "October", 11: "November", 12: "December"}
        earliest_month = month_dict[int(earliest_month)]
        latest_month = month_dict[int(latest_month)]
        st.info("Your data includes purchases from " + str(earliest_month) + " " + str(int(earliest_year)) + " to " + str(latest_month) + " " + str(int(latest_year)))


        # Main page with summary stats and 4 plots
        st.header("Summary Stats:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"Total Money Spent: £{total_money_spent:.2f}")
        with col2:
            st.info(f"Total Savings: £{total_savings:.2f}")
        with col3:
            st.info(f"Average Basket Value: £{average_basket_value:.2f}")
        
        # Find the latest year in the data
        latest_year = int(purchase_df['year'].max())
        TotalYearlySpend = cp.TotalYearSpend(purchase_df, latest_year)

        plotcol1, plotcol2 = st.columns(2)
        # 4 plots:
        # Plot 1 Total 2024 Spend, bar chart with amount of money per month
        # Plot 2 List of top n Most frequently purchased products (with widget?)
        with plotcol1:
            # Widget here?
            st.header("How much did you spend this year on shopping?")
            yearlyspendplot = px.bar(TotalYearlySpend, title=f'Total Spend per Month in {latest_year}')
            yearlyspendplot.update_layout(showlegend=False)
            # Rename y-axis to say Total Spend (£)
            yearlyspendplot.update_yaxes(title_text="Total Spend (£)")
            st.plotly_chart(yearlyspendplot)

            yearinfo = st.toggle("Click for more info on the bar chart")
            if yearinfo:
                st.info(f"This bar chart shows the total amount of money that you spent per month for the latest year in your data: {latest_year}. You can hover over each bar to see the exact values. You can navigate to the 'Spending' tab on the sidebar to see more info about your spending habits.")

            # Widget here?
            st.header("Most frequently purchased products:")
            topproduct, topfreq = most_frequent_products.loc[0, 'Product Name'], most_frequent_products.loc[0, 'Frequency']
            st.write(most_frequent_products)
            freqinfo = st.toggle("Click for more info on the table")
            if freqinfo:
                st.info(f"This table shows the products you purchased most frequently. So on the first row you can see that you bought {topproduct} {topfreq} times! You can scroll through to see all the products you purchased and their frequency and you can also hover over the table to get extra options to download, search or expand this table. You can navigate to the 'Spending' tab on the sidebar to see more info about your spending habits.")

        # Plot 3 All previous locations (static plot of shops)
        # Plot 4 Highest price increase, line plot for a particular item
        with plotcol2:
            # st.header("Where have you been shopping?")
            # # Commented out to remove widget for now
            # #map_widget_over = st.radio("Toggle to see all stores or only stores with purchases", ["Show all stores", "Show only stores with purchases"])
            # map_widget_over = "Show only stores with purchases"



            # #st.write(store_gdf)
            # if map_widget_over == "Show all stores":
            #     st.map(store_gdf, latitude="lat", longitude="lon", size=200)
            # if map_widget_over == "Show only stores with purchases":
            #     st.map(non_zero_store_gdf, latitude="lat", longitude="lon", size=200)
           
            # map_ov_info = st.toggle("Click for more info on the map")
            # if map_ov_info:
            #     st.info("This interactive map shows the locations of Tesco stores. You can pan and zoom to move around and see different areas. You can toggle to see just the stores you have purchased at or all stores we have data for. When you toggle, the map recentres. You can navigate to the 'Stores (Location)' tab on the sidebar to see more info about the stores you have shopped at.")

            st.header("The item with the biggest percentage price change in your dataset:")
           
            # Find the 3 products with the biggest price change
            item_change_df = item_change[['name', 'Price_Difference']].sort_values('Price_Difference', ascending=False)
            # Make the Price_Difference column a string with a £ sign and two decimal places
            item_change_df["Price_Difference"] = "£" + item_change_df["Price_Difference"].round(2).astype(str)
            # Rename it to be Price Difference
            item_change_df = item_change_df.rename(columns={"Price_Difference": "Price Difference"})
            item_change_df.reset_index(drop=True, inplace=True)
            #st.write(item_change_df)


            # For each item, see how many times it was purchased
            product_counts = price_change['name'].value_counts()
            # Filter out the products that were only purchased once
            product_counts = product_counts[product_counts > 1]
            # Filter price change to only include the products that were purchased more than once
            merged_df = price_change[price_change['name'].isin(product_counts.index)]
            # Calculate price percentage change for each product
            # Make a new dataframe which has the largest and smallest price for each product
            price_change = merged_df.groupby('name')['price'].agg(['max', 'min']).reset_index()
            price_change["Percentage Change"] = ((price_change["max"] - price_change["min"]) / price_change["min"]) * 100
            # Sort by percentage change
            price_change = price_change.sort_values("Percentage Change", ascending=False).reset_index(drop=True)
            # Find the top product name
            top_product = price_change.loc[0, 'name']
            # merged_df of the top_product 
            toppricechange = px.line(merged_df[merged_df['name'] == top_product], x='timestamp', y='price', title=f"Price Change Over Time for {top_product}")
            # Rename the x-axis to say Date
            toppricechange.update_xaxes(title_text="Date")
            # Rename the y-axis to say Price (£)
            toppricechange.update_yaxes(title_text="Price (£) per unit")
            st.plotly_chart(toppricechange)
            

            item_change_info = st.toggle("Click for more info on the price changes")
            if item_change_info:
                st.info(f"We looked at all the items you purchased and calculated the percentage increase between the most expensive the item was and the least expensive the item was. Here you can see {top_product} which had a percentage price change of {price_change.loc[0, 'Percentage Change']:.2f}% from £{price_change.loc[0, 'min']} to £{price_change.loc[0, 'max']}. You can navigate to the 'Price changes' tab on the sidebar to see more info about price changes of different items in your data.")

            
    elif selected == "Spending":
        
        st.header("Summary Stats:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"Total Money Spent: £{total_money_spent:.2f}")
        with col2:
            st.info(f"Total Savings: £{total_savings:.2f}")
        with col3:
            st.info(f"Average Basket Value: £{average_basket_value:.2f}")
        
        # Look at the purchase_df dataframe "basketValueGross" and "timeStamp" columns and maybe "month"
        # Aggregate purchase_df by month and year

        purchase_df["MonthYear"] = purchase_df["month"].astype(str) + "-" + purchase_df["year"].astype(str)

        # Then do a plot of total spend each month with a different colour for each year
        #purchase_df["MonthYear"] = purchase_df["month"].astype(str) + "-" + purchase_df["year"].astype(str)
        cost_month_year = purchase_df[["month", "year", "basketValueGross"]]
        # for each year, find the average spend per month
        cost_month_year["Average Monthly Spend (£)"] = cost_month_year.groupby(["year", "month"])["basketValueGross"].transform("mean")
        # Make this two decima places
        cost_month_year["Average Monthly Spend (£)"] = cost_month_year["Average Monthly Spend (£)"].round(2)
        # Drop duplicates and remove the basketvaluegross column
        cost_month_year = cost_month_year.drop_duplicates()
        cost_month_year = cost_month_year.drop(columns="basketValueGross")
        # Make the year have 0 decimal places
        cost_month_year["year"] = cost_month_year["year"].round(0)
        # Order by month number
        cost_month_year = cost_month_year.sort_values("month")
        # Make the month column have January for 1, February for 2 etc.
        cost_month_year["month"] = cost_month_year["month"].map({1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})

        #st.write(cost_month_year)
        spend_per_month = px.line(cost_month_year, x="month", y='Average Monthly Spend (£)', color='year', title="Average Spend per Month")
        st.plotly_chart(spend_per_month)

        colour_graph_info = st.toggle("Click for more info on this coloured line graph.")
        if colour_graph_info:
            st.info("This line chart shows the average amount of money you spent per month, for each year in your data. The x-axis shows the month and the y-axis shows the average amount of money you spent. Each line represents a different year, you can select which years to display above the chart! You can hover over the lines to see the exact values.")
        

        # Total monthly spend per year, top 5 product spends, top spending summary
        col1, col2 = st.columns(2)
        with col1:
            # Top 5 product spends
            product_df["Total Spend"] = product_df["price"] * product_df["quantity"]
            # For each product "name", sum the "Total Spend" column
            product_spend = product_df.groupby("name")["Total Spend"].sum().reset_index()
            # Sort the values in descending order
            product_spend = product_spend.sort_values("Total Spend", ascending=False).reset_index()
            # Get the top 5
            top5 = product_spend.head(3)
            
            st.header("What products have you spent the most on?")
            for row in top5.index:
                if row == 0:
                    nth = "1st"
                elif row == 1:
                    nth = "2nd"
                elif row == 2:
                    nth = "3rd"
                else:
                    nth = f"{row + 1}th"
                st.write("\n")
                st.info(f"{top5.loc[row, 'name']} was the {nth} top product by spend, with a total spend of £{top5.loc[row, 'Total Spend']:.2f}")
            st.write("\n")
            productspendinfo = st.toggle("Click for more info on how this was calculated!")
            if productspendinfo:
                st.write("We calculated this by looking at all the items you purchased and summing up how many times you bought them and how much they cost each time.")

        with col2:
            st.header("Summary of your spending:")
            st.write("\n")
            # Average highest spend category (do once the category data is in)
            # Largest basket spend and in what store and where
            largest_basket = purchase_df.loc[purchase_df["basketValueGross"].idxmax()]
            basket_val = largest_basket["basketValueGross"]
            # store_id = largest_basket["storeId"]
            # if store_id in store_loc["Store ID"].values:
            #     store_id = store_loc[store_loc["Store ID"] == store_id]["Store Name"].values[0]
            # else:
            #     store_id = False

            time_of_purchase = largest_basket["date"]
            
            if time_of_purchase == "nan-nan-nan":
                time_of_purchase = False
            else:
                time_of_purchase = time_of_purchase
                # Convert year-month-day into a more readable format
                year, month, day = time_of_purchase.split("-")
                # Round days, months and years to zero decimal places
                year, month, day = int(float(year)), int(float(month)), int(float(day))
                time_of_purchase = f"{day}/{month}/{year}"
            
            if time_of_purchase:
            #     st.info(f"The largest basket spend was £{largest_basket['basketValueGross']:.2f} at store {largest_basket['storeId']} on {largest_basket['timeStamp']}")
            # elif time_of_purchase:
            #     st.info(f"The largest basket spend was £{largest_basket['basketValueGross']:.2f} on {largest_basket['timeStamp']}")
            # elif store_id:
            #     st.info(f"The largest basket spend was £{largest_basket['basketValueGross']:.2f} at store {largest_basket['storeId']}")
            # else:
                st.info(f"The largest basket spend was £{largest_basket['basketValueGross']:.2f}")
            st.write("\n")
            # Most expensive product and when and where
            
            # Find the name of the most expensive product
        
            
            product_df["Spend per item"] = product_df["price"] / product_df["quantity"]
            #st.write(product_df)
            # Sort by largest Spend per item
            baskets = product_df.sort_values("Spend per item", ascending=False)[["name", "basket_id", "Spend per item"]]
            Name = baskets.iloc[0]["name"]
            Top_Spend = baskets.iloc[0]["Spend per item"]
            basket_no = baskets[baskets["Spend per item"] == Top_Spend]["basket_id"].values[0]

            #st.write("Basket no", basket_no)
            # Find the basket_id of the most expensive product
            #st.write(baskets)
            # Look at purchase_df for basket_id and find time and store
            #st.write(purchase_df)

            most_expensive = purchase_df[purchase_df["basket_id"] == basket_no]
            #store_id = most_expensive["storeId"].values[0]
            #st.write(store_id)
            
            time_of_purchase = most_expensive["date"]
            #st.write(time_of_purchase)
            if len(time_of_purchase) == 0:
                time_of_purchase = False
            else:
                time_of_purchase = time_of_purchase.values[0]
                # Convert year-month-day into a more readable format
                year, month, day = time_of_purchase.split("-")
                # Round days, months and years to zero decimal places
                year, month, day = int(float(year)), int(float(month)), int(float(day))
                time_of_purchase = f"{day}/{month}/{year}"
                
                

            #st.write(store_loc)
            # store_name = store_loc[store_loc["Store ID"] == store_id]["Store Name"].values
            # if len(store_name) == 0:
            #     store_name = False
            # else:
            #     store_name = store_name[0]

            # if time_of_purchase and store_name:
            #     st.info(f"The most expensive product was '{Name}' at £{Top_Spend:.2f} at store {store_name} purchased on {time_of_purchase}.")
            # elif time_of_purchase:
            #     st.info(f"The most expensive product was '{Name}' at £{Top_Spend:.2f} purchased on {time_of_purchase}.")
            # elif store_name:
            #     st.info(f"The most expensive product was '{Name}' at £{Top_Spend:.2f} at store {store_name}.")
            # else:
            #     st.info(f"The most expensive product was '{Name}' at £{Top_Spend:.2f}.")


        spend_over_time = px.line(purchase_df, x='timestamp', y='basketValueGross')
        spend_over_time.update_layout(title="Total Spend Over Time")
        
        spend_over_time.update_xaxes(title_text="Time")
        spend_over_time.update_yaxes(title_text="Total Spend (£)")
        st.plotly_chart(spend_over_time)

        totalspendinfo = st.toggle("Click for more info on the chart")
        if totalspendinfo:
            st.info("This line chart shows the total amount of money you spent over time. The x-axis shows the time and the y-axis shows the total amount of money you spent. You can hover over the line to see the exact values. If you scroll down you can see some summary stats and breakdowns per month.")            
        
    # elif selected == "Stores (Location)":

    #     #store_purchase_count = cp.store_purchase_counter(purchase_df)
    #     #monthly_visits = cp.monthly_frequency(purchase_df)

    #     col1, col2 = st.columns(2)

    #     with col1:
    #         st.header("Monthly Frequency:")
    #         # Write the 'year' column as integers
    #         monthly_visits['year'] = monthly_visits['year'].astype(int)
    #         year_list = monthly_visits['year'].unique()
    #         # Remove the "MonthYear" column
    #         monthly_visits = monthly_visits.drop(columns='MonthYear')

    #         # If there is a year without one of the months, add it to the dataframe with 0 visits
            
    #         for year in year_list:
    #             for month in range(1, 13):
    #                 if month not in monthly_visits[monthly_visits['year'] == year]['month'].values:
    #                     monthly_visits.loc[len(monthly_visits), monthly_visits.columns] = year, month, 0
            

    #         # Make a new column with the month name, by mapping the month number to the month name
    #         monthly_visits['Month Name'] = monthly_visits['month'].map({1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'})
    #         # Order monthly_visits by month number
    #         monthly_visits = monthly_visits.sort_values('month')
    #         # Get a list of unique years for making the multi select widget
                   
    #         # Make a multi select widget where the options are th eyears in the year_list, and the default is all years
    #         year_options = st.multiselect("Select years to display", year_list, default=year_list)
    #         # Filter the data based on the years that are checked
    #         monthly_visits = monthly_visits[monthly_visits['year'].isin([year for year in year_options])]
    #         # Plot a little line chart of these
    #         monthchart = px.line(monthly_visits, x="Month Name", y="Visits", color="year", title='Monthly Frequency of shopping trips')
    #         st.plotly_chart(monthchart)

    #         month_info = st.toggle("Click for more info on the chart")
    #         if month_info:
    #             st.info("This chart shows the frequency of shopping trips per month, for each year. The x-axis shows the month, and the y-axis shows the number of shopping trips. Each line represents a different year, you can select which years above the chart!")

    #     with col2:
    #         st.header("Store Purchase Counts:")
    #         # This is silly but it works to set the size of the markers on the map
    #         store_gdf["Point Size"] = 1
    #         non_zero_store_gdf["Point Size"] = 1
            
    #         # Check if there are 3 or more stores with purchases
    #         if len(non_zero_store_gdf) >= 3:
    #             Top3 = min(non_zero_store_gdf["Number of Purchases"].nlargest(3))
    #         else:
    #             Top3 = 0
    #         # Make a new column that is 
    #         non_zero_store_gdf["Top 3?"] = non_zero_store_gdf["Number of Purchases"] >= Top3
    #         # Commented out to remove widget for now
    #         #map_widget = st.radio("Toggle to see all stores or only stores with purchases", ["Show all stores", "Show only stores with purchases"])
    #         map_widget = "Show only stores with purchases"

    #         if map_widget == "Show all stores":
    #             map_chart = px.scatter_mapbox(store_gdf, lat=store_gdf.geometry.y, lon=store_gdf.geometry.x, color="Top 3?", size="Point Size", color_discrete_sequence=px.colors.qualitative.G10, 
    #             opacity = 0.7, hover_data=["Store Name", "Number of Purchases"], labels=["Store Name", "Number of Purchases"], title = "All Store Purchases")
    #             # Find the central lat and lon of the points in non_zero_store_gdf
    #             lat_centre = store_gdf["lat"].mean()
    #             lon_centre = store_gdf["lon"].mean()
    #             map_chart.update_layout(mapbox_style="carto-positron", mapbox_zoom=5, mapbox_center={"lat": lat_centre, "lon": lon_centre})

    #         if map_widget == "Show only stores with purchases":
                
    #             map_chart = px.scatter_mapbox(non_zero_store_gdf, lat=non_zero_store_gdf.geometry.y, lon=non_zero_store_gdf.geometry.x, color="Top 3?", size="Point Size", color_discrete_sequence=px.colors.qualitative.G10,
    #             opacity = 0.7, hover_data=["Store Name", "Number of Purchases"], labels=["Store Name", "Number of Purchases"], title = "Stores where you have shopped")

    #             # Find the central lat and lon of the points in non_zero_store_gdf
    #             lat_centre = non_zero_store_gdf["lat"].mean()
    #             lon_centre = non_zero_store_gdf["lon"].mean()
    #             map_chart.update_layout(mapbox_style="carto-positron", mapbox_zoom=5, mapbox_center={"lat": lat_centre, "lon": lon_centre})
    #         st.plotly_chart(map_chart)

    #         map_info = st.toggle("Click for more info on the map")
    #         if map_info:
    #             st.info("This interactive map shows the locations of Tesco stores. You can pan and zoom to move around and see different areas. You can toggle to see just the stores you have purchased at or all stores we have data for. When you toggle, the map recentres. There's a colour scale for the points that represents how many times you have shopped at them, but you can also hover over the points to see the store name and exact number of purcahses.")


    #     # Output 5 stores, number of purchases at each store and total spend in these stores

        
    #     # Take purchase_df and make a new df with one row per Store ID, sum the basket value
    #     store_spend = purchase_df.groupby("storeId")["basketValueGross"].sum().reset_index()
    #     store_spend = store_spend.rename(columns={"storeId": "Store ID", "basketValueGross": "Total Spend"})
    #     # Set Store ID as the index
    #     store_spend["Store ID"] = store_spend["Store ID"].astype(int)
    #     store_spend = store_spend.set_index("Store ID")

        
    #     # Make a new dataframe with the store ID, store name, number of purchases and total spend
    #     useful_stores_df = non_zero_store_gdf[["Store Name", "Number of Purchases"]]
    #     #st.write(useful_stores_df)

    #     # Combine the two dataframes
    #     store_info = useful_stores_df.join(store_spend)
    #     store_info["Average spend"] = store_info["Total Spend"] / store_info["Number of Purchases"]
    #     # Set average spend and total spend to 2 decimal places
    #     store_info["Average spend"] = store_info["Average spend"].round(2)
    #     store_info["Total Spend"] = store_info["Total Spend"].round(2)

    #     #Add a £ sign to the total spend and average spend columns
    #     store_info["Total Spend"] = "£" + store_info["Total Spend"].astype(str)
    #     store_info["Average spend"] = "£" + store_info["Average spend"].astype(str)
    #     st.header("Where have you been shopping and how much did you spend there?")
    #     # For plotting, reset the index
    #     store_info_plot = store_info.reset_index()
    #     st.write(store_info_plot)
        

    elif selected == "Products types":
        

        most_frequent_products = cp.most_frequent_products_calc(product_df)
        col1, col2 = st.columns(2)
        with col1:
            # Food categories by number of products
            CategoryNumbers = product_df["Category"].value_counts()
            # Remove "Unknown" category but keep the count
            unknown_count = CategoryNumbers["Unknown"]
            sum_cat = CategoryNumbers.sum()
            
            CategoryNumbers = CategoryNumbers.drop("Unknown")
            
            unknown_percent = (unknown_count / sum_cat) * 100
            category_pie = px.pie(CategoryNumbers, names=CategoryNumbers.index, values=CategoryNumbers, title="Number of products in each category")
            st.plotly_chart(category_pie)
            st.write(f"There are {unknown_count} products with an unknown category which is {unknown_percent:.1f} % of the total products.")
            pieinfo1 = st.toggle("Click for more info on this pie chart about the number of products per category.")
            if pieinfo1:
                st.info("This pie chart shows the percentages of products you have purchased in each category. You can hover over the slices to see the exact number of products in each category.")

        with col2:
            # Money spent per category
            # Make a new column with the total spend per product
            product_df["Total Spend (£)"] = product_df["price"] * product_df["quantity"]
            # Group by category and sum the total spend
            category_spend = product_df.groupby("Category")["Total Spend (£)"].sum().reset_index()
            # Remove "Unknown" category but keep the count
            unknown_spend = category_spend[category_spend["Category"] == "Unknown"]["Total Spend (£)"].values[0]
            category_spend = category_spend[category_spend["Category"] != "Unknown"]
            # Make a bar chart of this
            category_spend_pie = px.pie(category_spend, names="Category", values="Total Spend (£)", title="Total Spend per category (£)")
            category_spend_pie.update_traces(textinfo='value')
            st.plotly_chart(category_spend_pie)

            st.write(f"You spent £{unknown_spend:.2f} on products with an unknown category.")
            pieinfo2 = st.toggle("Click for more info on this pie chart about the total spend per category.")
            if pieinfo2:
                st.info("This pie chart shows the total amount of money you spent on products in each category. You can hover over the slices to see the exact amount of money spent in each category.")

        st.header("See the 5 products you purchased the most of for each category:")
        topinfo = st.toggle("Click for more info on the top 5 products per category")
        if topinfo:
            st.write("You can pick a product type from the dropdown below. Then you can see the top 5 products you purchased the most of for each category. If there are less than 5 products in a category then you'll just see all of them.")
        # Want to see the top 5 purchased products for each category
        category_selector = st.selectbox("Select a category to see the top 5 products", product_df["Category"].unique())
        # Filter the product_df to only include the selected category
        category_df = product_df[product_df["Category"] == category_selector]
        # Group by the product name and sum the quantity
        product_counts = category_df.groupby("name")["quantity"].sum().reset_index()
        # Sort the values in descending order
        product_counts = product_counts.sort_values("quantity", ascending=False).reset_index(drop=True)
        # Get the top 5
        if len(product_counts) < 5:
            st.write("There are less than 5 products in this category.")
            n = len(product_counts)
        else:
            n = 5
        for row in range(n):
            st.write("\n")
            st.info(f"You bought {product_counts.loc[row, 'quantity']:.0f} of '{product_counts.loc[row, 'name']}'.")

        # Going to do bar charts which have different colours for different years and show the total spend per category
        # Look at product_df and add a year column by comparing basket_id to purchase_df
        product_df["year"] = product_df["basket_id"].map(purchase_df.set_index("basket_id")["year"])
        # Group by category and year and sum the total spend
        categ_spend = product_df.groupby(["Category", "year"])["Total Spend (£)"].sum().reset_index()
        # Make a bar chart of this
        categ_spend_bar = px.histogram(product_df, barmode = "group", x="Category", y="Total Spend (£)", color="year", title="Total Spend per category (£)")
        st.plotly_chart(categ_spend_bar)
        categ_spend_info = st.toggle("Click for more info on this bar chart about total spend per category.")
        if categ_spend_info:
            st.info("This bar chart shows the total amount of money you spent on products of different categories. The bars are grouped by category and coloured by year.")

    elif selected == "Price changes":
        
        # Working with price_change df

        # For each item, see how many times it was purchased
        product_counts = price_change['name'].value_counts()
        # Filter out the products that were only purchased once
        product_counts = product_counts[product_counts > 1]
        # Filter price change to only include the products that were purchased more than once
        merged_df = price_change[price_change['name'].isin(product_counts.index)]
        # Create a list of unique product names for the dropdown
        product_names = merged_df['name'].unique()

        product_select = st.selectbox("Select a product to view price changes", product_names)

        # Create a figure with a line chart
        fig = px.line(merged_df[merged_df['name'] == product_select], x='timestamp', y='price', title="Product Price Change Over Time")
        # Make the x axis label "Time" and the y axis label "Price (£)"
        fig.update_xaxes(title_text="Time")
        fig.update_yaxes(title_text="Price (£) per unit")
        # Update the title
        fig.update_layout(title=f"How the price of {product_select} changes over time")
        
        #Show the plot
        st.plotly_chart(fig)

        

        st.header("The items with the biggest increase in price:")
        #nonzero_toggle = nonzero_toggle = st.toggle("Show only non-zero price changes")

        
        # Plot the  biggest price increases from item_change
        item_change = item_change.sort_values('Price_Percent_Change', ascending=False).reset_index(drop=True)
        top5 = item_change[['name', 'Price_Percent_Change', 'max_price', 'max_date', 'min_price', 'min_date']].head(5)
        for row in top5.index:
            st.write("\n")
            st.info(f"{top5.loc[row, 'name']} had a price increase of {top5.loc[row, 'Price_Percent_Change']:.2f}% from £{top5.loc[row, 'min_price']} on {top5.loc[row, 'min_date']} to £{top5.loc[row, 'max_price']} on {top5.loc[row, 'max_date']}")
            
        percent_info = st.toggle("Click to see what we mean by price percentage increase", value=False)
        if percent_info:
            st.header("What is a price percentage increase?")
            st.write("\n")
            st.write("The price percentage increase is calculated by taking the difference between the maximum and minimum price, dividing by the minimum price and multiplying by 100. This gives the percentage increase in price over the time period.")
            st.write("\n")
            # This means a 100% increase is a doubling in price, a 50% increase is a 1.5x increase in price etc.
            st.write("A 100% increase is a doubling in price (so £1 goes to £2), a 50% increase is a 1.5x increase in price (so £1 goes to £1.50)")
            st.write("\n")
            st.write("This is useful to see how much the price increased proportional to how much the original price was.")

# Note this if statement is outside the big if about if product df and purchase df are loaded, because we want people to be able to see this even if the data isn't loaded
if selected == "App Guide":

    st.header("I want to use this app but don’t have my Tesco data file. How do I request it from Tesco?​")

    st.write("If you are registered for a Clubcard, you can request your data through Tesco to be sent to you via email.")

    st.write("1. Search in your browser: “Tesco Data Portability” and navigate to the login page.")
    st.write("2. Sign into your account and request your data to be sent to your email.")
    st.write("3. Your data should be sent to you within 30 days – you will be emailed a JSON file which you can upload directly to this app.")

    # Insert dataportabilitypage.png
    st.image("images/dataportabilitypage.png", caption="Tesco Data Portability page")

    st.header("How do I upload my Data?")

    # Insert Uploadhere.png
    st.image("images/Uploadhere.png", caption="Upload your data here")

    st.header("How do I see more information after the first page?")

    # Insert Menu.png
    st.image("images/Menu.png", caption="Click on the menu to see more pages")

    st.header("How do I interact with the graphs?")

    # Insert GraphGuide.png
    st.image("images/GraphGuide.png", caption="Click on the graph to see more options")

    st.write("You can move the graphs and plots by hovering with your curser and dragging the plot OR by using the navigation pane that appears in the top right corner of the graph.")

    st.header("I have lost the data in the graph, and I can't see any of the data anymore, how do I get back?​")

    # Insert ResetZoom.png
    st.image("images/ResetZoom.png", caption="Click on the reset axes button to get back to the original view")
    
    st.write("If you have moved the graph and can’t get back to the original view, try ‘Reset Axes’ or the ‘Auto Scale’ buttons. If that doesn’t work – click on a different page and come back to this page – it should reset automatically. ​")


        
        

        