import numpy as np
import json
import folium
from folium.plugins import HeatMap
from scipy.spatial import KDTree


# Constants
TURNOVER_MIN = 2.5  # in million lei
TURNOVER_MAX = 50  # Maximum turnover in million lei
SURFACE_MIN = 100  # Minimum store surface in sqm
SURFACE_MAX = 1200  # Maximum store surface in sqm
SURFACE_MEDIAN = 400  # Median store surface in sqm
SURFACE_WEIGHTS = {"traffic": 0.5, "density": 0.4, "income": 0.05, "competition": 0.05}  # Weights for surface factors
TURNOVER_WEIGHTS = {"density": 0.4, "income": 0.3, "traffic": 0.3}  # Weights for turnover factors


# Load JSON file utility
def load_json_file(filename):
    """Load JSON data from a file."""
    with open(filename, "r") as file:
        return json.load(file)


# Normalize value utility
def normalize(value, min_value, max_value):
    """Normalize a value to a range [0, 1]."""
    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0


# Calculate store surface based on weighted factors and median surface
def calculate_surface(density, income, traffic, competition, density_range, income_range, traffic_range):
    """
    Calculate store surface using weighted normalized values.
    """
    # Normalize all factors
    density_normalized = normalize(density, *density_range)
    income_normalized = normalize(income, *income_range)
    traffic_normalized = normalize(traffic, *traffic_range)
    competition_normalized = 1 - competition  # Competition lowers the score

    # Weighted surface calculation
    weighted_factor = (
        SURFACE_WEIGHTS["traffic"] * traffic_normalized +
        SURFACE_WEIGHTS["density"] * density_normalized +
        SURFACE_WEIGHTS["income"] * income_normalized +
        SURFACE_WEIGHTS["competition"] * competition_normalized
    )

    # Adjust surface using median as the base
    if weighted_factor >= 0.5:
        # Scale up from the median
        surface = SURFACE_MEDIAN + (SURFACE_MAX - SURFACE_MEDIAN) * (weighted_factor - 0.5) * 2
    else:
        # Scale down from the median
        surface = SURFACE_MEDIAN - (SURFACE_MEDIAN - SURFACE_MIN) * (0.5 - weighted_factor) * 2

    return surface


# Turnover and store surface calculation
def calculate_turnover_and_surface(
    density, income, traffic, competition,
    density_range, income_range, traffic_range
):
    """
    Calculate turnover and store surface based on input factors.
    """
    # Normalize turnover factors
    density_normalized = normalize(density, *density_range)
    income_normalized = normalize(income, *income_range)
    traffic_normalized = normalize(traffic, *traffic_range)

    # Calculate weighted adjusted turnover
    adjusted_factor = (
        TURNOVER_WEIGHTS["density"] * density_normalized +
        TURNOVER_WEIGHTS["income"] * income_normalized +
        TURNOVER_WEIGHTS["traffic"] * traffic_normalized
    )

    # Calculate competition penalty
    competition_penalty = min(competition, 1)

    # Base turnover adjusted by competition
    base_turnover = TURNOVER_MIN + (TURNOVER_MAX - TURNOVER_MIN) * adjusted_factor
    base_turnover *= (1 - competition_penalty)

    # Calculate surface proportionality impact
    store_surface = calculate_surface(density, income, traffic, competition, density_range, income_range, traffic_range)
    scaling_factor = 0.25
    estimated_turnover = base_turnover * (1 + scaling_factor * (store_surface - SURFACE_MEDIAN) / SURFACE_MEDIAN)

    return estimated_turnover * 1e6, store_surface

disposable_income = load_json_file("datasets/dispozable_income.json")
population_density = load_json_file("datasets/population_density.json")
traffic_data = load_json_file("datasets/traffic_info.json")
stores_data = load_json_file("datasets/stores_with_coords.json")

def find_min_price_index():
    """Find the minimum price index from JSON."""
    price_indices = [
        feature["properties"]["price_index"]
        for feature in disposable_income["features"]
        if "price_index" in feature["properties"]
    ]
    return min(price_indices) if price_indices else None


def find_max_price_index():
    """Find the maximum price index from JSON."""
    price_indices = [
        feature["properties"]["price_index"]
        for feature in disposable_income["features"]
        if "price_index" in feature["properties"]
    ]
    return max(price_indices) if price_indices else None


def find_min_density():
    """Find the minimum population density value."""
    density_values = [
        data["density"] for key, data in population_density.items() if "density" in data
    ]
    return min(density_values) if density_values else None


def find_max_density():
    """Find the maximum population density value."""
    density_values = [
        data["density"] for key, data in population_density.items() if "density" in data
    ]
    return max(density_values) if density_values else None


def find_min_congestion():
    """Find minimum congestion values."""
    congestion_values = [
        data["congestion"] for key, data in traffic_data.items() if "congestion" in data
    ]
    return min(congestion_values) if congestion_values else None


def find_max_congestion():
    """Find maximum congestion values."""
    congestion_values = [
        data["congestion"] for key, data in traffic_data.items() if "congestion" in data
    ]
    return max(congestion_values) if congestion_values else None


# Find data ranges for normalization (using existing logic as it is)
density_range = (find_min_density(), find_max_density())  # (0.6492700054844956, 8453.737886022765)
income_range = (find_min_price_index(), find_max_price_index())  # (900, 2500)
traffic_range = (find_min_congestion(), find_max_congestion())  # (4.7357599444741716e-05, 0.9999050808206642)

# Precompute KDTree for density and income data for fast spatial querying
density_coords = np.array([
    [data["coordinates"][0], data["coordinates"][1]]
    for data in population_density.values()
])
density_values = np.array([data["density"] for data in population_density.values()])
density_tree = KDTree(density_coords)

income_coords = []
for feature in disposable_income["features"]:
    # Access geometry's coordinates safely
    if "geometry" in feature and "coordinates" in feature["geometry"]:
        # Flatten the coordinates if it's multi-dimensional
        for coords in feature["geometry"]["coordinates"][0]:  # Adjust indexing if necessary
            lon, lat = coords  # Unpack the coordinates
            income_coords.append([lon, lat])

income_coords = np.array(income_coords)

income_coords = []
income_values = []

for feature in disposable_income["features"]:
    # Check if the necessary keys exist in each feature
    if "geometry" in feature and "coordinates" in feature["geometry"]:
        # Loop over all coordinates for this feature's price index
        for coord in feature["geometry"]["coordinates"][0]:
            lon, lat = coord  # Unpack coordinates
            income_coords.append([lon, lat])
            # Repeat the price_index value for every coordinate
            if "properties" in feature and "price_index" in feature["properties"]:
                income_values.append(feature["properties"]["price_index"])

# Convert lists to numpy arrays
income_coords = np.array(income_coords)
income_values = np.array(income_values)

# Build KDTree
income_tree = KDTree(income_coords)

store_coords = np.array([
    [store["longitude"], store["latitude"]]
    for store_group in stores_data.values()  # Loop over all store chains in the JSON
    for store in store_group
])
store_tree = KDTree(store_coords)

radius = 0.001

# Compute density for all points
def calculate_competition_score(lon, lat):
    # Query all points within the given radius
    points_in_radius = store_tree.query_ball_point([lon, lat], radius)
    # Number of stores found in this neighborhood
    num_stores_in_radius = len(points_in_radius)

    # Normalize this by comparing it to the median number of points
    median_density = np.median([
        len(store_tree.query_ball_point(point, radius)) 
        for point in store_coords
    ])

    # Avoid division by zero
    if median_density == 0:
        return 1.0  # If median density is zero, the location is effectively isolated
    
    # Compute the competition score
    score = 1 - (num_stores_in_radius / median_density)

    # Clip values to ensure the score is between 0 and 1
    score = max(0, min(1, score))
    return score

def normalize_turnover_data(turnover_data):
    """
    Normalize the turnover values in the turnover_data array to a range of [0, 1].

    Parameters:
        turnover_data (list of lists): Each inner list contains [latitude, longitude, turnover].

    Returns:
        list of lists: The same structure as input, but with normalized turnover values.
    """
    # Extract turnover values
    turnovers = np.array([point[2] for point in turnover_data])
    min_turnover, max_turnover = turnovers.min(), turnovers.max()

    # Normalize turnover values
    normalized_data = []
    for point in turnover_data:
        normalized_turnover = (point[2] - min_turnover) / (max_turnover - min_turnover)
        normalized_data.append([point[0], point[1], normalized_turnover])

    return normalized_data

# Map with heatmap visualization
def generate_heatmap():
    traffic_data = load_json_file("datasets/traffic_info.json")
    turnover_data = []
    surfaces = []
    
    # Spatial KDTree lookups
    density_tree = KDTree(density_coords)
    income_tree = KDTree(income_coords)
    store_tree = KDTree(store_coords)

    # Loop over keys directly since `features` doesn't exist
    for key, feature in traffic_data.items():
        coordinates = feature["coordinates"]
        congestion = feature["congestion"]

        # Loop through the coordinates array to handle multiple points for heatmap data
        for coord in coordinates:
            # Lookup spatial matches using nearest neighbors
            lat, lon = coord[1], coord[0]  # Ensure correct lat/lon order
            
            # Find the closest population density value
            nearest_density_idx = density_tree.query([lon, lat])[1]
            population_density_value = density_values[nearest_density_idx]
            
            # Find the closest income value
            nearest_income_idx = income_tree.query([lon, lat])[1]
            income_value = income_values[nearest_income_idx]
            competition_score = calculate_competition_score(lon, lat)

            # Calculate turnover for this data point
            turnover, surface = calculate_turnover_and_surface(
                population_density_value,
                income_value,
                congestion,
                competition_score,
                density_range, income_range, traffic_range
            )

            turnover_data.append([lat, lon, turnover])
            surfaces.append(surface)

    # Create the map with the calculated heatmap
    m = folium.Map(location=[44.5, 26.0], zoom_start=12)
    HeatMap(
    normalize_turnover_data(turnover_data),
    name="Turnover Heatmap",
    radius=15,  # Increased for stronger visual impact
    gradient={
        0.0: "#000000",  # Black
        0.1: "#00008b",  # Dark Blue
        0.2: "#0000ff",  # Bright Blue
        0.3: "#1e90ff",  # Dodger Blue
        0.4: "#00ff00",  # Bright Green
        0.5: "#ffff00",  # Pure Yellow
        0.6: "#ff4500",  # Orange Red
        0.7: "#ff0000",  # Pure Red
        0.8: "#8b0000",  # Dark Red
        0.9: "#551a8b",  # Deep Purple
        1.0: "#ffffff"   # White for the most intense points
    }
    ).add_to(m)
    points_layer = folium.FeatureGroup(name="Turnover Points")
    i = 0
    for point in turnover_data:
        lat, lon, turnover = point

        if turnover / 1000000 == 0:
            i += 1
            continue

        # Add a CircleMarker with a tooltip
        folium.CircleMarker(
            location=(lat, lon),
            radius=3,
            color='blue',
            fill=True,
            fill_color='blue',
            fill_opacity=0.6,
            tooltip=f"Turnover: {turnover / 1000000:,.2f} Lei<br>Surface: {surfaces[i]:.2f} sqm"
        ).add_to(points_layer)
        i += 1

    points_layer.add_to(m)
    folium.LayerControl().add_to(m)

    m.save("turnover_heatmap.html")


generate_heatmap()
