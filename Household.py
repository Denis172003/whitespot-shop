import cv2
import numpy as np
import matplotlib.pyplot as plt

# Step 1: Load the image
image_path = "HouseholdIncome.png"
image = cv2.imread(image_path)
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Step 2: Define color ranges for segmentation (BGR format)
# Adjust these based on the legend colors in the map
color_ranges = {
    "45k-50k EUR": ([0, 0, 200], [50, 50, 255]),  # Red
    "50k-55k EUR": ([0, 100, 200], [50, 150, 255]),  # Orange
    "55k-60k EUR": ([0, 200, 200], [50, 255, 255]),  # Yellow
    "60k-65k EUR": ([200, 200, 0], [255, 255, 50]),  # Light green
    "65k-70k EUR": ([0, 200, 0], [50, 255, 50]),  # Green
    "70k-80k EUR": ([200, 0, 0], [255, 50, 50]),  # Dark Blue
    "80k-100k EUR": ([50, 0, 0], [255, 50, 50]),  # Blue
}

# Step 3: Segment regions by color
segmented_regions = {}
for label, (lower, upper) in color_ranges.items():
    lower = np.array(lower, dtype="uint8")
    upper = np.array(upper, dtype="uint8")
    mask = cv2.inRange(image, lower, upper)
    segmented_regions[label] = mask

# Step 4: Plot the segmented regions
fig, axes = plt.subplots(1, len(segmented_regions), figsize=(20, 10))
for ax, (label, mask) in zip(axes, segmented_regions.items()):
    ax.set_title(label)
    ax.imshow(mask, cmap="gray")
plt.show()

# Step 5: Save masks (optional)
for label, mask in segmented_regions.items():
    cv2.imwrite(f"{label.replace(' ', '_')}_mask.png", mask)
