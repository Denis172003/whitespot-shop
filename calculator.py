import numpy as np

# Constants
TURNOVER_MIN = 2.5  # in million lei
TURNOVER_MAX = 50  # Maximum turnover in million lei
SURFACE_MIN = 100  # Minimum store surface in sqm
SURFACE_MAX = 1200  # Maximum store surface in sqm
SURFACE_MEDIAN = 400  # Median store surface in sqm
SURFACE_WEIGHTS = {"traffic": 0.5, "density": 0.4, "income": 0.05, "competition": 0.05}  # Weights for surface factors
TURNOVER_WEIGHTS = {"density": 0.4, "income": 0.3, "traffic": 0.3}  # Weights for turnover factors

def normalize(value, min_value, max_value):
    """Normalize a value to a range [0, 1]."""
    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0

def calculate_surface(density, income, traffic, competition, density_range, income_range, traffic_range):
    """
    Calculate store surface based on weighted factors and median surface.
    """
    # Normalize all factors
    density_normalized = normalize(density, *density_range)
    income_normalized = normalize(income, *income_range)
    traffic_normalized = normalize(traffic, *traffic_range)
    competition_normalized = 1 - competition  # Competition lowers the score

    # Weighted factor for surface
    weighted_factor = (
        SURFACE_WEIGHTS["traffic"] * traffic_normalized +
        SURFACE_WEIGHTS["density"] * density_normalized +
        SURFACE_WEIGHTS["income"] * income_normalized +
        SURFACE_WEIGHTS["competition"] * competition_normalized
    )

    # Adjust surface using the median as the base
    if weighted_factor >= 0.5:
        # If weighted factor is above the mid-point, scale up from the median
        surface = SURFACE_MEDIAN + (SURFACE_MAX - SURFACE_MEDIAN) * (weighted_factor - 0.5) * 2
    else:
        # If weighted factor is below the mid-point, scale down from the median
        surface = SURFACE_MEDIAN - (SURFACE_MEDIAN - SURFACE_MIN) * (0.5 - weighted_factor) * 2

    return surface


def calculate_turnover_and_surface(
    density, income, traffic, competition,
    density_range, income_range, traffic_range
):
    """
    Calculate turnover and store surface based on input factors.
    
    Args:
        density: Population density in the target area.
        income: Disposable income in the target area.
        traffic: Traffic index for the target area.
        competition: Number of competing stores in the area.
        density_range: Tuple of (min_density, max_density).
        income_range: Tuple of (min_income, max_income).
        traffic_range: Tuple of (min_traffic, max_traffic).
    
    Returns:
        Tuple of (estimated turnover in lei, store surface in sqm).
    """
    # Normalize factors for turnover
    density_normalized = normalize(density, *density_range)
    income_normalized = normalize(income, *income_range)
    traffic_normalized = normalize(traffic, *traffic_range)

    # Weighted factor for turnover
    adjusted_factor = (
        TURNOVER_WEIGHTS["density"] * density_normalized +
        TURNOVER_WEIGHTS["income"] * income_normalized +
        TURNOVER_WEIGHTS["traffic"] * traffic_normalized
    )

    # Competition penalty for turnover
    competition_penalty = min(competition, 1)

    # Calculate store surface
    store_surface = calculate_surface(density, income, traffic, competition, density_range, income_range, traffic_range)

    # Calculate base turnover
    base_turnover = TURNOVER_MIN + (TURNOVER_MAX - TURNOVER_MIN) * adjusted_factor
    base_turnover *= (1 - competition_penalty)  # Reduce by competition effect

    # Scale turnover proportionally to surface
    # Use a scaling factor to limit surface influence
    scaling_factor = 0.25  # Reduced scaling factor to moderate surface impact
    estimated_turnover = base_turnover * (1 + scaling_factor * (store_surface - SURFACE_MEDIAN) / SURFACE_MEDIAN)

    return estimated_turnover * 1e6, store_surface

# Example Input Data
density = 7000  # Population density per sq km
income = 2000  # Average disposable income in lei
traffic = 125  # Traffic index
competition = 0.4  # 20% competition factor (normalized to [0, 1])

# Ranges for normalization
density_range = (1000, 10000)  # Min and max density in dataset
income_range = (2000, 5000)  # Min and max disposable income
traffic_range = (100, 300)  # Min and max traffic index

# Calculate turnover and surface
turnover, surface = calculate_turnover_and_surface(
    density, income, traffic, competition,
    density_range, income_range, traffic_range
)

print(f"Estimated Turnover: {turnover / 1e6:.2f} million lei")
print(f"Store Surface: {surface:.2f} sqm")
