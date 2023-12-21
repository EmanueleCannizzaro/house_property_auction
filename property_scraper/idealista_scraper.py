
import logging
from autologging import logged, TRACE, traced

from bs4 import BeautifulSoup
from datetime import datetime
import json
from lxml import etree, html
from lxml.etree import tostring
import numpy as np
import pandas as pd
import re
import requests
from time import sleep
from tqdm.auto import tqdm

from property_scraper import DEFAULT_GEOCODE_ENGINE, DEFAULT_HTML_PARSER, IDEALISTA_URL_ROOTNAME
from property_scraper.idealista_page import IdealistaPage
from property_scraper.idealista_property import IdealistaProperty
from property_scraper.scraper import Scraper


@logged(logging.getLogger("property_scraper"))
class IdealistaScraper(Scraper):
    """The `Idealista` webscraper collects structured data on properties
    returned by a search performed on www.rightmove.co.uk

    An instance of the class provides attributes to access data from the search
    results, the most useful being `get_results`, which returns all results as a
    Pandas DataFrame object.

    The query to rightmove can be renewed by calling the `refresh_data` method.
    """
    
    URL_ROOTNAME = IDEALISTA_URL_ROOTNAME
    
    KEYS = [
        ##'citta',         
        #'criterio',
        #'prezzoMinimo',
        #'prezzoMassimo',
        #'superficieMinima',
        #'bagni'
    ]
    
    # There are 25 results per page.
    NUMBER_OF_RESULTS_PER_PAGE = 25
    ## Rightmove will return a maximum of 42 results pages
    MAXIMUM_NUMBER_OF_PAGES = 42
    ##PROTOCOLS = ["http", "https"]
    PROPERTY_TYPES = ["property-to-rent", "vendita-case", "new-homes-for-sale"]    
    
    NUMBER_OF_RESULTS = {
        'tag' : 'h1', 
        'attribute': 'id',
        'value': 'h1-container'
    }


    def __init__(self, name:str=None):
        super(IdealistaScraper, self).__init__()
        self.page = IdealistaPage()
        self.property = IdealistaProperty()
        
        self._property_type = self.PROPERTY_TYPES[1]


    def set_url(self, parameters:dict):
        _url = f"{self.URL_ROOTNAME}/vendita-case/{parameters['citta'].lower()}-{parameters['citta'].lower()}/"
        count = 0
        for ix in range(len(self.KEYS)):
            key = self.KEYS[ix]
            if key in parameters.keys():
                if parameters[key]:
                    if count > 0:
                        _url += f"&{key}={parameters[key]}"
                    else:
                        _url += f"{key}={parameters[key]}"
                    count += 1
        return _url

    def read_parameters(self, filename:str):
        _parameters = super(IdealistaScraper, self).read_parameters(filename)
        self.location = _parameters["citta"]
        self.country = _parameters["paese"]
        self.property_type = _parameters["vendita_o_affitto"]
        if hasattr(self, 'REGIONS'):
            self.region = self.REGIONS[_parameters['location']]
        return _parameters



    '''
    def get_results(self, engine:str=DEFAULT_HTML_PARSER):
        """Build a Pandas DataFrame with all results returned by the search."""

        # Iterate through all pages scraping results:
        _pages = []
        self.status_code, self.content = self.get_request(self.url)
        _page = self.page.get_page(self.content, self._property_type, self.number_of_batches[0], engine)
        _pages.append(_page)
        pbar = tqdm(range(1, self.number_of_pages), position=0)
        for ix in pbar:
            # Create the URL of the specific results page:
            _url = f"{str(self.url)}&index={ix * self.NUMBER_OF_RESULTS_PER_PAGE}"
            self.__log.info(f"{_url}")

            # Make the request:
            self.status_code, self.content = self.get_request(_url)
            _page = self.page.get_page(self.content, self._property_type, self.number_of_batches[ix], engine)
            _pages.append(_page)
            
            sleep(self.WAITING_TIME)

        # Concatenate the temporary DataFrame with the full DataFrame:
        _results = pd.concat(_pages)
        _results = _results.drop_duplicates(keep='first')
        _results = _results.reset_index()
        return _results
        
    def scrape(self, html_engine:str=DEFAULT_HTML_PARSER, map_engine:str=DEFAULT_GEOCODE_ENGINE, api_key:str=None):
        """Initialize the scraper with a URL from the results of a property
        search performed on www.rightmove.co.uk.

        Args:
            url (str): full HTML link to a page of rightmove search results.
            get_floorplans (bool): optionally scrape links to the individual
                floor plan images for each listing (be warned this drastically
                increases runtime so is False by default).
        """

        self.status_code, self.content = self.get_request(self.url)
        
        self.__log.info(f"Found {self.number_of_results} results in {self.number_of_pages} pages.")
        self.__log.info("Number of branches is : " + ", ".join([str(x) for x in self.number_of_batches]))
        
        _results = self.get_results(html_engine)
        self.__log.info('\n'.join(sorted([str(x) for x in _results['Hyperlink'].unique()])))
        _results = self.fix_results(_results)
        _results = self.enrich_results(_results, html_engine, map_engine, api_key)
        return _results
    '''