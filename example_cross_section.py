import pandas as pd
import matplotlib.pyplot as plt
from river_transect import RiverTransect

# Read the CSV file
csv_path = "example_usk.csv"
df = pd.read_csv(csv_path)

# Extract eastings and northings
eastings = df["X (Easting)"].tolist()
northings = df["Y (Northing)"].tolist()

print(f"Read {len(eastings)} points from {csv_path}")

# Set file paths
geom_file_path = "../14DayHYD_NoWind_Nash_HD_waqgeom.nc"
stat_file_path = "../deltashell-stat_map.nc"

# Create a transect with points from the CSV
transect = RiverTransect(eastings, northings, geom_file_path=geom_file_path, stat_file_path=stat_file_path)

# Calculate DIN mean and standard deviation
transect.get_din()
transect.get_din_std_dev()

# Calculate 10th and 90th percentiles
transect.calculate_din_percentile(10)  # 10th percentile
transect.calculate_din_percentile(90)  # 90th percentile

# Calculate WFD performance
transect.wfd_performance()

# Create a single plot with all three percentiles
fig, ax = plt.subplots(figsize=(12, 7))

# Plot the three lines
ax.plot(transect.df['distance'], transect.df['din_percentile_10'], 'b--', label='10th Percentile')
ax.plot(transect.df['distance'], transect.df['mean_din'], 'g-', label='Mean')
ax.plot(transect.df['distance'], transect.df['din_percentile_90'], 'r--', label='90th Percentile')
ax.plot(transect.df['distance'], transect.df['WFD Good'], 'k:', label='WFD Good')
ax.plot(transect.df['distance'], transect.df['WFD High'], 'k--', label='WFD High')
ax.plot(transect.df['distance'], transect.df['WFD Moderate'], 'm-.', label='WFD Moderate')
ax.plot(transect.df['distance'], transect.df['WFD Poor'], 'c:', label='WFD Poor')

# Add labels and title
ax.set_xlabel('Distance along transect (m)')
ax.set_ylabel('DIN Concentration')
ax.set_title('DIN Concentrations Along River Transect')
ax.legend()
ax.grid(True)
ax.set_yscale('log')

# Add point markers
for i in range(len(transect.df)):
    if not pd.isna(transect.df['mean_din'].iloc[i]):
        ax.annotate(f"{i+1}", 
                   (transect.df['distance'].iloc[i], transect.df['mean_din'].iloc[i]),
                   xytext=(5, 5), textcoords='offset points')

plt.tight_layout()
plot_filename = "din_cross_section.png"
plt.savefig(plot_filename, dpi=300)
plt.show(block=False)
plt.pause(5)  # Show plot for 5 seconds
plt.close()

# Print summary statistics
print("\nSummary statistics for DIN:")
print(f"  10th percentile range: {transect.df['din_percentile_10'].min():.3f} - {transect.df['din_percentile_10'].max():.3f}")
print(f"  Mean range: {transect.df['mean_din'].min():.3f} - {transect.df['mean_din'].max():.3f}")
print(f"  90th percentile range: {transect.df['din_percentile_90'].min():.3f} - {transect.df['din_percentile_90'].max():.3f}")