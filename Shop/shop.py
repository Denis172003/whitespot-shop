import folium
import requests
import os
import json
print(os.getcwd())  # Prints the current working directory


# Geocoding function to get latitude and longitude for a given address
def geocode_address(address, api_key):
    """Geocode an address using the Google Maps Geocoding API."""
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url)
    data = response.json()
    
    if data['status'] != 'OK':
        print(f"Error geocoding {address}: {data}")
        return None
    
    lat = data['results'][0]['geometry']['location']['lat']
    lng = data['results'][0]['geometry']['location']['lng']
    print(f"Geocoded {address}: ({lat}, {lng})")
    return lat, lng

# Your Google Maps API key (replace this with your own key)
api_key = "AIzaSyCAf6wpKSjh_nHVxGC82NG_7KdHPXYgMcM"

# Load store data from the JSON file
with open('Shop/stores.json', 'r') as file:
    store_data = json.load(file)

lidl_stores = store_data["lidl_stores"]
mega_image_stores = store_data["mega_image_stores"]
profi_stores = store_data["profi_stores"]
la_doi_pasi_stores = store_data["la_doi_pasi_stores"]
carrefour_stores = store_data["carrefour_stores"]

# Create a map centered around Bucharest
map_bucharest = folium.Map(location=[44.4268, 26.1025], zoom_start=12)

# Paths to custom store icons
lidl_icon_path = os.path.join('Shop/Images', 'lidl.png')
mega_image_icon_path = os.path.join('Shop/Images', 'mega_image.png')
profi_icon_path = os.path.join('Shop/Images', 'profi.png')
la_doi_pasi_icon_path = os.path.join('Shop/Images', 'la_doi_pasi.png')
carrefour_stores_icon_path = os.path.join('Shop/Images', 'carrefour.png')

# Plot Lidl stores on the map
for store in lidl_stores:
    coordinates = geocode_address(store["address"], api_key)
    if coordinates:  # If geocoding was successful
        lat, lng = coordinates
        custom_icon = folium.CustomIcon(icon_image=lidl_icon_path, icon_size=(50, 35))
        folium.Marker(
            location=[lat, lng],
            popup=store["name"],
            icon=custom_icon
        ).add_to(map_bucharest)
    else:
        print(f"Could not geocode {store['name']} at {store['address']}")

# Plot Mega Image stores on the map
for store in mega_image_stores:
    # Make the address lowercase after the first letter
    address = store["address"].lower().capitalize()  # Capitalizes the first letter only
    
    coordinates = geocode_address(address, api_key)
    if coordinates:  # If geocoding was successful
        lat, lng = coordinates
        custom_icon = folium.CustomIcon(icon_image=mega_image_icon_path, icon_size=(25, 25))
        folium.Marker(
            location=[lat, lng],
            popup=f"{store['name']} - {store['program']}",
            icon=custom_icon
        ).add_to(map_bucharest)
    else:
        print(f"Could not geocode {store['name']} at {store['address']}")
        
# Plot Profi stores on the map
for store in profi_stores:
    coordinates = geocode_address(store["address"], api_key)
    if coordinates:  # If geocoding was successful
        lat, lng = coordinates
        custom_icon = folium.CustomIcon(icon_image=profi_icon_path, icon_size=(60, 20))
        folium.Marker(
            location=[lat, lng],
            popup=store["name"],
            icon=custom_icon
        ).add_to(map_bucharest)
    else:
        print(f"Could not geocode {store['name']} at {store['address']}")    

# Plot La Doi Pasi stores on the map
for store in la_doi_pasi_stores:
    coordinates = geocode_address(store["address"], api_key)
    if coordinates:  # If geocoding was successful
        lat, lng = coordinates
        custom_icon = folium.CustomIcon(icon_image=la_doi_pasi_icon_path, icon_size=(25, 25))
        folium.Marker(
            location=[lat, lng],
            popup=store["name"],
            icon=custom_icon
        ).add_to(map_bucharest)
    else:
        print(f"Could not geocode {store['name']} at {store['address']}")

# Plot Carrefour stores on the map
for store in carrefour_stores:
    coordinates = geocode_address(store["address"], api_key)
    if coordinates:  # If geocoding was successful
        lat, lng = coordinates
        custom_icon = folium.CustomIcon(icon_image=carrefour_stores_icon_path, icon_size=(30, 20))
        folium.Marker(
            location=[lat, lng],
            popup=store["name"],
            icon=custom_icon
        ).add_to(map_bucharest)
    else:
        print(f"Could not geocode {store['name']} at {store['address']}")

# Save the map to an HTML file
map_bucharest.save("Shop/stores_bucharest.html")

print("Map has been saved as 'stores_bucharest.html'. Open it in your browser to view the map.")
