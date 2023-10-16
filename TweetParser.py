#import libraries
import snscrape.modules.twitter as sntwitter
import geopandas as gpd
import pandas as pd
import itertools
import math

#parameters
# the path to your local directory containing all project files
rt = r'path/to/your/project/output/directory'
#your desired Esri file geodatabase name that contains the project geographic feature layers and data tables
fgdbname = 'GeospatialTweetAnalysis.gdb'
# keywords to search Twitter regarding the COVID-19 virus
content = 'covid OR corona OR coronavirus OR pandemic OR outbreak OR epidemic' 
# specify start and end date of tweets to be collected on the above topics
start_date = '2020-09-01'
end_date = '2020-12-31'

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


def create_search_centers(rt, fgdbname):
    
    """
    This function combines the city and state centers and create a full set of search center points with their
    search radius to find relevant tweets in each geographic area

    INPUTS:
    rt: specify the project directory in which you would like your file geodatabase to be stored!
    fgdbname: name of the file geodatabase

    OUTPUTS: 
    a pandas dataframe with a full set of search center points to find relevant tweets
    """
    
    # connect to the existing Esri file geodatabase contaning the search buffers
    fgdb = create_filegdb(rt, fgdbname)
    #and set it as the main workspace 
    arcpy.env.workspace = fgdb
    
    statepoints = gpd.read_file(fgdb, layer = 'StatePointsLyr')
    citypoints = gpd.read_file(fgdb, layer = 'CityPointsLyr')
    
    #change name of cities to aligh
    citypoints['NAME'] = citypoints['NAME'] + ' City'
    #specify column names to use 
    usecols=['ST','cir_cen_x','cir_cen_y','cir_radius_m','NAME']
    # concatenate the state and city dataframes 
    points = pd.concat([statepoints.rename({'STUSPS':'ST'}, axis=1)[usecols],
                        citypoints[usecols]], axis=0)
    return points 

    
def parse_tweets(points, start_date, end_date, content):
    """
    This function searches Twitter based on the specified contents and date interval. 

    INPUTS:
    points: pandas dataframe containing search center points data
    start_date: start date to search for relavant tweets 
    end_date: end date to search for relavant tweets 
    content: contents to search Twitter
    
    OUTPUTS: 
    a full set of search center points to find relevant tweets
    """

    #create an empty list to store all the pandas dataframes containing scraped tweets 
    dfs = []
    
    for i,row in points.iterrows():
        
        #specify the location string: geocode:lat,long,radius
        loc = '%s, %s, %skm'%(row['cir_cen_y'], row['cir_cen_x'], row['cir_radius_m'] / 1000)
        #generate a search string 
        srch = '%s geocode:"%s" since:%s until:%s lang:en'%(content, loc, start_date, end_date) 

        try:    
            df_coord = pd.DataFrame(itertools.islice(sntwitter.TwitterSearchScraper(srch).get_items(),
                                                     10**10))[['user', 'date','content']]
            #add user location  
            df_coord['user_location'] =  df_coord['user'].apply(lambda x: x['location'])
            #add a location column to the df based on my search
            df_coord['searched_location'] = row['ST']
            
            dfs.append(df_coord)
            
            print('tweets for %s was collected: %s'%row['NAME'])

        except:
            print('Tweet scparing for %s did not work!'%row['NAME'])  

    #merge all the data 
    full_df = pd.concat(dfs2)
    #save it all as a csv 
    COVID_df.to_csv(rt + '\\AllTweets.csv')
    
    
if __name__ == '__main__':
    print('----Process Started----')
    start = time.time()
    #define below parameter to keep track of total processing time! 
    totalT = 0  

    points = create_search_centers(rt, fgdbname)
    print('a dataframe containing full set of search centers in the US was created!')

    _ = parse_tweets(points, start_date, end_date, content)
    print('all relavant tweets from the above geographic locations were scraped and stored as a CSV file!')
    
    end = time.time()  
    deltaT = end - start
    
    print('----Process Ended----')
    print('----The processing as done in %s minutes!'%round(deltaT/60, 1))    

