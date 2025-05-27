import netCDF4
import numpy as np
from shapely.geometry import Point, Polygon

#TODO: A function which calculates 90th, 10th percentile for a given element ID.
# Function which takes in a ordered list of eastings and northings, and produces the x axis (ie distance across the river)
# A function which takes in an ordered list of eastings and northings, and a variable (e.g. mean/90th percentile) and produces the graph. 
#Hi Will

def calculate_distance(easting1, northing1, easting2, northing2):
    """
    Calculate the Euclidean distance between two points given by their eastings and northings.
    
    Args:
        easting1: X coordinate of first point
        northing1: Y coordinate of first point
        easting2: X coordinate of second point
        northing2: Y coordinate of second point
        
    Returns:
        float: Distance between the two points in the same units as the input coordinates
    """
    return np.sqrt((easting2 - easting1)**2 + (northing2 - northing1)**2)

def find_element_from_coordinates(easting, northing, geom_file_path="14DayHYD_NoWind_Nash_HD_waqgeom.nc"):
    """
    Find the mesh element ID containing the given coordinates.
    
    Args:
        easting: X coordinate (easting)
        northing: Y coordinate (northing)
        geom_file_path: Path to the geometry netCDF file
        
    Returns:
        int: Element ID if found, None if not found
    """
    # Open the geometry file
    nc = netCDF4.Dataset(geom_file_path)
    
    # Get node coordinates
    x = nc.variables["NetNode_x"][:]
    y = nc.variables["NetNode_y"][:]
    
    # Get element-to-node connectivity
    # NetElemNode is usually shape (nElem, nNodesPerElem), 1-based with -1 as fill value
    elem_node = nc.variables["NetElemNode"][:] - 1  # Convert to 0-based
    
    # Remove padding/fill values (-1) per element
    elem_node = np.ma.filled(elem_node, -1)
    
    # Convert coordinates to a shapely Point
    point = Point(easting, northing)
    found_elem = None
    
    # Search through elements
    for elem_idx, node_ids in enumerate(elem_node):
        valid_ids = node_ids[node_ids >= 0]  # Remove invalid node indices (padding)
        poly_coords = list(zip(x[valid_ids], y[valid_ids]))
        if len(poly_coords) < 3:
            continue  # Not a valid polygon
        polygon = Polygon(poly_coords)
        if polygon.contains(point):
            found_elem = elem_idx
            break
    
    nc.close()
    return found_elem

def get_value_for_element(element_id, variable_name, stat_file_path="deltashell-stat_map.nc"):
    """
    Get the value of a specified variable for a given element ID.
    
    Args:
        element_id: The element ID to look up
        variable_name: Name of the variable to extract (e.g., 'Mesh2D_2d_MAX_FullRun_cTR1')
        stat_file_path: Path to the statistics netCDF file
        
    Returns:
        The value of the variable at the specified element, or None if not found
    """
    # Open the statistics file
    stat_nc = netCDF4.Dataset(stat_file_path)
    
    # Check if the variable exists
    if variable_name not in stat_nc.variables:
        print(f"Variable {variable_name} not found in {stat_file_path}")
        stat_nc.close()
        return None
    
    # Get the data for the specified element
    # Assuming first dimension is time and second is element
    try:
        data = stat_nc.variables[variable_name][0, element_id]
        stat_nc.close()
        return data
    except Exception as e:
        print(f"Error getting data: {e}")
        stat_nc.close()
        return None

def get_value_from_coordinates(easting, northing, variable_name, 
                              geom_file_path="14DayHYD_NoWind_Nash_HD_waqgeom.nc", 
                              stat_file_path="deltashell-stat_map.nc"):
    """
    Get the value of a variable at specified coordinates.
    
    Args:
        easting: X coordinate (easting)
        northing: Y coordinate (northing)
        variable_name: Name of the variable to extract
        geom_file_path: Path to the geometry netCDF file
        stat_file_path: Path to the statistics netCDF file
        
    Returns:
        The value of the variable at the specified coordinates, or None if not found
    """
    # Find which element contains the coordinates
    element_id = find_element_from_coordinates(easting, northing, geom_file_path)
    
    if element_id is None:
        print(f"No element found at coordinates ({easting}, {northing})")
        return None
        
    # Get the value for this element
    return get_value_for_element(element_id, variable_name, stat_file_path)

# Example usage:
if __name__ == "__main__":
    # Example coordinates
    test_easting, test_northing = 332732, 184236
    test_variable = "Mesh2D_2d_MAX_FullRun_cTR1"
    
    # Test each function
    element_id = find_element_from_coordinates(test_easting, test_northing)
    if element_id is not None:
        print(f"Coordinates ({test_easting}, {test_northing}) are in element: {element_id}")
        
        value = get_value_for_element(element_id, test_variable)
        if value is not None:
            print(f"Value of {test_variable} at element {element_id}: {value}")
            
    # Test combined function
    value = get_value_from_coordinates(test_easting, test_northing, test_variable)
    if value is not None:
        print(f"Value of {test_variable} at coordinates ({test_easting}, {test_northing}): {value}")