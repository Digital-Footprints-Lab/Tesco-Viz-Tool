import streamlit as st
import json
import pandas as pd
import plotly.express as px
import clubcard_pipeline as cp
import time

st.session_state.setdefault("loading", None)
st.session_state.setdefault("uploaded_file", None)
st.session_state.setdefault("purchase_df", None)
st.session_state.setdefault("product_df", None)
st.session_state.setdefault("slider", 1)

# Main page

if not st.session_state["loading"]:
    uploaded_file = st.file_uploader("Upload your Tesco clubcard data here", type="json")
    st.session_state["uploaded_file"] = uploaded_file

if st.session_state["uploaded_file"] is not None:
    st.session_state["loading"] = True

    with st.spinner("Loading..."):
        #start = time.time()
        uploaded_file = st.session_state["uploaded_file"]
        tesco_clubcard_data = json.load(uploaded_file)
        purchase_df, product_df = cp.clubcard_process(tesco_clubcard_data)
        
        st.session_state["purchase_df"] = purchase_df
        st.session_state["product_df"] = product_df
        
        #end = time.time()  
        


if st.session_state["purchase_df"] is not None and st.session_state["product_df"] is not None:
    purchase_df, product_df = st.session_state["purchase_df"], st.session_state["product_df"]

with st.sidebar:
    st.sidebar.title('Shopping Trolley Secrets')

# if uploaded_file is not None:
      
tab1, tab2, tab3 = st.tabs(["Summary Stats", "Most Frequent Products", "Store Purchase Counts"])
    
   
if st.session_state["purchase_df"] is not None and st.session_state["product_df"] is not None:
    with tab1:
        total_money_spent, total_savings, average_basket_value = cp.kpi_calculator(purchase_df)
        st.header("Summary Stats:")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"Total Money Spent: £{total_money_spent:.2f}")
        with col2:
            st.info(f"Total Savings: £{total_savings:.2f}")
        with col3:
            st.info(f"Average Basket Value: £{average_basket_value:.2f}")

    with tab2:
        most_frequent_products = cp.most_frequent_products(product_df)
    
        st.info("Most Frequent Products:")
        st.write(most_frequent_products)

        length = most_frequent_products.shape[0]
        st.write(length)
        slider = st.slider(label="I want to see the top n most frequently purchased products",
            on_change=None,
            min_value=1,
            max_value=min(20, length))
        
        st.write(st.session_state.slider)

        # The slider for this barchart does not work yet - it is not updating the value of st.session_state.slider

        barchart = px.bar(
        most_frequent_products.head(st.session_state.slider), 
        x='Product Name', y='Frequency', 
        title=f'Top {st.session_state.slider} Most Frequently Purchased Products')
    
        st.plotly_chart(barchart)

    with tab3:
        store_purchase_count = cp.store_purchase_count(purchase_df)
        monthly_visits = cp.monthly_frequency(purchase_df)
        col1, col2 = st.columns(2)
        with col1:
            st.info("Store Purchase Counts:")
            st.write(store_purchase_count)
        with col2:
            st.info("Monthly Frequency:")
            st.write(monthly_visits)