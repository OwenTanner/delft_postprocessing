import pandas as pd
import matplotlib.pyplot as plt
from river_transect import RiverTransect
import os

def plot_din_stats(ax, transect_df, df, title_text):
    """
    Plot just the DIN statistics on the given axis.
    
    Args:
        ax: Matplotlib axis to plot on
        transect_df: DataFrame from RiverTransect object
        df: Original CSV DataFrame (for point IDs)
        title_text: Text to use in plot title
    """
    # Plot DIN statistics
    ax.plot(transect_df['distance'], transect_df['din_percentile_10'], 'b--', label='10th Percentile')
    ax.plot(transect_df['distance'], transect_df['mean_din'], 'g-', label='Mean')
    ax.plot(transect_df['distance'], transect_df['din_percentile_90'], 'r--', label='90th Percentile')
    
    # Add labels and title
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('DIN concentration (mg N/l)')
    ax.set_title(f'DIN concentrations in {title_text}')
    ax.legend()
    ax.grid(True)
    
    # Add point markers with their original IDs from the CSV
    for i, row_id in enumerate(df['id']):
        if i < len(transect_df) and not pd.isna(transect_df['mean_din'].iloc[i]):
            ax.annotate(f"{row_id}", 
                      (transect_df['distance'].iloc[i], transect_df['mean_din'].iloc[i]),
                      xytext=(5, 5), textcoords='offset points')
    
    return ax

def plot_din_with_wfd(ax, transect_df, df, title_text):
    """
    Plot DIN statistics with WFD guidelines on the given axis.
    
    Args:
        ax: Matplotlib axis to plot on
        transect_df: DataFrame from RiverTransect object
        df: Original CSV DataFrame (for point IDs)
        title_text: Text to use in plot title
    """
    # Plot DIN statistics
    ax.plot(transect_df['distance'], transect_df['din_percentile_10'], 'b--', label='10th Percentile')
    ax.plot(transect_df['distance'], transect_df['mean_din'], 'g-', label='Mean')
    ax.plot(transect_df['distance'], transect_df['din_percentile_90'], 'r--', label='90th Percentile')
    
    # Add WFD guidelines
    ax.plot(transect_df['distance'], transect_df['WFD Good'], 'k:', label='WFD Good')
    ax.plot(transect_df['distance'], transect_df['WFD High'], 'k--', label='WFD High')
    ax.plot(transect_df['distance'], transect_df['WFD Moderate'], 'm-.', label='WFD Moderate')
    ax.plot(transect_df['distance'], transect_df['WFD Poor'], 'c:', label='WFD Poor')
    
    # Add labels and title
    ax.set_xlabel('Distance (m)')
    ax.set_ylabel('DIN concentration (mg N/l)')
    ax.set_title(f'DIN concentrations in {title_text} with WFD guidelines')
    ax.legend()
    ax.grid(True)
    ax.set_yscale('log')  # Set y-axis to log scale
    
    # Add point markers with their original IDs from the CSV
    for i, row_id in enumerate(df['id']):
        if i < len(transect_df) and not pd.isna(transect_df['mean_din'].iloc[i]):
            ax.annotate(f"{row_id}", 
                      (transect_df['distance'].iloc[i], transect_df['mean_din'].iloc[i]),
                      xytext=(5, 5), textcoords='offset points')
    
    return ax

def process_transect(csv_path, title_text, geom_file_path, stat_file_path):
    """
    Process a single transect CSV file and create plots.
    
    Args:
        csv_path: Path to the CSV file with transect coordinates
        title_text: Text to use in plot titles (e.g., "Cross Section 1")
        geom_file_path: Path to the geometry netCDF file
        stat_file_path: Path to the statistics netCDF file
        
    Returns:
        bool: True if successful, False otherwise
    """
    print(f"Processing {title_text}...")
    
    # Check if the file exists
    if not os.path.exists(csv_path):
        print(f"WARNING: File {csv_path} not found. Skipping.")
        return False
    
    # Read the CSV file
    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print(f"ERROR: Could not read {csv_path}: {e}")
        return False
    
    # Extract eastings and northings
    try:
        eastings = df["E"].tolist()
        northings = df["N"].tolist()
    except KeyError as e:
        print(f"ERROR: CSV file missing required columns: {e}")
        return False
    
    print(f"Read {len(eastings)} points from {csv_path}")
    
    # Create a transect with points from the CSV
    transect = RiverTransect(eastings, northings, geom_file_path=geom_file_path, stat_file_path=stat_file_path)
    
    # Calculate DIN mean and standard deviation
    transect.get_din()
    transect.get_din_std_dev()
    
    # Calculate 10th and 90th percentiles
    transect.calculate_din_percentile(10)
    transect.calculate_din_percentile(90)
    
    # Calculate WFD performance
    transect.wfd_performance()
    
    # Generate filename base from title_text
    if "cross section" in title_text:
        section_num = title_text.split()[-1]
        filename_base = f"din_cross_section_{section_num}"
    else:
        filename_base = "din_centreline"
    
    # ------------------------------------------------------------------------
    # PLOT 1: Just DIN statistics (without WFD guidelines)
    # ------------------------------------------------------------------------
    fig1, ax1 = plt.subplots(figsize=(12, 7))
    plot_din_stats(ax1, transect.df, df, title_text)
    plt.tight_layout()
    
    plot1_filename = f"Results/{filename_base}_stats.png"
    plt.savefig(plot1_filename, dpi=300)
    print(f"Plot saved to {plot1_filename}")
    
    # ------------------------------------------------------------------------
    # PLOT 2: DIN statistics with WFD guidelines
    # ------------------------------------------------------------------------
    fig2, ax2 = plt.subplots(figsize=(12, 7))
    plot_din_with_wfd(ax2, transect.df, df, title_text)
    plt.tight_layout()
    
    plot2_filename = f"Results/{filename_base}_with_wfd.png"
    plt.savefig(plot2_filename, dpi=300)
    print(f"Plot saved to {plot2_filename}")
    
    plt.close('all')
    return True

# Main execution
if __name__ == "__main__":
    # Set file paths for all transects
    geom_file_path = "../14DayHYD_NoWind_Nash_HD_waqgeom.nc"
    stat_file_path = "../deltashell-stat_map.nc"
    
    # Process centreline first
    centreline_path = "Usk_Transects/Centreline.csv"
    process_transect(centreline_path, "the centreline section of the Usk", geom_file_path, stat_file_path)
    
    # Process each cross section
    for i in range(1, 8):  # 1 through 6
        try:
            csv_path = f"Usk_Transects/Cross_Section_{i}.csv"
            process_transect(csv_path, f"horizontal cross section {i}", geom_file_path, stat_file_path)
        except Exception as e:
            print(f"Error processing cross section {i}: {e}")
    
    print("Success")

