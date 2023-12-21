# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
import json
import os
import pandas as pd
import scrapy
from scrapy.loader import ItemLoader
import shutil
#from urllib.parse import unquote, urlparse
import wget
import yaml

from property_scraper import PVP_URL_ROOTNAME #LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
#from property_scraper.io import get_worksheet
from property_scraper.pvp.items import PVPPropertyItem, PVPPropertyModel
#from property_scraper.pvp.pipelines import get_location
from property_scraper.pvp.spiders.search import PVPSearchSpider
from property_scraper.pvp_page import PVPPage
from property_scraper.pvp_property import PVPProperty
from property_scraper.pvp_scraper import PVPScraper


@traced
@logged
class PVPPropertySpider(PVPSearchSpider):
    name = 'pvp_property'
    allowed_domains = ['localhost:8000/pvp']

    def start_requests(self):
        with open(f'{self.name}_localhost.json') as f:
            URLS = json.load(f)
            self.follow_links = False
            self.download_pages = False
            for url in URLS['properties']:
                yield scrapy.Request(URLS['root'] + url)

    def parse(self, response):
        url = response.url
        url_localhost = url
        self.property = PVPPropertyItem()
        property_loader = ItemLoader(item=self.property, response=response)
        for key in self.property.items['css'].keys():
            property_loader.add_css(key, self.property.items['css'][key])
        for key in self.property.items['xpath'].keys():
            property_loader.add_xpath(key, self.property.items['xpath'][key])
        #property_loader.add_value('basename', basename)
        #property_loader.add_value('filename', filename)
        #property_loader.add_value('id', os.path.splitext(basename)[0])
        property_loader.add_value('is_downloaded', False)
        property_loader.add_value('is_relative_href_fixed', False)
        property_loader.add_value('response_status_code', 200)
        property_loader.add_value('spider_name', self.name)
        property_loader.add_value('url', url)
        property_loader.add_value('url_localhost', url_localhost)
        
        property_data = property_loader.load_item()
        property_model = PVPPropertyModel(**property_data)
        
        yield property_data
