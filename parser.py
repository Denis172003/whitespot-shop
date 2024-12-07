import geopandas as gpd
from shapely.geometry import box
import json

def create_density_dictionary(geojson_path, bounding_box=None):
    """
    Create a dictionary mapping regions to population density, including coordinates.

    Args:
        geojson_path (str): Path to the GeoJSON or shapefile containing population and geometry data.
        bounding_box (tuple, optional): (minx, miny, maxx, maxy) for clipping the data.

    Returns:
        dict: A dictionary where keys are region names/IDs and values are population density, coordinates.
    """
    # Load the GeoDataFrame
    gdf = gpd.read_file(geojson_path)
    
    # Keep only population and geometry columns
    gdf = gdf[["population", "geometry"]]
    
    # Convert to EPSG:4326 (WGS84)
    gdf = gdf.to_crs("EPSG:4326")
    
    # Clip to bounding box if provided
    if bounding_box:
        minx, miny, maxx, maxy = bounding_box
        bbox = box(minx, miny, maxx, maxy)
        gdf = gdf[gdf.intersects(bbox)]
    
    # Calculate area in square kilometers
    gdf["area_km2"] = gdf.geometry.to_crs("EPSG:3395").area / 1e6
    
    # Calculate density (population per square kilometer)
    gdf["density"] = gdf["population"] / gdf["area_km2"]
    
    # Create a dictionary with region ID (or another identifier) as key and density, coordinates as value
    density_dict = {}
    for idx, row in gdf.iterrows():
        region_name = row.name  # Use index as region identifier (can be replaced with a specific column if available)
        
        # Extract coordinates from the geometry
        coordinates = list(row["geometry"].representative_point().coords) if row["geometry"].is_valid else None
        
        density_dict[region_name] = {
            "density": row["density"],
            "coordinates": coordinates[0] if coordinates else None
        }
    
    return density_dict

# Example Usage
def main():
    geojson_path = "RomaniaPopulation"  # Path to your dataset
    bounding_box = (25.94, 44.36, 26.28, 44.54)  # Example bounding box for Bucharest
    
    # Generate the density dictionary
    density_dict = create_density_dictionary(geojson_path, bounding_box)
    
    # Save the dictionary to a JSON file
    json_file_path = "population_density.json"
    with open(json_file_path, 'w') as json_file:
        json.dump(density_dict, json_file, indent=4)
    
    print(f"Density data saved to {json_file_path}")

    # Print the density dictionary (optional)
    print("Density Dictionary with Coordinates:")
    for region_id, details in density_dict.items():
        print(f"Region {region_id}:")
        print(f"  Density: {details['density']:.2f} people/km²")
        print(f"  Coordinates: {details['coordinates']}")
        print("-" * 40)

if __name__ == "__main__":
    main()
