import pandas as pd
import matplotlib.pyplot as plt
from helpers import (
    calculate_path_distances, 
    find_element_from_coordinates, 
    get_value_for_element
)

class RiverTransect:
    """
    Class to manage data along a river transect.
    Stores points and their associated data in a pandas DataFrame.
    """
    def __init__(self, eastings, northings, geom_file_path, 
                 stat_file_path):
        """
        Initialize the transect with a series of points.
        
        Args:
            eastings: List of X coordinates
            northings: List of Y coordinates
            geom_file_path: Path to the geometry netCDF file
            stat_file_path: Path to the statistics netCDF file
        """
        # Validate inputs
        if len(eastings) != len(northings):
            raise ValueError("Eastings and northings lists must have the same length")
        
        # Store file paths
        self.geom_file_path = geom_file_path
        self.stat_file_path = stat_file_path
        
        # Create initial DataFrame with coordinates
        self.df = pd.DataFrame({
            'easting': eastings,
            'northing': northings
        })
        
        # Calculate distances and element IDs
        self.get_distances()
        self.get_element_ids()
        
        # Reorder columns to put element_id as the third column
        if 'element_id' in self.df.columns and 'distance' in self.df.columns:
            self.df = self.df[['easting', 'northing', 'element_id', 'distance']]
    
    def get_element_ids(self):
        """
        Populate the dataframe with element IDs for each point.
        """
        element_ids = []
        for i, row in self.df.iterrows():
            element_id = find_element_from_coordinates(row['easting'], row['northing'], self.geom_file_path)
            element_ids.append(element_id)
        
        # Add to DataFrame
        self.df['element_id'] = element_ids
        return element_ids
    
    def get_distances(self):
        """
        Populate the dataframe with cumulative distances along the transect.
        """
        if len(self.df) > 0:
            distances = calculate_path_distances(self.df['easting'].tolist(), self.df['northing'].tolist())
            self.df['distance'] = distances
            return distances
        return []
        
    def load_variable(self, variable_name):
        """
        Load values for a variable at each point in the transect.
        
        Args:
            variable_name: Name of the variable to load
        
        Returns:
            True if successful, False otherwise
        """
        values = []
        for element_id in self.df['element_id']:
            if element_id is not None:
                value = get_value_for_element(element_id, variable_name, self.stat_file_path)
                values.append(value)
            else:
                values.append(None)
        
        # Add to DataFrame
        self.df[variable_name] = values
        
        # Check if we got any valid values
        return any(v is not None for v in values)
    
    def plot_transect(self, variable_name=None):
        """
        Plot the transect data.
        If variable_name is specified, plots distance vs variable value.
        If variable_name is None, returns empty figure and axis without plotting.
        
        Args:
            variable_name: Optional name of variable to plot against distance
            
        Returns:
            tuple: (fig, ax) matplotlib figure and axis objects
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # If no variable specified, return empty plot
        if variable_name is None:
            return fig, ax
            
        # Check if the variable exists in the dataframe
        if variable_name in self.df.columns:
            # Plot distance vs variable value
            ax.plot(self.df['distance'], self.df[variable_name], 'o-')
            ax.set_xlabel('Distance along transect (m)')
            ax.set_ylabel(variable_name)
            ax.set_title(f'Transect profile - {variable_name}')
            
            # Add point labels
            for i, (d, v) in enumerate(zip(self.df['distance'], self.df[variable_name])):
                if v is not None:  # Only label points with valid values
                    ax.text(d, v, f'  {i+1}', va='center')
                    
            plt.grid(True)
            plt.tight_layout()
        else:
            # Variable doesn't exist in the dataframe
            print(f"Warning: Variable '{variable_name}' not found in transect data")
            
        return fig, ax
    
    def list_available_variables(self):
        """
        List all variable names available in the statistics file.
        
        Returns:
            list: Names of all variables in the statistics file
        """
        import netCDF4
        
        try:
            with netCDF4.Dataset(self.stat_file_path) as nc:
                # Get all variable names
                variables = list(nc.variables.keys())
                
                # Optional: print them for convenience
                print(f"Found {len(variables)} variables in {self.stat_file_path}")
                for var in variables:
                    print(f"  - {var}")
                    
                return variables
        except Exception as e:
            print(f"Error reading variables: {e}")
            return []
    
    def get_dataframe(self):
        """Return the pandas DataFrame containing all transect data"""
        return self.df
    
    def get_din(self):
        """
        Calculate mean DIN values by summing Mesh2D_2d_MEAN_FullRun_cTR2 and Mesh2D_2d_MEAN_FullRun_cTR4.
        
        Returns:
            bool: True if calculation successful, False otherwise
        """
        # Load required variables if they aren't already loaded
        variables = ['Mesh2D_2d_MEAN_FullRun_cTR2', 'Mesh2D_2d_MEAN_FullRun_cTR4']
        for var in variables:
            if var not in self.df.columns:
                self.load_variable(var)
        
        # Check if all required variables were successfully loaded
        if not all(var in self.df.columns for var in variables):
            print("Warning: Could not calculate mean DIN - required variables not available")
            return False
        
        # Calculate mean DIN and add to dataframe
        self.df['mean_din'] = self.df['Mesh2D_2d_MEAN_FullRun_cTR2'] + self.df['Mesh2D_2d_MEAN_FullRun_cTR4']
        
        return True
    
    def wfd_performance(self):
        
        self.df['WFD High'] = 0.282
        self.df['WFD Good'] = 3.807
        self.df['WFD Moderate'] = 5.7105
        self.df['WFD Poor'] = 8.56575
        
        return True

    def get_din_std_dev(self):
        """
        Calculate DIN standard deviation using the formula:
        sqrt(σ²_cTR2 + σ²_cTR4 + 2*σ_cTR2*σ_cTR4)
        Given they are strongly correlated.
        Returns:
            bool: True if calculation successful, False otherwise
        """
        # Load required variables if they aren't already loaded
        variables = ['Mesh2D_2d_STDEV_FullRun_cTR2', 'Mesh2D_2d_STDEV_FullRun_cTR4']
        for var in variables:
            if var not in self.df.columns:
                self.load_variable(var)
        
        # Check if all required variables were successfully loaded
        if not all(var in self.df.columns for var in variables):
            print("Warning: Could not calculate DIN standard deviation - required variables not available")
            return False
        
        # Get shorthands for easier formula expression
        stdev_tr2 = self.df['Mesh2D_2d_STDEV_FullRun_cTR2']
        stdev_tr4 = self.df['Mesh2D_2d_STDEV_FullRun_cTR4']
        
        import numpy as np
        
        # Handle the calculation with proper masked array support
        # First convert pandas series to numpy arrays
        tr2_array = np.array(stdev_tr2)
        tr4_array = np.array(stdev_tr4)
        
        # Replace None with np.nan
        tr2_array = np.where(pd.isna(tr2_array), np.nan, tr2_array)
        tr4_array = np.where(pd.isna(tr4_array), np.nan, tr4_array)
        
        # Calculate the result
        result = tr2_array+tr4_array
        
        # Add to DataFrame
        self.df['din_std_dev'] = result
        
        return True
    
    def calculate_din_percentile(self, percentile):
        """
        Calculate the specified percentile of DIN using log-normal distribution.
        
        Args:
            percentile: The percentile to calculate (e.g., 90 for 90th percentile)
            
        Returns:
            pandas.Series: The calculated percentile values for each point
        """
        import numpy as np
        from scipy import stats
        
        # Ensure we have mean_din and din_std_dev
        if 'mean_din' not in self.df.columns:
            success = self.get_din()
            if not success:
                return None
        
        if 'din_std_dev' not in self.df.columns:
            success = self.get_din_std_dev()
            if not success:
                return None
        
        # Get the mean and standard deviation
        mean_din = self.df['mean_din']
        std_dev_din = self.df['din_std_dev']
        
        # Convert percentile to proportion (e.g., 90 -> 0.9)
        p = percentile / 100.0
        
        # Calculate parameters of the log-normal distribution
        # For a log-normal distribution with mean m and variance s²:
        # The underlying normal distribution has parameters:
        # μ = ln(m²/√(m² + s²))
        # σ = √(ln(1 + s²/m²))
        
        # Create empty series for results
        result = pd.Series(index=self.df.index)
        
        for i in self.df.index:
            m = mean_din[i]
            s = std_dev_din[i]
            
            # Handle null values or zeros
            if pd.isna(m) or pd.isna(s) or m <= 0:
                result[i] = None
                continue
            
            # Calculate parameters of underlying normal distribution
            mu = np.log(m**2 / np.sqrt(m**2 + s**2))
            sigma = np.sqrt(np.log(1 + (s**2 / m**2)))
            
            # Calculate the percentile using the log-normal distribution
            percentile_value = np.exp(mu + sigma * stats.norm.ppf(p))
            result[i] = percentile_value
        
        # Add to DataFrame with a descriptive column name
        column_name = f'din_percentile_{percentile}'
        self.df[column_name] = result
        
        return result

