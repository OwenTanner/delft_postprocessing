import pandas as pd
import matplotlib.pyplot as plt
from delft_postprocessing.helpers import (
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
        Otherwise plots the transect path on X-Y coordinates.
        
        Args:
            variable_name: Optional name of variable to plot against distance
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        
        if variable_name is not None and variable_name in self.df.columns:
            # Plot distance vs variable value
            ax.plot(self.df['distance'], self.df[variable_name], 'o-')
            ax.set_xlabel('Distance along transect (m)')
            ax.set_ylabel(variable_name)
            ax.set_title(f'Transect profile - {variable_name}')
            
            # Add point labels
            for i, (d, v) in enumerate(zip(self.df['distance'], self.df[variable_name])):
                if v is not None:  # Only label points with valid values
                    ax.text(d, v, f'  {i+1}', va='center')
        else:
            # Plot the transect path on X-Y coordinates
            ax.plot(self.df['easting'], self.df['northing'], 'o-')
            ax.set_xlabel('Easting')
            ax.set_ylabel('Northing')
            ax.set_title('Transect path')
            ax.set_aspect('equal')
            
            # Add point labels
            for i, (e, n) in enumerate(zip(self.df['easting'], self.df['northing'])):
                ax.text(e, n, f'  {i+1}', va='center')
        
        plt.grid(True)
        plt.tight_layout()
        return fig, ax
    
    def get_dataframe(self):
        """Return the pandas DataFrame containing all transect data"""
        return self.df

