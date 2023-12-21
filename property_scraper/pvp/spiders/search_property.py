# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
import json
import os
import scrapy
#from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
#from scrapy.spiders import CrawlSpider, Rule
from tqdm.auto import tqdm
from urllib.parse import urljoin
import yaml

from property_scraper import LOCALHOST_URL_ROOTNAME, PVP_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.pvp.items import PVPSearchPropertyItem, PVPSearchPropertyModel
#from property_scraper.pvp.pipelines import get_location
from property_scraper.pvp.spiders.search import PVPSearchSpider


@traced
@logged
class PVPSearchPropertySpider(PVPSearchSpider):
    name = 'pvp_search_property'
    allowed_domains = ['pvp.giustizia.it', 'localhost:8000']
    total_urls = []
    total_urls_to_be_downloaded = []
    
    WEBSITE = name.split('_')[0]

    def start_requests(self):
        with open(f'{self.name}_localhost.json') as f:
            URLS = json.load(f)
            self.follow_links = True
            self.download_pages = True
            for url in URLS['searches']:
                yield scrapy.Request(URLS['root'] + url)

    def parse(self, response):
        keys = ['contentId']
        root = f"{ROOT_FOLDER}/{self.WEBSITE}/{self.name}"

        for card in response.xpath('//div[@class="col-md-12 tile-dettaglio bg-white"]'):
            search_url = response.url
            url = card.css('a::attr(href)').get().strip()
            if url.startswith('/'):
                url = urljoin(PVP_URL_ROOTNAME, url)
            self.property = PVPSearchPropertyItem()
            property_loader = ItemLoader(item=self.property, selector=card)
            for key in self.property.items['css'].keys():
                property_loader.add_css(key, self.property.items['css'][key])
            for key in self.property.items['xpath'].keys():
                property_loader.add_xpath(key, self.property.items['xpath'][key])
            filename = get_filename_from_identifier(url, keys, root)
            basename = os.path.basename(filename)
            if LOCALHOST_URL_ROOTNAME not in url:
                url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.WEBSITE, basename)
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
            property_model = PVPSearchPropertyModel(**property_data)
        
            yield property_data

        if self.follow_links:
            properties = response.xpath('//div[@class="anagrafica-risultato" or @class="col-xs-12 relative"]//a')
            urls_to_be_downloaded = set()
            for property in properties:
                url = property.attrib['href']
                if url.startswith('/'):
                    url = urljoin(PVP_URL_ROOTNAME, url)
                if url.startswith(PVP_URL_ROOTNAME):
                    self.total_urls.append(url)
                    filename = get_filename_from_identifier(url, keys, root)
                    if (not os.path.exists(filename)) and \
                        not (url.startswith(f'{PVP_URL_ROOTNAME}/{self.WEBSITE}/it/risultati_ricerca.page?') or \
                             url.startswith(f'{PVP_URL_ROOTNAME}/{self.WEBSITE}/en/risultati_ricerca.page?')):
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
        self.__log.info(url)
        keys = ['contentId']
        root = f"{ROOT_FOLDER}/{self.WEBSITE}/{self.WEBSITE}_property"
        filename = get_filename_from_identifier(url, keys, root)
        self.__log.info(filename)
        if self.download_pages:
            if 'localhost' not in url:
                self.to_html(filename, response)


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = f'property_scraper.{PVPSearchPropertySpider.WEBSITE}.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(PVPSearchPropertySpider)

    # Start the crawler process    
    process.start()
