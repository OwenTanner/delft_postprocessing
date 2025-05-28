import pandas as pd
import matplotlib.pyplot as plt
from river_transect import RiverTransect

# Read the Centreline CSV file
csv_path = "Centreline.csv"
df = pd.read_csv(csv_path)

# Extract eastings and northings from E and N columns
eastings = df["E"].tolist()
northings = df["N"].tolist()

print(f"Read {len(eastings)} points from {csv_path}")

# Set file paths
geom_file_path = "14DayHYD_NoWind_Nash_HD_waqgeom.nc"
stat_file_path = "deltashell-stat_map.nc"

# Create a transect with points from the CSV
transect = RiverTransect(eastings, northings, geom_file_path=geom_file_path, stat_file_path=stat_file_path)

# Calculate DIN mean and standard deviation
transect.get_din()
transect.get_din_std_dev()

# Calculate 10th and 90th percentiles
transect.calculate_din_percentile(10)  # 10th percentile
transect.calculate_din_percentile(90)  # 90th percentile

# Create a single plot with all three percentiles
fig, ax = plt.subplots(figsize=(12, 7))

# Plot the three lines
ax.plot(transect.df['distance'], transect.df['din_percentile_10'], 'b--', label='10th Percentile')
ax.plot(transect.df['distance'], transect.df['mean_din'], 'g-', label='Mean')
ax.plot(transect.df['distance'], transect.df['din_percentile_90'], 'r--', label='90th Percentile')

# Add labels and title
ax.set_xlabel('River distance (m)')
ax.set_ylabel('DIN Concentration')
ax.set_title('DIN Concentrations Along River Centreline')
ax.legend()
ax.grid(True)

# Add point markers with their original IDs from the CSV
for i, row_id in enumerate(df['id']):
    if i < len(transect.df) and not pd.isna(transect.df['mean_din'].iloc[i]):
        ax.annotate(f"{row_id}", 
                   (transect.df['distance'].iloc[i], transect.df['mean_din'].iloc[i]),
                   xytext=(5, 5), textcoords='offset points')

plt.tight_layout()
plt.show()

# Print summary statistics
print("\nSummary statistics for DIN:")
try:
    print(f"  10th percentile range: {transect.df['din_percentile_10'].min():.3f} - {transect.df['din_percentile_10'].max():.3f}")
    print(f"  Mean range: {transect.df['mean_din'].min():.3f} - {transect.df['mean_din'].max():.3f}")
    print(f"  90th percentile range: {transect.df['din_percentile_90'].min():.3f} - {transect.df['din_percentile_90'].max():.3f}")
except:
    print("  Could not calculate summary statistics - check if values were found in the model")