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

