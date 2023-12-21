# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from datetime import datetime
import json
import os
import pandas as pd
import scrapy
from scrapy.loader import ItemLoader
import shutil
from urllib.parse import unquote, urlparse
import wget
import yaml

from property_scraper import PVP_URL_ROOTNAME #LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.io import get_worksheet
from property_scraper.pvp.items import PropertyItem, SearchItem
from property_scraper.pvp.pipelines import get_location
from property_scraper.pvp.spiders.search import PVPSearchSpider
from property_scraper.pvp_page import PVPPage
from property_scraper.pvp_property import PVPProperty
from property_scraper.pvp_scraper import PVPScraper


@traced
@logged
class AsteGiudiziariePropertySpider(AsteGiudiziarieSearchSpider):
    name = 'astegiudiziarie_property'
    allowed_domains = ['localhost:8000/astegiudiziarie']

    def start_requests(self):
        with open('pvp.json') as f:
            URLS = json.load(f)
            self.follow_links = URLS['follow_links']
            self.download_pages = URLS['download_pages']
            for url in URLS['searches']:
                yield scrapy.Request(URLS['root'] + url)

    def start_requests(self):
        with open('pvp.json') as f:
            URLS = json.load(f)
            self.follow_links = URLS['follow_links']
            self.download_pages = URLS['download_pages']
            for url in URLS['searches']:
                yield scrapy.Request(URLS['root'] + url)

    def parse(self, response):
        self.property = PropertyItem()
        listing = response.xpath('//div[@class="si-listings-column"]')
        property_loader = ItemLoader(item=self.property, response=response, selector=listing)
        for key in self.property.items['css'].keys():
            property_loader.add_css(key, self.property.items['css'][key])
        for key in self.property.items['xpath'].keys():
            property_loader.add_xpath(key, self.property.items['xpath'][key])
        yield property_loader.load_item()

        for selector in response.xpath('//a/@href'):
            url = selector.get()
            if url.startswith(f"{PVP_URL_ROOTNAME}/pvp-resources/cms/documents/") and \
                    url.lower().endswith('.pdf'):
                basename = os.path.basename(unquote(urlparse(url).path))
                print(url, basename)
                ofilename = os.path.join('/home/git/property_scraper/www/pvp/documents', basename)
                if not os.path.exists(ofilename):
                    filename = wget.download(url)
                    shutil.move(filename, ofilename)

        for selector in response.xpath('//img/@src'):
            url = selector.get()
            if url.startswith('/'):
                url = urljoin(PVP_URL_ROOTNAME, url)
            if url.startswith(f"{PVP_URL_ROOTNAME}/pvp-resources/cms/images/") and \
                    url.lower().endswith('.png'):
                basename = os.path.basename(unquote(urlparse(url).path))
                print(url, basename)
                ofilename = os.path.join('/home/git/property_scraper/www/pvp/images', basename)
                if not os.path.exists(ofilename):
                    filename = wget.download(url)
                    shutil.move(filename, ofilename)
            else:
                print(url)
