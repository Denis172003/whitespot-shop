import folium
import json
import random

def generate_random_color():
    """Generate a random color for map styling."""
    return f'#{random.randint(0, 0xFFFFFF):06x}'

def visualize_geojson(geojson_path):
    """
    Visualize GeoJSON with different colors for each feature and display properties.
    
    Args:
        geojson_path (str): Path to the GeoJSON file
    
    Returns:
        folium.Map: Map with GeoJSON features visualized
    """
    # Read the GeoJSON file
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    # Create a map centered on the first feature's geometry
    if geojson_data['features']:
        first_feature = geojson_data['features'][0]
        
        # Extract the center as the first point of the first geometry
        coordinates = first_feature['geometry']['coordinates'][0][0]
        center = [coordinates[1], coordinates[0]]  # Convert to [latitude, longitude]
        m = folium.Map(location=center, zoom_start=12)
    else:
        # Fallback to a default location if no features
        m = folium.Map(location=[44.4268, 26.1025], zoom_start=10)
    
    # Add each feature to the map with a unique color and popup
    for feature in geojson_data['features']:
        color = generate_random_color()
        
        # Create a popup with feature properties
        popup_text = "<b>Properties:</b><br>"
        for key, value in feature['properties'].items():
            popup_text += f"{key}: {value}<br>"
        
        # Add the GeoJSON layer with style
        folium.GeoJson(
            feature,
            style_function=lambda x, color=color: {
                'fillColor': color,
                'color': color,
                'weight': 2,
                'fillOpacity': 0.7
            },
            popup=folium.Popup(popup_text, max_width=300)
        ).add_to(m)
    
    return m

def create_region_dictionary(geojson_path):
    """
    Create a dictionary containing details about each region from a GeoJSON file.

    Args:
        geojson_path (str): Path to the GeoJSON file.

    Returns:
        dict: Dictionary containing region details.
    """
    # Load the GeoJSON file
    with open(geojson_path, 'r') as f:
        geojson_data = json.load(f)
    
    region_dict = {}
    
    # Populate the dictionary with region details
    for feature in geojson_data["features"]:
        # Extract region properties
        properties = feature["properties"]
        region_name = list(properties.keys())[0]  # Assume the region name is the first key
        region_sector = properties[region_name]
        price_index = properties.get("price_index", None)  # Assume price_index is in 'properties'
        coordinates = feature["geometry"]["coordinates"]
        
        # Add to the dictionary
        region_dict[region_name] = {
            "sector": region_sector,
            "coordinates": coordinates,
            "price_index": price_index
        }
    
    return region_dict

# Example usage
def main():
    # Replace 'your_geojson_file.geojson' with the path to your GeoJSON file
    print("Visualizing GeoJSON file...")
    m = visualize_geojson('bucharest.geojson')
    
    # Save the map
    #print("Saving visualization to geojson_visualization.html...")
    #m.save('geojson_visualization.html')
    #print("Visualization saved to geojson_visualization.html")

    # Create the region dictionary
    region_details = create_region_dictionary("bucharest.geojson")
    
    # Print the resulting dictionary
    print(json.dumps(region_details, indent=4))



if __name__ == "__main__":
    main()
