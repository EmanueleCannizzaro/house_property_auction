
#Import required packages
from rightmove_webscraper import RightmoveData
import pandas as pd
from geopy.geocoders import Nominatim
import folium
from folium.plugins import MarkerCluster
from datetime import date

#Scrape data from RightMove
url = "https://www.rightmove.co.uk/property-for-sale/find.html?searchType=SALE&locationIdentifier=REGION%5E93598&insId=1&radius=0.0&minPrice=&maxPrice=&minBedrooms=&maxBedrooms=&displayPropertyType=&maxDaysSinceAdded=&_includeSSTC=on&sortByPriceDescending=&primaryDisplayPropertyType=&secondaryDisplayPropertyType=&oldDisplayPropertyType=&oldPrimaryDisplayPropertyType=&newHome=&auction=false"

rm = RightmoveData(url)
data = rm.get_results

#Find coordinates for listings using Nominatim and Geopy
geolocator = Nominatim(user_agent="example app")
data["location"] = data["address"].apply(geolocator.geocode)

#Drop listings with no geolocation
location_data = data.dropna(subset=['location']).reset_index(drop=True)
location_data['coordinates'] = [location_data['location'][i][1] for i in range(len(location_data))]
location_data['lat'] = [location_data.coordinates[i][0] for i in range(len(location_data))]
location_data['lon'] = [location_data.coordinates[i][1] for i in range(len(location_data))]

#Get current date
today = date.today().strftime("%m%d%y")

#Save data gathered to CSV
data.to_csv('data/raw_data_' + today + '.csv')
location_data.to_csv('data/loc_data_' + today + '.csv')

#chron job info
0 0 * * 0 /Users/charlotte/opt/anaconda3/envs/scrapers/bin/python /Users/charlotte/Documents/Projects/real-estate/real-estate-scraper.py
