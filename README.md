# whitespot-shop

A Python-based solution for analyzing geospatial data, visualizing maps, and performing advanced geographic computations. This project leverages a variety of powerful libraries to enable integration, data manipulation, and visualization of geographic information.

## Features
- **Geospatial Analysis:** Perform operations on geographic data using GeoPandas.
- **Interactive Maps:** Visualize data with Folium and OpenStreetMap (OSM).
- **Map Styling:** Use Contextily for beautiful basemap integration.
- **Route and Navigation Analysis:** Calculate optimal routes and analyze geospatial paths.
- **Custom Map Creation:** Generate customized visualizations using Matplotlib and OpenCV.
- **Google Maps API Integration:** Leverage Google Maps for advanced geolocation and mapping tasks.
- **Advanced Projections:** Utilize PyProj for coordinate transformations.
- **Scientific Computations:** Perform sophisticated numerical computations using SciPy.

## Dependencies
To run this project, install the following Python libraries:

## Getting Started

### Prerequisites

Ensure you have Python 3.8 or later installed.

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd <repository-folder>
```
2. Install dependencies:
   
```bash
pip install geopandas matplotlib contextily folium osmnx opencv-python googlemaps pyproj scipy
```

## Example Usage
Here's an example of what this project can do:

```
import geopandas as gpd
import folium
import contextily as ctx

# Example: Load geospatial data
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

# Example: Plot a map with contextily basemap
ax = world.plot(figsize=(10, 10), alpha=0.5, edgecolor='k')
ctx.add_basemap(ax, source=ctx.providers.Stamen.Terrain)
```

## Key Functionality

- Load and manipulate geospatial data.
- Generate interactive maps.
- Perform route analysis and geospatial computations.
- Train and use ML models of Random Forest to analyze patterns and make predictions.

## Documentation with relevant links on how we gathered all the necessary data:

1) List of all Mega Image shops in Bucharest: https://www.profi.ro/magazine/
2) Dispozable income mapping: https://geojson.io/#map=2/0/20
3) Population Density: https://www.kontur.io/portfolio/population-dataset/
4) Traffic data for Bucharest: https://osmnx.readthedocs.io/en/stable/
5) Data from press about Mega Image: https://www.zf.ro/zf-24/mega-image-a-ajuns-cu-210-magazine-cel-mai-mare-chirias-de-la-parterul-blocurilor-din-bucuresti-11671359

## Link to our ppt presentation:

https://www.canva.com/design/DAGYpABcv8g/AaQQ_XV4Jm0Hy1w85WkV1g/edit?utm_content=DAGYpABcv8g&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
