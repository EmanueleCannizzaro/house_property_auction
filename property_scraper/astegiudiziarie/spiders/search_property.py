# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
#from datetime import datetime
from glob import glob
#from itemloaders.processors import TakeFirst
import json
import os
#import pandas as pd
import scrapy
from scrapy.loader import ItemLoader
from tqdm.auto import tqdm
from urllib.parse import urljoin
import yaml

from property_scraper import LOCALHOST_URL_ROOTNAME, ASTEGIUDIZIARIE_URL_ROOTNAME, ROOT_FOLDER #, get_filename_from_identifier, get_unique_filename
# from property_scraper.io import get_worksheet
from property_scraper.astegiudiziarie.items import AsteGiudiziarieSearchPropertyItem
#from property_scraper.astegiudiziarie.pipelines import get_location
from property_scraper.astegiudiziarie.spiders.search import AsteGiudiziarieSearchSpider
# from property_scraper.pvp_page import PVPPage
# from property_scraper.pvp_property import PVPProperty
# from property_scraper.pvp_scraper import PVPScraper


@traced
@logged
class AsteGiudiziarieSearchPropertySpider(AsteGiudiziarieSearchSpider):
    name = 'astegiudiziarie_search_property'
    allowed_domains = ['localhost:8000/astegiudiziarie', 'www.astegiudiziarie.it']
    total_urls = []
    total_urls_to_be_downloaded = []

    def start_requests(self):
        with open('astegiudiziarie.json') as f:
            URLS = json.load(f)
            self.follow_links = URLS['follow_links']
            self.download_pages = URLS['download_pages']
            for url in URLS['searches']:
                yield scrapy.Request(URLS['root'] + url)

    def parse(self, response):
                    
        keys = ['contentId']
        root = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}"
        
        for card in response.xpath('//div[@class="listing-item"]'):
            search_url = response.url
            url = card.css('a::attr(href)').get().strip()
            if url.startswith('/'):
                url = urljoin(ASTEGIUDIZIARIE_URL_ROOTNAME, url)
            self.total_urls.append(url)
            self.property = AsteGiudiziarieSearchPropertyItem()
            property_loader = ItemLoader(item=self.property, selector=card)
            for key in self.property.items['css'].keys():
                property_loader.add_css(key, self.property.items['css'][key])
            for key in self.property.items['xpath'].keys():
                property_loader.add_xpath(key, self.property.items['xpath'][key])
            filename = self.get_filename_from_identifier(url, root)
            basename = os.path.basename(filename)
            if LOCALHOST_URL_ROOTNAME not in url:
                url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.name.split('_')[0], basename)
            else:
                url_localhost = url
            property_loader.add_value('filename', filename)
            property_loader.add_value('basename', basename)
            property_loader.add_value('id', os.path.splitext(basename)[0])
            property_loader.add_value('spider_name', self.name)
            property_loader.add_value('search_id', search_url)
            property_loader.add_value('url', url)
            property_loader.add_value('url_localhost', url_localhost)
            property_loader.add_value('is_downloaded', False)
            property_loader.add_value('is_relative_href_fixed', False)
            property_loader.add_value('response_status_code', 200)
            yield property_loader.load_item()
            
        self.total_urls = sorted(set(self.total_urls))

        if self.follow_links:
            proxy_url = self.get_proxy_url()
            urls_to_be_downloaded = set()
            root = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}"
            for url in self.total_urls:                
                filename = self.get_filename_from_identifier(url, root)#, keys)
                #print(filename)
                if not os.path.exists(filename):
                    print(url, filename)
                    urls_to_be_downloaded.add(url)
            urls_to_be_downloaded = sorted(urls_to_be_downloaded)
            
            self.total_urls_to_be_downloaded += urls_to_be_downloaded
            self.total_urls_to_be_downloaded  = sorted(set(self.total_urls_to_be_downloaded))
            #print(f"{len(urls_to_be_downloaded)} out of {len(urls)} must be downloaded!")
            print(f"Generally {len(self.total_urls_to_be_downloaded)} out of {len(self.total_urls)} must be downloaded!")
            for url in urls_to_be_downloaded:
                #yield response.follow(_url, callback=self.parse_property)
                #yield scrapy.Request(URLS['root'] + url)
                yield scrapy.Request(url, meta={"proxy": proxy_url}, callback=self.parse_property)

    def parse_property(self, response):
        url = response.url
        print(url)
        root = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}"
        filename = self.get_filename_from_identifier(url, root) #, keys)
        print(filename)
        if self.download_pages:
            if 'localhost' not in url:
                self.to_html(filename, response)
