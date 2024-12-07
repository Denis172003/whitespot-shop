import googlemaps
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import contextily as ctx
from dotenv import load_dotenv
import os
import time

load_dotenv()
API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")  # Your Google Maps API Key

# Initialize the Google Maps client
gmaps = googlemaps.Client(key=API_KEY)

# Define coordinates bounding box
minx, miny, maxx, maxy = 25.94, 44.36, 26.28, 44.54

def search_shops(api_client, center_lat, center_lng, radius, keywords):
    all_shops = []
    
    for keyword in keywords:
        next_page_token = None
        while True:
            try:
                # Perform nearby search using Google Maps API
                result = api_client.places_nearby(
                    location=(center_lat, center_lng),
                    radius=radius,
                    keyword=keyword,
                    page_token=next_page_token
                )

                # Parse the results and append them to all_shops
                for place in result.get("results", []):
                    lat = place["geometry"]["location"]["lat"]
                    lng = place["geometry"]["location"]["lng"]
                    name = place.get("name", "")
                    all_shops.append({"name": name, "latitude": lat, "longitude": lng})

                # Get the next page token, if available
                next_page_token = result.get("next_page_token", None)

                # If there is a next page, wait for a few seconds before requesting the next page
                if next_page_token:
                    time.sleep(2)  # Adjust the delay if necessary

                # If there's no next page, exit the loop
                if not next_page_token:
                    break

            except Exception as e:
                print(f"Error while requesting data: {e}")
                break

    return all_shops



# Define the bounding box's approximate center point and radius
center_latitude = (44.36 + 44.54) / 2  # Middle of the bounding box latitudes
center_longitude = (25.94 + 26.28) / 2  # Middle of the bounding box longitudes
search_radius = 10000  # Search radius in meters

# Define the shops to search
shop_keywords = ["Mega Image", "Lidl", "La2Pasi", "Kaufland", "Profi", "Carrefour"]

# Call the function to search for shops
shops_data = search_shops(gmaps, center_latitude, center_longitude, search_radius, shop_keywords)

# Process and visualize results using geopandas
# Convert shop coordinates into GeoDataFrame
gdf_data = gpd.GeoDataFrame(
    shops_data,
    geometry=[Point(shop["longitude"], shop["latitude"]) for shop in shops_data],
    crs="EPSG:4326",
)

# Plotting with contextily basemap
fig, ax = plt.subplots(figsize=(12, 12))

# Plot the shop locations
gdf_data.plot(ax=ax, markersize=10, color="red", label="Shops")

# Add basemap with contextily
ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, crs=gdf_data.crs.to_string())

# Set titles and legends
ax.set_title("Shops in Bucharest's Bounding Box", fontsize=15)
plt.legend()
plt.show()
