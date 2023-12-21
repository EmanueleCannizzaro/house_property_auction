# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
import json
import os
#import scrapy
from scrapy import Request, Selector, Spider
#from scrapy.http import HtmlResponse
#from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
#from scrapy.spiders import CrawlSpider, Rule
from selenium import webdriver
from tqdm.auto import tqdm
from urllib.parse import urljoin
import yaml

from property_scraper import LOCALHOST_URL_ROOTNAME, ASTAGIUDIZIARIA_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.astagiudiziaria.items import AstaGiudiziariaSearchPropertyItem, AstaGiudiziariaSearchPropertyModel
#from property_scraper.astagiudiziaria.pipelines import get_location
#from property_scraper.pvp.spiders.search_property import PVPSearchPropertySpider
from property_scraper.selenium.spiders.selenium import SeleniumSpider


@traced
@logged
class AstaGiudiziariaSearchPropertySpider(SeleniumSpider):
    name = 'astagiudiziaria_search_property'
    allowed_domains = ['www.astagiudiziaria.com', 'localhost:8000']
    total_urls = []
    total_urls_to_be_downloaded = []
    start_urls = [
        'http://localhost:8000/astagiudiziaria/astagiudiziaria_20230321015045_00.html',
        #'https://www.astagiudiziaria.com/inserzioni/procedura-sovra-indebitamento-rg-72023-gia-1182023-ceriale-sv-via-della-concordia-42-qre-scuole-seugenio-casa-indipendente-con-1068735#'
    ]
    
    def start_requests(self):
        self.follow_links = True
        self.download_pages = True
        self.is_first_page = True
        for url in self.start_urls:
            print(url)
            yield Request(url)
    '''
        with open(f'{self.name}_localhost.json') as f:
            URLS = json.load(f)
            self.follow_links = True
            self.download_pages = True
            for url in URLS['searches']:
                yield scrapy.Request(URLS['root'] + url)
    '''

    def parse(self, response):
        search_url = response.url
        self.driver.get(search_url)
        self.sleep()
        print(search_url)
        # Use Selenium to interact with the webpage
        # Extract data using Selenium
        # ...

        # Create a new Scrapy response using the source code obtained from Selenium
        body = self.driver.page_source
        #print(body)
        #_response = HtmlResponse(url, body=body, encoding='utf-8')
        selector = Selector(text=body.encode('utf-8'))

        # Process the response using Scrapy
        keys = []
        root = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name}"

        for card in selector.xpath('//div[@class="pure-u-1 pure-u-md-8-24"]/a/@href'):
            url = card.get()
            if url:
                if url.startswith('/'):
                    url = urljoin(ASTAGIUDIZIARIA_URL_ROOTNAME, url)
                #print(url)
                self.property = AstaGiudiziariaSearchPropertyItem()
                property_loader = ItemLoader(item=self.property, selector=card)
                for key in self.property.items['css'].keys():
                    property_loader.add_css(key, self.property.items['css'][key])
                for key in self.property.items['xpath'].keys():
                    property_loader.add_xpath(key, self.property.items['xpath'][key])
                filename = get_filename_from_identifier(url, keys, root)
                basename = os.path.basename(filename)
                if LOCALHOST_URL_ROOTNAME not in url:
                    url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.name.split('_')[0], basename)
                else:
                    url_localhost = url
                property_loader.add_value('basename', basename)
                property_loader.add_value('filename', filename)
                property_loader.add_value('id', os.path.splitext(basename)[0])
                property_loader.add_value('spider_name', self.name)
                property_loader.add_value('search_id', search_url)
                property_loader.add_value('url', url)
                property_loader.add_value('url_localhost', url_localhost)
                property_loader.add_value('is_downloaded', False)
                property_loader.add_value('is_relative_href_fixed', False)
                property_loader.add_value('response_status_code', 200)
                
                property_data = property_loader.load_item()
                #property_model = AstaGiudiziariaSearchPropertyModel(**property_data)
            
                yield property_data
                yield response.follow(url, callback=self.parse_property)
            #break

        if self.follow_links:
            properties = response.xpath('//div[@class="pure-u-1 pure-u-md-8-24"]/a')
            urls_to_be_downloaded = set()
            for property in properties:
                url = property.attrib['href']
                if url.startswith('/'):
                    url = urljoin(ASTAGIUDIZIARIA_URL_ROOTNAME, url)
                print(url)
                if url.startswith(ASTAGIUDIZIARIA_URL_ROOTNAME):
                    self.total_urls.append(url)
                    filename = get_filename_from_identifier(url, keys, root)
                    print(filename)
                    if (not os.path.exists(filename)):
                        self.__log.info(f"{url} -> {filename}")
                        urls_to_be_downloaded.add(url)
            urls_to_be_downloaded = sorted(urls_to_be_downloaded)
            self.total_urls = sorted(set(self.total_urls))
            self.total_urls_to_be_downloaded += urls_to_be_downloaded
            self.total_urls_to_be_downloaded  = sorted(set(self.total_urls_to_be_downloaded))
            #self.__log.info(f"{len(urls_to_be_downloaded)} out of {len(urls)} must be downloaded!")
            self.__log.info(f"Generally {len(self.total_urls_to_be_downloaded)} out of {len(self.total_urls)} must be downloaded!")
            for url in urls_to_be_downloaded:
                yield response.follow(url, callback=self.parse_property)

    def parse_property(self, response):
        url = response.url
        self.driver.get(url)
        if self.is_first_page: 
            self.sleep(5)
            self.is_first_page = False
        else:
            self.sleep()
        print(url)
        # Use Selenium to interact with the webpage
        # Extract data using Selenium
        # ...

        # Create a new Scrapy response using the source code obtained from Selenium
        body = self.driver.page_source
        #print(body)
        #_response = HtmlResponse(url, body=body, encoding='utf-8')
        selector = Selector(text=body.encode('utf-8'))

        #self.__log.info(response.url)
        keys = []
        root = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}_property"
        filename = get_filename_from_identifier(url, keys, root)
        self.__log.info(filename)
        if self.download_pages:
            if 'localhost' not in url:
                self.to_html(filename, response)
