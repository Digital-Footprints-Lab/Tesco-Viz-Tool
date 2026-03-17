import streamlit as st
import pandas as pd
import plotly.express as px

ShoppingTrips = pd.read_csv('ShoppingTrips.csv')
TripsMelt = pd.melt(ShoppingTrips, id_vars = 'Month', var_name = 'Product', value_name = 'Quantity')

dates = ShoppingTrips['Month']

ShoppingCosts = pd.read_csv('ShoppingCost.csv')
CostsMelt = pd.melt(ShoppingCosts, id_vars = 'Month', var_name = 'Product', value_name = 'Cost')

TripsMin = TripsMelt['Quantity'].min()
TripsMax = TripsMelt['Quantity'].max()

CostsMin = CostsMelt['Cost'].min()
CostsMax = CostsMelt['Cost'].max()

chart1 = px.scatter(
    data_frame = ShoppingTrips,
    x = "Weetabix",
    y = "Milk",
    hover_name = "Month",
    title = "Weetabix vs Milk")

chart2 = px.scatter(
    data_frame = ShoppingCosts,
    x = "Month",
    y = "Total",
    hover_name = "Month",
    title = "Total Cost of Shopping")

#st.title('Shopping Trolley Secrets')

# st.header('This is a header')

# st.write('This is Huw trying to make a data app')

# st.info('Here is an information box!')

with st.sidebar:
    st.title('Shopping Trolley Secrets')
    user_name = st.text_input("Hi there! Please enter your name.")

    animate_vis = st.checkbox(
        label="Animate",
        value = False)

    date_widget = st.slider(
        label="Which month do you want to chart?",
        min_value=min(dates),
        max_value=max(dates),
        disabled = animate_vis)
    
    cost_widget = st.checkbox(
        label = "Do you want to see the cost of items?",
        value = True)
    
    
#column1, column2 = st.columns(2)
column1, column2 = st.columns([3, 1])

with column1:
    st.info('Welcome to the shopping trolley secrets app:')

with column2:
    st.info(f"{user_name}")

tab1, tab2 = st.tabs(["Data", "Visualisation"])

with tab1:
    st.info('Here is the information about what was purchased each month:')
    st.dataframe(ShoppingTrips)

    st.info('And here is the information on how much it cost (in £, need 2dp here!):')
    st.dataframe(ShoppingCosts)

    st.info('Select the items you want to see on the X and Y axis.')

    tab1col1, tab1col2 = st.columns(2)
    with tab1col1:
        x_data_widget = st.radio(
        label = "X-axis:",
        options = ShoppingTrips.columns[1:])

    with tab1col2:
        y_data_widget = st.radio(
        label = "Y-axis:",
        options = ShoppingTrips.columns[1:])

    
    chart_toggle = px.scatter(
        data_frame = ShoppingTrips,
        x = x_data_widget,
        y = y_data_widget,
        title = f"{x_data_widget} vs {y_data_widget}")
    
    st.plotly_chart(chart_toggle)

with tab2:
    # st.plotly_chart(chart1)
    # st.plotly_chart(chart2)

    st.write('Here are some charts to help you understand your shopping habits. You can use the slider in the sidebar to select the month you want to see.')
    
    if cost_widget:
        st.info(f"Total cost of shopping in month {date_widget} was: £{ShoppingCosts.iloc[date_widget-1]['Total']:.2f}")

        chart5 = px.line(
            data_frame = ShoppingCosts,
            x = "Month",
            y = "Total",
            title = "Total Cost of Shopping each month (£)")

        st.plotly_chart(chart5)

    if animate_vis == False:
        chart3 = px.bar(
            data_frame = TripsMelt[TripsMelt["Month"] == date_widget],
            x = "Product",
            y = "Quantity",
            title = "How much did you buy in month " + str(date_widget) + "?",
            range_y = [TripsMin, TripsMax])

        chart4 = px.bar(
            data_frame = CostsMelt[CostsMelt["Month"] == date_widget],
            x = "Product",
            y = "Cost",
            title = "How much did you spend in month " + str(date_widget) + "?",
            range_y = [CostsMin, CostsMax])
        
    elif animate_vis == True:
        chart3 = px.bar(
            data_frame = TripsMelt,
            x = "Product",
            y = "Quantity",
            title = "How much did you buy each month?",
            animation_frame = "Month",
            range_y = [TripsMin, TripsMax])


        chart4 = px.bar(
            data_frame = CostsMelt,
            x = "Product",
            y = "Cost",
            title = "How much did you spend each month?",
            animation_frame = "Month",
            range_y = [CostsMin, CostsMax])
        
    st.plotly_chart(chart3)
    st.plotly_chart(chart4)
        



