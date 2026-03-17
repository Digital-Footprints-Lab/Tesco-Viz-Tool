# SupermarketViz
Seedcorn project with Huw + Laura Fryer on visualising Tesco clubcard data

Currently private repo but will make public for deployment :)

Using Al Tanner's streamlit tutorial as a starting point: https://altanner.github.io/graphical-data-apps/

And this code for processing clubcard JSON through pipeline: https://github.com/cristina-projects/Tesco-Clubcard-Data-Analysis

## Instructions on running the app

1. Make sure you've got "clubcard_pipeline.py", "clubcardapp.py", "unique_products.csv" and "tesco_store_lat_lon.csv" in your directory
2. Make sure your environment has the required dependencies (e.g. streamlit, pandas etc.)
3. In your terminal activate your environment
4. And then run:
```
streamlit run clubcardapp.py
```
in your terminal and then the app should open up in your browser.

5. Load in your Tesco clubcard data JSON file within the app
