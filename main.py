import pandas as pd
import numpy as np

import geopandas as gpd
import time
import geoplot as gplt
from matplotlib import pyplot as plt
import mapclassify
from cmcrameri import cm
import geoplot.crs as gcrs
from matplotlib.colors import rgb2hex
from matplotlib.colors import ListedColormap

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
# pd.set_option('display.max_colwidth', None)
 
SHDIComplete = pd.read_csv('data/SHDI Complete 4.0 (1).csv', usecols=['level', 'year', 'GDLCODE', 'shdi', 'healthindex',
                                                                      'incindex', 'edindex', 'lifexp', 'gnic', 'esch',
                                                                      'msch', 'pop'])
SHDIComplete = SHDIComplete[SHDIComplete['level'] == 'Subnat']
SHDI_first = SHDIComplete[SHDIComplete['year'] == 1990]
SHDI_first = SHDI_first[['GDLCODE', 'shdi']]
SHDI_first['shdi'] = SHDI_first['shdi'].astype(float)

try:
    countries_gdf = gpd.read_file("data/GDL Shapefiles V4.shp")
except Exception as  e:
    countries_gdf = gpd.read_file("data/GDL Shapefiles V4.zip")

try:
    world = gpd.read_file("data/world_data_administrative_boundaries_country_level.shp")
except Exception as  e:
    world = gpd.read_file("data/world_data_administrative_boundaries_country_level.zip")

# TODO: Make into gifs
# TODO: Make legend have "No Data" for 0


countries_gdf = countries_gdf[['GDLcode', 'geometry']]
countries_gdf.rename(columns={'GDLcode': 'GDLCODE'}, inplace=True)

countries_gdf = countries_gdf.merge(SHDI_first, on='GDLCODE', how='left')
countries_gdf['shdi'].fillna(-1, inplace=True)
scheme = mapclassify.UserDefined(countries_gdf['shdi'],
                                 bins=[0, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 1.0])

background_color = '#d1e5f0'
missing_color = 'grey'
fig, ax = plt.subplots(figsize=(20, 10), facecolor=background_color,
                       subplot_kw={
                           'projection': gcrs.Robinson(),
                           # https://scitools.org.uk/cartopy/docs/latest/crs/projections.html
                           'facecolor' : background_color}

                       )
plt.title('Human Development Index by World Subdivisions', fontdict={'fontsize': 20, 'fontweight': 'bold'})

cmap = plt.cm.get_cmap('Blues', len(scheme.bins) + 1)
cmap_list = [rgb2hex(cmap(i)) for i in range(cmap.N)]
cmap_list.insert(0, missing_color)
cmap_world = ListedColormap(cmap_list)

gplt.polyplot(world, ax=ax, facecolor=missing_color, linewidth=0.05, )

gplt.choropleth(countries_gdf,
                # projection=gcrs.Robinson(),
                ax=ax,
                hue=countries_gdf['shdi'],
                scheme=scheme,
                cmap=cmap_world,
                legend_kwargs={'loc'      : 'lower left',
                               'fontsize' : 10,
                               'frameon'  : True,
                               'edgecolor': background_color,
                               'facecolor': background_color},
                linewidth=0.1,
                extent=(-180, -90, 180, 90),
                legend=True, )

plt.tight_layout()

fig.show()
