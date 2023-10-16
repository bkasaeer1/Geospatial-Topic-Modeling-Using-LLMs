#library imports
import geopandas as gpd
import pandas as pd
import arcpy
import os
from pyproj import Transformer
import numpy as np
import math


#parameters
# the path to your local directory containing all project files
rt = r'path/to/your/project/output/directory'
#your desired Esri file geodatabase name that contains the project geographic feature layers and data tables
fgdbname = 'GeospatialTweetAnalysis.gdb'
#reference: https://hub.arcgis.com/datasets/esri::usa-census-populated-place-areas-1/explore
cpp_shp = r'path/to/your/census/populated/place/areas/shapefile'
#reference: https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html
state_shp = r'path/to/your/census/states/boundaries/shapefile'


def create_filegdb(rt, fgdbname):
    """
    This function creates an empty Esri file geodatabase to store the project geographic feature classes. 

    INPUTS:
    rt: specify the project directory in which you would like your file geodatabase to be stored!
    fgdbname: name of the file geodatabase

    OUTPUTS: 
    an empty Esri file geodatabase with the specified name in the specified directory!
    """
    fgdbdir=rt+'\\'+fgdbname
    if not os.path.isdir(fgdbdir):
        arcpy.CreateFileGDB_management(rt, fgdbname)
    return fgdbdir


def convert_xy_epsg(df, long, lat, epsg1 = 4326, epsg2 = 3857):
    """
    This function creates converts latitude and longitude inside a pandas df from EPSG1 to EPSG2

    INPUTS:
    df: pandas dataframe containing the original latitude and longitudes of points. 
    long: longitudes of points 
    lat: latitude of points 
    epsg1: original EPSG (default: 4326)
    epsg2: original EPSG (default: 3857)

    OUTPUTS: 
    a new dataframe with with converted latitude and longitudes of EPSG2
    """
    #create a transfomer from epsg1 to epsg2
    transformer = Transformer.from_crs("epsg:%s"%epsg1, "epsg:%s"%epsg2, always_xy = True)    
    #calculate new x & y in the new coordinates
    newxys = transformer.transform(list(df[long]),list(df[lat]))
    #replace them with the new coordinate values
    df[long + str(epsg2)],df[lat + str(epsg2)] = newxys[0], newxys[1]
    return df


def data_to_gdbtable(fgdb, df, outname):
    """
    This function generates an Esri file geodatabase table from a specified Pandas dataframe!

    INPUTS:
    fgdb: directory of the Esri file geodatabase that will host the new file geodatabase table
    df: a pandas dataframe 
    outname: name of the new file geodatabase table
 

    OUTPUTS: 
    outputs the name of the new file geodatabase table
    """
    #convert the df to a numpy array
    arr = np.array(np.rec.fromrecords(df.values))
    names = df.dtypes.index.tolist()
    arr.dtype.names = tuple(names)
    #convert the numpy array to a gdp table
    arcpy.da.NumPyArrayToTable(arr, fgdb+'\\'+outname)
    return outname


def find_most_populous_cities(cpp_shp):
    """
    This function reads the link to the US Census most populous cities Esri shapefil on your local drive and
    filters the dataset to only keep the most populous cities of every US state. Here is the source to download
    the dataset from Esri ARCGIS Hub: https://hub.arcgis.com/datasets/esri::usa-census-populated-place-areas-1/explore

    INPUTS:
    cpp_shp: directory of the Esri file geodatabase that will host the new file geodatabase table


    OUTPUTS: 
    outputs a geodataframe that contains the most populous cities of US states 
    """
    #read the shapefile as a geodataframe using geopandas! 
    gdf_cpp = gpd.read_file(cpp_shp, crs = {'init': 'epsg:4326'})
    #find index of rows corresponding the most populous city of eah US state
    StatesMaxPopIdx = gdf_cpp.groupby('ST').apply(lambda x: x.POP2012.idxmax())
    #filter the geodataframe to only include those most populous cities 
    gdf_cpp = gdf_cpp.iloc[StatesMaxPopIdx.values, :]
    return gdf_cpp


def create_city_buffers(cpp_shp, fgdbname):
    """
    This function reads the geodatarfame of most US populous cities resulted from find_most_populous_cities
    and creates a buffer area around them. The buffer is a circle that includes the rectangle representing city
    boundaries.

    INPUTS:
    cpp_shp: directory of the Esri file geodatabase that will host the new file geodatabase table
    fgdbname: the name of the Esri file geodatabase to store all the information in it

    OUTPUTS: 
    It generates city buffers within the specified file geodatabase 
    """
    #create the most populous cities geodataframe 
    gdf_cpp = find_most_populous_cities(cpp_shp)
    #calculate min and max x, y in degrees
    df_bounds = gdf_cpp.geometry.bounds
    #and convert lower left and upper right cornerts to UTM coordinates 
    df_bounds = convert_xy_epsg(df_bounds,'minx','miny', 4326, 3857)
    df_bounds = convert_xy_epsg(df_bounds,'maxx','maxy', 4326, 3857)
    #now use the Pythagorean Theorem and UTM coordinations to calculate radius of the fitted circle 
    df_bounds['cir_cen_x'] = (df_bounds.maxx + df_bounds.minx) / 2
    df_bounds['cir_cen_y'] = (df_bounds.maxy + df_bounds.miny) / 2
    #It is assumed the earth is flat here but which is reasonable for a city size scale. I checked with 
    #https://boulter.com/gps/distance/?from=60.733788+-150.281695+&to=61.483938+-148.460007&units=k
    #and it was very close with 129 km (above source) versu 133 km (this method)
    df_bounds['cir_radius_m'] = df_bounds.apply(lambda row: (((row.maxx3857 - row.minx3857)/2)**2 + 
                            ((row.maxy3857 - row.miny3857) / 2)**2)**0.5, axis = 1)
    #concatenate the center geometries with radius to have the city points columns 
    gdf_citypoints = pd.concat([gdf_cpp.drop(columns = 'geometry'),
                              df_bounds[['cir_cen_x','cir_cen_y','cir_radius_m']]], axis = 1)
    #create a file gdb to store the analysis outputs
    fgdb = create_filegdb(rt, fgdbname)
    #and set it as the main workspace 
    arcpy.env.workspace = fgdb

    #create a text column in gdf_citypoints to indicate the buffer distance for the ARCGIS Pro Buffer tool
    gdf_citypoints['buff'] = gdf_citypoints.cir_radius_m.astype(int).astype(str) + ' Meters'

    #now convert the gdb into a file gdb
    table = data_to_gdbtable(fgdb, gdf_citypoints,'temp')
    #convert the table into a point feature layer 
    _=arcpy.management.XYTableToPoint(table, 'CityPointsLyr',
                                      "cir_cen_x", "cir_cen_y", "#","#")

    # create a buffer using buffer info
    # the buffers were visually inspected relative to the actual city boindaries. It appears that it is slightly 
    # overestimating which is good as it covers some suburban areas. The only issue is that Newark in NJ fell within 
    # the NYC buffer. So, only data for NYC was collected and tweets from Newark were seperated to represent NJ. 
    _=arcpy.analysis.Buffer('CityPointsLyr', 'CityBuff', 'buff', 
                            "FULL", "ROUND", "NONE", None, "PLANAR")
    
    
def create_state_buffers(state_shp, fgdbname):
    """
    This function reads US states shapefile from the Census website provided below and creates a buffer area around 
    their center to collect more tweets which may have been missed from city-scale tweet collection step. The buffer 
    is a circle that has an area equal to the land area of the state. Use the below link to download the US states shapefile: 
    https://www.census.gov/geographies/mapping-files/time-series/geo/carto-boundary-file.html

    INPUTS:
    state_shp: directory of the shapefile that contains the most populous cities of US states
    fgdbname: the name of the Esri file geodatabase to store all the information in it

    OUTPUTS: 
    It generates state buffers within the specified file geodatabase 
    """
    #make state radius smaller to reduce inter-state overlaps
    gdf_States = gpd.read_file(state_shp, crs = {'init': 'epsg:4326'})
    gdf_States['cir_cen_x'] = gdf_States.geometry.centroid.x
    gdf_States['cir_cen_y'] = gdf_States.geometry.centroid.y
    gdf_States['cir_radius_m'] = 0.72*(gdf_States.ALAND/math.pi)**0.5
    gdf_States['buff'] = gdf_States.cir_radius_m.astype(int).astype(str) + ' Meters'
    table = data_to_gdbtable(fgdb, gdf_States[['STUSPS',"cir_cen_x", "cir_cen_y",
                                            'cir_radius_m','buff']],'temp')
    _ = arcpy.management.XYTableToPoint(table, 'StatePointsLyr',"cir_cen_x", 
                                      "cir_cen_y", "#","#")
    #create a buffer using buffer info
    _ = arcpy.analysis.Buffer('StatePointsLyr', 'StatesBuff', 'buff', "FULL", 
                            "ROUND", "NONE", None, "PLANAR")
    
    
if __name__ == '__main__':
    print('----Process Started----')
    start = time.time()
    #define below parameter to keep track of total processing time! 
    totalT = 0  

    _ = create_city_buffers(gdf_cpp, fgdbname)
    print('the US most populous city buffers were generated inside the %s file geodatabase!'%fgdbname)

    _ = create_state_buffers(state_shp, fgdbname)
    print('the US state buffers were generated inside the %s file geodatabase!'%fgdbname)
    
    end = time.time()  
    deltaT = end - start

    print('----Process Ended----')
    print('----The processing as done in %s minutes!'%round(deltaT/60, 1))





