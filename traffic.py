import json
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import box
import contextily as ctx
import osmnx as ox
import random

# Step 1: Get the road network for Bucharest
print("Downloading road network for Bucharest...")
bucharest_graph = ox.graph_from_place('Bucharest, Romania', network_type='drive')

# Convert to GeoDataFrame
gdf_nodes, gdf_edges = ox.graph_to_gdfs(bucharest_graph)

# Step 2: Add simulated traffic data (0 = no traffic, 1 = heavy traffic)
gdf_edges['congestion'] = [random.uniform(0, 1) for _ in range(len(gdf_edges))]

# You can use traffic intensity to define the color (green for low, red for high congestion)
gdf_edges['color'] = gdf_edges['congestion'].apply(lambda x: 'red' if x > 0.75 else ('orange' if x > 0.5 else 'green'))

# Step 3: Clip the road network to the same bounding box
minx, miny, maxx, maxy = 25.94, 44.36, 26.28, 44.54  # Example coordinates for Bucharest
bbox = box(minx, miny, maxx, maxy)

gdf_clipped_roads = gdf_edges[gdf_edges.intersects(bbox)]

# Step 4: Save traffic information in a dictionary
traffic_dict = {}

for idx, row in gdf_clipped_roads.iterrows():
    road_id = row['osmid'] if isinstance(row['osmid'], (int, str)) else f"road_{idx}"  # Ensure road_id is unique and hashable
    congestion = row['congestion']
    color = row['color']
    coordinates = list(row['geometry'].coords)
    
    traffic_dict[road_id] = {
        'congestion': congestion,
        'color': color,
        'coordinates': coordinates
    }

# Step 5: Save the dictionary to a JSON file
json_file_path = "traffic_info.json"
with open(json_file_path, 'w') as json_file:
    json.dump(traffic_dict, json_file, indent=4)

print(f"Traffic data saved to {json_file_path}")

# Step 6: Plot the traffic congestion map (optional)
fig, ax = plt.subplots(figsize=(10, 10))
for _, row in gdf_clipped_roads.iterrows():
    line_coords = list(row['geometry'].coords)
    color = row['color']  # red, orange, green (based on traffic)
    # Plot each road with its respective color
    plt.plot(*zip(*line_coords), color=color, linewidth=2)

# Add basemap
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_clipped_roads.crs.to_string())

# Title and visualization
ax.set_title("Traffic Intensity in Bucharest (Clipped Area)", fontsize=15)
plt.show()
