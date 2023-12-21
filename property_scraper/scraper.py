
import logging
import sys

from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
import folium
from folium.plugins import MarkerCluster
#from geopy.geocoders import Nominatim
import googlemaps
import json
from lxml import etree, html
from lxml.etree import tostring
import numpy as np
import os
import pandas as pd
import re
import requests
#import scraperwiki
#import StringIO
from tqdm.auto import tqdm
#import urllib
#import urllib.request

from property_scraper import DEFAULT_GEOCODE_ENGINE, DEFAULT_HTML_PARSER, MAX_TIMEOUT, SCRAPENINJA_URL_ROOTNAME, sleep_randomly
from property_scraper.page import Page
from property_scraper.property import Property


@traced
@logged
class Scraper:
    """The Scraper collects structured data on properties
    returned by a search performed on www.rightmove.co.uk

    An instance of the class provides attributes to access data from the search
    results, the most useful being `get_results`, which returns all results as a
    Pandas DataFrame object.

    The query to rightmove can be renewed by calling the `refresh_data` method.
    """

    URL_ROOTNAME = ''
    KEYS = []
    BASE_HEADERS = {
        #"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        #"accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        #"accept-language": "en-US;en;q=0.9",
        #"accept-encoding": "gzip, deflate, br",
    }


    def __init__(self, name:str=None):
        self._name = name
        #self._protocol = self.PROTOCOLS[-1]
        self._url = None
        self.page = Page()
        self.property = Property()
        self._location = None
        self._results = []

    @staticmethod
    def read_configuration(filename:str):
        with open(filename, 'r') as f:
            _configuration = json.load(f)
        return _configuration

    def show_configuration(self):
        print(json.dumps(self.configuration, indent=4))

    @staticmethod
    def read_parameters(filename:str):
        with open(filename, 'r') as f:
            _parameters = json.load(f)
        return _parameters

        
    @staticmethod
    def write_parameters(filename:str):
        with open(filename, 'w') as f:
            json.dump(parameters, f, indent=4)

    ''' The functions below could be improved by redefining them based on the urllib.parse module and urlparse function.
        See https://docs.python.org/3/library/urllib.parse.html.
    '''

    def get_parameters_from_url(self, url:str):
        tokens = url.split('/')[-1].split('?')[-1].split('&')
        _values = {}
        for key in self.KEYS:
            was_found_flag = False
            for token in tokens:
                if token.lower().startswith(key.lower()):
                    _values[key] = token[len(key)+1:]
                    was_found_flag = True
                    break
            if not was_found_flag:
                _values[key] = None
        return _values

    @property
    def protocol(self):
        return self._protocol
        
    @protocol.setter
    def protocol(self, value:str):
        self._protocol = value        
    
    @protocol.deleter
    def protocol(self):
        del self._protocol

    @property
    def property_type(self):
        return self._property_type
        
    @property_type.setter
    def property_type(self, value:str):
        self._property_type = value    
    
    @property_type.deleter
    def property_type(self):
        del self._property_type
    
    @property
    def location(self):
        return self._location
        
    @location.setter
    def location(self, value:str):
        self._location = value        
    
    @location.deleter
    def location(self):
        del self._location

    @property
    def country(self):
        return self._country
        
    @country.setter
    def country(self, value:str):
        self._country = value        
    
    @country.deleter
    def country(self):
        del self._country

    @property
    def region(self):
        return self._region
        
    @region.setter
    def region(self, value:str):
        self._region = value
    
    @region.deleter
    def region(self):
        del self._region
            
    @property
    def url(self):
        return self._url
        
    @url.setter
    def url(self, value:str):
        self._url = value
    
    @url.deleter
    def url(self):
        del self._url

    @staticmethod
    def get_request(url:str, **kwargs):        
        r = requests.get(url, **kwargs)
        # Requests to scrape lots of pages eventually get status 400, so:
        if r.status_code != 200:
            raise ValueError(f'The request status code is {r.status_code}.')
        return r.status_code, r.content

    def init_scrapeninja(self, search_filename:str, **kwargs):
        filename = os.path.join(os.path.expanduser('~'), "scrapeninja.json")
        headers = Scraper().read_parameters(filename)        
        #print(json.dumps(headers, indent=4))
        
        payload = Scraper().read_parameters(search_filename)        
        #print(json.dumps(payload, indent=4))
        
        return headers, payload

    @staticmethod
    def get_request_via_scrapeninja(headers:dict, payload:dict, **kwargs):
        url = SCRAPENINJA_URL_ROOTNAME
        r = requests.request("POST", url, json=payload, headers=headers)
                
        # Requests to scrape lots of pages eventually get status 400, so:
        if r.status_code != 200:
            raise ValueError(f'The request status code is {r.status_code}.')
        return r


    @property
    def number_of_results(self, engine:str=DEFAULT_HTML_PARSER):
        """Returns an integer of the total number of listings as displayed on
        the first page of results. Note that not all listings are available to
        scrape because rightmove limits the number of accessible pages."""
        
        if engine == 'xml.html':
            tree = html.fromstring(self.content)
            #<span class="searchHeader-resultCount" data-bind="counter: resultCount, formatter: numberFormatter">115</span>
            xpath = f"""//{self.NUMBER_OF_RESULTS['tag']}[@{self.NUMBER_OF_RESULTS['attribute']}="{self.NUMBER_OF_RESULTS['value']}"]/text()"""
            _number_of_results = int(tree.xpath(xpath)[0].replace(",", ""))
        elif engine == 'bs4':
            soup = BeautifulSoup(self.content, 'html.parser')
            non_decimal = re.compile(r'[^\d.]+')
            _number_of_results = soup.find(self.NUMBER_OF_RESULTS['tag'], {self.NUMBER_OF_RESULTS['attribute']: self.NUMBER_OF_RESULTS['value']}).text.strip()
            if ' ' in _number_of_results:
                _number_of_results = _number_of_results.split(' ')[0]
                if '.' in _number_of_results:
                    _number_of_results = _number_of_results.replace('.', '')
            _number_of_results = int(non_decimal.sub('', _number_of_results))
        return _number_of_results

    @property
    def number_of_pages(self):
        """Returns the number of result pages returned by the search URL. 
        Note that the website limits results to a
        maximum of 42 accessible pages."""
        _number_of_pages = self.number_of_results // self.NUMBER_OF_RESULTS_PER_PAGE
        if self.number_of_results % self.NUMBER_OF_RESULTS_PER_PAGE > 0:
            _number_of_pages += 1
        # Rightmove will return a maximum of 42 results pages, hence:
        _number_of_pages = min(_number_of_pages, self.MAXIMUM_NUMBER_OF_PAGES)
        return _number_of_pages

    @property
    def number_of_batches(self):
        if self.number_of_results == self.number_of_pages * self.NUMBER_OF_RESULTS_PER_PAGE:
            _number_of_batches = [self.NUMBER_OF_RESULTS_PER_PAGE] * self.number_of_pages
        else:
            _number_of_batches = [self.NUMBER_OF_RESULTS_PER_PAGE] * (self.number_of_pages - 1) + [self.number_of_results % self.NUMBER_OF_RESULTS_PER_PAGE]
        return _number_of_batches
    
    def get_next_search_page(self, ix):
        return f"{str(self.url)}&index={ix * self.NUMBER_OF_RESULTS_PER_PAGE}"
    
    '''    
    def validate_url(self):
        """Basic validation that the URL at least starts in the right format and
        returns status code 200."""
        real_url = "{}://www.rightmove.co.uk/{}/find.html?"
        
        
        urls = [real_url.format(p, t) for p in protocols for t in types]
        conditions = [self.url.startswith(u) for u in urls]
        conditions.append(self._status_code == 200)
        if not any(conditions):
            raise ValueError(f"Invalid rightmove search URL:\n\n\t{self.url}")
    '''

    def get_page(self, url:str, engine:str=DEFAULT_HTML_PARSER, use_scrapeninja:bool=False, payload:dict=None, headers:dict=None): #, get_floorplans: bool = False):
        """Build a Pandas DataFrame with all results returned by the search."""

        # Iterate through all pages scraping results:
        _pages = []
        if use_scrapeninja:
            payload['url'] = url
            status_code, content = self.get_request_via_scrapeninja(payload, headers)
        else:
            status_code, content = self.get_request(url, timeout=MAX_TIMEOUT)
        _page = self.page.get_page(content, self.property_type, self.number_of_batches[0], engine)#, get_floorplans=get_floorplans)
        return _page


    def get_results(self, engine:str=DEFAULT_HTML_PARSER): #, get_floorplans: bool = False):
        """Build a Pandas DataFrame with all results returned by the search."""

        #if use_scrapeninja:
        #    headers, payload = self.init_scrapeninja(search_filename)

        # Iterate through all pages scraping results:
        _pages = []

        _page = self.get_page(url, engine) #, self.payload, self.headers)
        _pages.append(_page)
        pbar = tqdm(range(1, self.number_of_pages), position=0)
        for ix in pbar:
            # Create the URL of the specific results page:
            _url = self.get_next_search_page(ix)
            self.__log.info(f"{_url}")

            # Make the request:
            _page = self.get_page(url, engine) #, payload, headers)
            _pages.append(_page)

            sleep_randomly()

        # Concatenate the temporary DataFrame with the full DataFrame:
        _results = pd.concat(_pages)
        #_results = _results.dropna(how='all').dropna(how='all', axis=1)
        _results = _results.drop_duplicates(keep='first')
        _results = _results.reset_index()
        display(_results.head().T)
        return _results
        
    def fix_results(self, results: pd.DataFrame):
        # Reset the index:
        #results = results.reset_index()
        return results

    def enrich_results(self, results:pd.DataFrame, html_engine:str=DEFAULT_HTML_PARSER, map_engine:str=DEFAULT_GEOCODE_ENGINE, api_key:str=None):        
        _results = results.copy()
        _results = self.enrich_results_with_details(results, self.property_type, html_engine)
        _results = self.enrich_results_with_geocode(_results, engine=map_engine, api_key=api_key)
        return _results
        
    def enrich_results_with_details(self, results:pd.DataFrame, rent_or_sale:str, html_engine:str=DEFAULT_HTML_PARSER):
        _results = results.copy()
        pbar = tqdm(_results.index)
        for ix in pbar:
            _url = _results.loc[ix, 'Hyperlink']
            self.__log.info(_url)
            self.status_code, _content = self.get_request(_url, timeout=MAX_TIMEOUT, headers=self.BASE_HEADERS)
            self.property.get_page(_content, rent_or_sale)
            break
        #self.__log.info('\tColumns: \n' + '\n'.join(sorted(_results.columns)))
        return _results

    def geolocate(self, _address:str, geolocator):
        _address = str(_address)
        if _address.endswith('.'):
            _address = _address[:-1]
        _location = self.location.title()
        if _location not in _address.title():
            _address = f"{_address}, {_location}"
        _country = self.country.title()
        if _country not in _address.title():
            _address = f"{_address}, {_country}"
        geocode = geolocator.geocode(_address)
        try:
            return (geocode[0]['geometry']['location']['lat'], geocode[0]['geometry']['location']['lng'])
        except:
            print(f"Address {_address} was not located!")
            return (0., 0.)
        
    def enrich_results_with_geocode(self, results:pd.DataFrame, engine:str=DEFAULT_GEOCODE_ENGINE, api_key:str=None):
        # Geocoding an address
        
        if engine == 'googlemaps':
            geolocator = googlemaps.Client(key=api_key)
        elif engine == 'Nominatim':
            #Find coordinates for listings using Nominatim and Geopy
            geolocator = Nominatim(user_agent="example app")
        else:
            raise ValueError()
        
        _results = results.copy()
        #self.__log.info('\tColumns: \n' + '\n'.join(sorted(_results.columns)))
        _results['Geocode'] = _results[['Address']].apply(lambda x: self.geolocate(x[0], geolocator), axis=1)

        return _results
        
    def scrape(self, html_engine:str=DEFAULT_HTML_PARSER, map_engine:str=DEFAULT_GEOCODE_ENGINE, api_key:str=None): #, get_floorplans:bool=False):
        """Initialize the scraper with a URL from the results of a property
        search performed on www.rightmove.co.uk.

        Args:
            url (str): full HTML link to a page of rightmove search results.
            get_floorplans (bool): optionally scrape links to the individual
                floor plan images for each listing (be warned this drastically
                increases runtime so is False by default).
        """

        self.status_code, self.content = self.get_request(self.url, timeout=MAX_TIMEOUT, headers=self.BASE_HEADERS)
        
        self.__log.info(f"Found {self.number_of_results} results in {self.number_of_pages} pages.")
        self.__log.info("Number of branches is : " + ", ".join([str(x) for x in self.number_of_batches]))
        
        _results = self.get_results(html_engine) #get_floorplans=get_floorplans)
        #self.__log.info('\n'.join(sorted([str(x) for x in _results['Hyperlink'].unique()])))
        _results = self.fix_results(_results)
        _results = self.enrich_results(_results, html_engine, map_engine, api_key)
        return _results

    def create_map(self):
        origin = self.results.loc[list(self.results.index)[0], 'Geocode']
        self.results['color'] = 'red' #'darkblue'
        self.results['popup'] = 'ID: ' + self.results['Address'] + ' \n' + self.results['color']
        
        tooltip = "Click here to see more details!"

        m = folium.Map(location=origin, tiles='Stamen Terrain', zoom_start=12)
        mc = MarkerCluster().add_to(m)
        pbar = tqdm(self.results.index)
        for idx in pbar:
            pbar.set_description(f"Processing {self.results.loc[idx, 'Address']:>80}")
            folium.Marker(self.results.loc[idx, 'Geocode'],                           
                        popup=f"<a href={self.results.loc[idx, 'Hyperlink']} target='_blank'>{self.results.loc[idx, 'popup']}</a>", 
                        tooltip=tooltip,
                        icon=folium.Icon(color=self.results.loc[idx, 'color'], icon_color='white', icon='male', angle=0, prefix='fa')).add_to(mc)
        return m
        
    '''    
    def check_for_completeness(self):
        # Go through each station: scrape each set of results in turn. 
        for station in stations:
            station_name = station.keys()[0].title()
            print 'Scraping %s' % station_name
            station_id = station.values()[0]
            url1 = '/property-for-sale/find.html?locationIdentifier=STATION^%s&minPrice=%s&maxPrice=%s' % (station_id, MIN_PRICE, MAX_PRICE)
            url2 = '&minBedrooms=%s&displayPropertyType=houses&oldDisplayPropertyType=houses&radius=%s' % (MIN_BEDROOMS, RADIUS_MILES)
            # displayPropertyType=detachedshouses
            INITIAL_URL = url1 + url2
            scrape_results_page(INITIAL_URL, town=station_name, initial=True)
    
    
    def refresh_data(self): #, url: str = None, get_floorplans: bool = False):
        """Make a fresh GET request for the rightmove data.

        Args:
            url (str): optionally pass a new HTML link to a page of rightmove
                search results (else defaults to the current `url` attribute).
            get_floorplans (bool): optionally scrape links to the individual
                flooplan images for each listing (this drastically increases
                runtime so is False by default).
        """
        #url = self.url if not url else url
        _status_code, _first_page = self.get_request()
        #self._url = url
        #self._validate_url()
        #self._results = self._get_results(get_floorplans=get_floorplans)
    '''

    '''

    @property
    def average_price(self):
        """Average price of all results returned by `get_results` (ignoring
        results which don't list a price)."""
        total = self.get_results["price"].dropna().sum()
        return total / self.results_count

    def summary(self, by: str = None):
        """DataFrame summarising results by mean price and count. Defaults to
        grouping by `number_bedrooms` (residential) or `type` (commercial), but
        accepts any column name from `get_results` as a grouper.

        Args:
            by (str): valid column name from `get_results` DataFrame attribute.
        """
        if not by:
            by = "type" if "commercial" in self.rent_or_sale else "number_bedrooms"
        assert by in self.get_results.columns, f"Column not found in `get_results`: {by}"
        df = self.get_results.dropna(axis=0, subset=["price"])
        groupers = {"price": ["count", "mean"]}
        df = df.groupby(df[by]).agg(groupers)
        df.columns = df.columns.get_level_values(1)
        df.reset_index(inplace=True)
        if "number_bedrooms" in df.columns:
            df["number_bedrooms"] = df["number_bedrooms"].astype(int)
            df.sort_values(by=["number_bedrooms"], inplace=True)
        else:
            df.sort_values(by=["count"], inplace=True, ascending=False)
        return df.reset_index(drop=True)

    @property
    def rent_or_sale(self):
        """String specifying if the search is for properties for rent or sale.
        Required because Xpaths are different for the target elements."""
        if "/property-for-sale/" in self.url or "/new-homes-for-sale/" in self.url:
            return "sale"
        elif "/property-to-rent/" in self.url:
            return "rent"
        elif "/commercial-property-for-sale/" in self.url:
            return "sale-commercial"
        elif "/commercial-property-to-let/" in self.url:
            return "rent-commercial"
        else:
            raise ValueError(f"Invalid rightmove URL:\n\n\t{self.url}")

    @property
    def number_of_results_count_display(self):
    '''
