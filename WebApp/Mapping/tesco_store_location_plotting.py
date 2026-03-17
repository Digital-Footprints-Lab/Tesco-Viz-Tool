import numpy as np
#import fiona ### having issues with compatability of this package - hence not used geopandas to plot currently 
import geopandas
import pandas as pd
import matplotlib.pyplot as plt 
from geodatasets import get_path 
import shapefile as shp
import seaborn as sns
from mpl_toolkits.basemap import Basemap


##import lat lon file for tesco store locations 
df = pd.read_csv("tesco_store_lat_lon.csv")
## read pandas dataframe lat lon values into geopandas
gdf = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.lon, df.lat), crs="EPSG:4326")
##Below plots the points of where locations are without a basemap behind
##I was getting errors importing .shp files using geopands - specifically with fiona dependency - hence I went a new route using more basic Basemap
#gdf.plot()
#plt.show()

#### Layer with BASEMAP ####
## Equidistant Cylindrical Projection of UK map - coordinates show 'llc' lower left corner, right corners ect of chosen lat lon to limit World map to UK 
fig, ax = plt.subplots()
m = Basemap(projection='merc', lat_0 = 55, lon_0 = -4,
    resolution = 'i', area_thresh = 0.05,
    llcrnrlon=-9, llcrnrlat=49,
    urcrnrlon=2, urcrnrlat=61)
m.drawcoastlines(linewidth = 0.2, zorder = 0)
x, y = m(df.lon,df.lat) # convert Store loc from lat-long to x,y coordinates 
m.scatter(x,y,0.5,marker='o',color='k')
no_stores_plot = np.count_nonzero(~np.isnan(x))
plt.title("Locations of Tesco Stores UK (N = "+str(no_stores_plot)+")")
plt.show()
