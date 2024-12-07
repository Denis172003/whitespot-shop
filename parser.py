import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
import contextily as ctx

gdf = gpd.read_file("RomaniaPopulation")
gdf = gdf[["population", "geometry"]]
gdf = gdf.to_crs("EPSG:4326")

minx, miny, maxx, maxy = 25.94, 44.36, 26.28, 44.54  # Example coordinates
bbox = box(minx, miny, maxx, maxy)

gdf_clipped = gdf[gdf.intersects(bbox)]

fig, ax = plt.subplots(figsize=(10, 10))
gdf_clipped.plot(column='population', cmap='viridis', legend=True, ax=ax, alpha=0.35)

ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_clipped.crs.to_string())
ax.set_title("Population Density in Bucharest (Clipped Data)", fontsize=15)

plt.show()