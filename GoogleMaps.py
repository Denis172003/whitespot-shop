import googlemaps
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from dotenv import load_dotenv
import os
from pyproj import Proj


# Load environment variables
load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # Your Google Maps API Key

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

# Define coordinates bounding box
minx, miny, maxx, maxy = 25.94, 44.36, 26.28, 44.54


def search_shops(api_client, center_lat, center_lng, radius, keywords):
    """
    Search Google Maps for specific shop types around a center point within a radius.

    Args:
    - api_client: Google Maps API client instance.
    - center_lat: Latitude for the center of the bounding box.
    - center_lng: Longitude for the center of the bounding box.
    - radius: Search radius in meters.
    - keywords: List of keywords (store names) to filter search results.

    Returns:
    - List of matching shops' locations with their coordinates and names.
    """
    all_shops = []
    
    for keyword in keywords:
        # Perform nearby search using Google Maps API
        result = api_client.places_nearby(
            location=(center_lat, center_lng),
            radius=radius,
            keyword=keyword
        )
        
        # Parse the response and append results
        for place in result.get("results", []):
            lat = place["geometry"]["location"]["lat"]
            lng = place["geometry"]["location"]["lng"]
            name = place.get("name", "")
            all_shops.append({"name": name, "latitude": lat, "longitude": lng})
    
    return all_shops


# Define the bounding box's approximate center point and radius
center_latitude = (44.36 + 44.54) / 2  # Middle of the bounding box latitudes
center_longitude = (25.94 + 26.28) / 2  # Middle of the bounding box longitudes
search_radius = 3000  # Search radius in meters

# Define the shops to search
shop_keywords = ["Mega Image", "Lidl", "La2Pasi", "Kaufland", "Profi", "Carrefour"]

# Call the function to search for shops
shops_data = search_shops(gmaps, center_latitude, center_longitude, search_radius, shop_keywords)

# Convert shop coordinates into GeoDataFrame
gdf_data = gpd.GeoDataFrame(
    shops_data,
    geometry=[Point(shop["longitude"], shop["latitude"]) for shop in shops_data],
    crs="EPSG:4326",
)

# Reproject to web-mercator for compatibility with contextily basemap
gdf_data = gdf_data.to_crs(epsg=3857)

# Correctly reproject the bounding box limits to match web-mercator
proj = Proj('epsg:3857')
projected_minx, projected_miny = proj(minx, miny)
projected_maxx, projected_maxy = proj(maxx, maxy)

# Plotting with contextily basemap
fig, ax = plt.subplots(figsize=(12, 12))

# Add basemap with contextily
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik)

# Plot the shop locations
gdf_data.plot(ax=ax, markersize=50, color="red", label="Shops")

# Set bounding box limits in reprojected web-mercator coordinates
ax.set_xlim(projected_minx, projected_maxx)
ax.set_ylim(projected_miny, projected_maxy)

# Set titles and legends
ax.set_title("Shops in Bucharest's Bounding Box", fontsize=15)
plt.legend()
plt.show()
