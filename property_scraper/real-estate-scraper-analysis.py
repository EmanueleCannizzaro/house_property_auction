
from rightmove_webscraper import RightmoveData
import pandas as pd
url = "https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E93598&insId=1&radius=0.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false"
print(url)
rm = RightmoveData(url)
data = rm.get_results
data.head()

#Find coordinates for listings
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="example app")
data["location"] = data["address"].apply(geolocator.geocode)

#drop ones with no geolocation
location_data = data.dropna(subset=['loc']).reset_index(drop=True)
location_data['coordinates'] = [location_data['loc'][i][1] for i in range(len(location_data))]
location_data['lat'] = [location_data.coordinates[i][0] for i in range(len(location_data))]
location_data['lon'] = [location_data.coordinates[i][1] for i in range(len(location_data))]

location_data = pd.read_csv('loc_data_011721.csv')

import folium
from folium.plugins import MarkerCluster

# Create a map object and center it to the avarage coordinates to m
m = folium.Map(location=location_data[["lat", "lon"]].mean().to_list(), zoom_start=2)
# if the points are too close to each other, cluster them, create a cluster overlay with MarkerCluster, add to m
marker_cluster = MarkerCluster().add_to(m)
# draw the markers and assign popup and hover texlots
# add the markers the the cluster layers so that they are automatically clustered
for i,r in location_data.iterrows():
    location = (r["lat"], r["lon"])
    folium.Marker(location=location,
                      popup = r['address'],
                      tooltip=r['type'])\
    .add_to(marker_cluster)
# display the map
m

#Save data gathered to CSV
data.to_csv('data/raw_data_011721.csv')
location_data.to_csv('data/loc_data_011721.csv')

#Figure out how to run the script weekly and select only new listings
