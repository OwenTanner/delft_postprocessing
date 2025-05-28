import geopandas as gpd
import os

# Set folder containing shapefiles
folder_path = r"C:\Users\DOHE4616\OneDrive Corp\AtkinsRéalis\5230317-RegionalCoastalInvestigations - Collaboration\02 Deliver Work\Modelling\Magor\WD Postprocessing\Usk ENs"

# Loop through all .shp files
for file in os.listdir(folder_path):
    if file.endswith(".shp"):
        shp_path = os.path.join(folder_path, file)
        csv_path = os.path.join(folder_path, file.replace(".shp", ".csv"))

        # Read shapefile and export as CSV, ignoring geometry column
        gdf = gpd.read_file(shp_path)
        gdf.drop(columns='geometry', inplace=True)
        gdf.to_csv(csv_path, index=False)

print("Conversion complete! CSV files saved in the same folder.")