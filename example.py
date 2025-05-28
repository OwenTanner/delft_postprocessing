import pandas as pd
import matplotlib.pyplot as plt
from river_transect import RiverTransect

# Read the CSV file
csv_path = "example_usk.csv"  # Adjust path if needed
df = pd.read_csv(csv_path)

# Extract eastings and northings
eastings = df["X (Easting)"].tolist()
northings = df["Y (Northing)"].tolist()

print(f"Read {len(eastings)} points from {csv_path}")

geom_file_path = "14DayHYD_NoWind_Nash_HD_waqgeom.nc"
stat_file_path = "deltashell-stat_map.nc"

# Create a transect with points from the CSV and explicit file paths
transect = RiverTransect(eastings, northings, geom_file_path=geom_file_path, stat_file_path=stat_file_path)
variables = transect.list_available_variables()
# Load a variable
variable_name = "Mesh2D_2d_MAX_FullRun_cTR1" 
success = transect.load_variable(variable_name)

if success:
    print(f"Successfully loaded {variable_name}")
else:
    print(f"Warning: Could not load {variable_name} for any points")

# Display first few rows of the dataframe with the loaded data
print("\nTransect data:")
print(transect.get_dataframe().head())

# Show distance information
print("\nDistance information:")
distances = transect.get_dataframe()['distance'].tolist()
print(f"Total transect length: {distances[-1]:.2f} meters")
print(f"Distance between points: {[round(distances[i+1]-distances[i], 2) for i in range(len(distances)-1)]}")



# Plot the variable along the transect
plt.figure(1)
transect.plot_transect(variable_name)
plt.title(f"{variable_name} Along Transect")

plt.show()