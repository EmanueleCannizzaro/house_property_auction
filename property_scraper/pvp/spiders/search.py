# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
import json
import os
from pydantic import ValidationError
import scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
import yaml

from property_scraper import LOCALHOST_URL_ROOTNAME, PVP_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.pvp.items import PVPSearchItem, PVPSearchModel
#from property_scraper.pvp.pipelines import get_location


@traced
@logged
class PVPSearchSpider(Spider):
    name = 'pvp_search'
    allowed_domains = ['pvp.giustizia.it']
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    
    WEBSITE = name.split('_')[0]

    def start_requests(self):
        rc_filename = os.path.join(os.path.expanduser('~'), 'property_scraper.json')
        with open(rc_filename, 'r') as f:
            key, subkey = self.name.split('_')
            URLS = json.load(f)[key][subkey]
            self.follow_links = True
            self.download_pages = True
            for url in URLS['searches']:
                yield scrapy.Request(URLS['root'] + url)

    def parse(self, response):
        url = response.url
        location = self.get_location(response.url)
        number_of_results = int(response.xpath('//span[@class="font-green"]/text()').extract_first().replace(' Annunci', ''))
        page_id = self.get_page_id(response.url)
        maximum_number_of_results_per_page = self.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

        if location:
            template = f"{ROOT_FOLDER}/{self.WEBSITE}/{self.name}_{location}.html"
        else:
            template = f"{ROOT_FOLDER}/{self.WEBSITE}/{self.name}.html"
        filename = get_unique_filename(template, self.search_datetime)
        basename = os.path.basename(filename)
        if LOCALHOST_URL_ROOTNAME not in url:
            if self.download_pages:
                self.to_html(filename, response)
            url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.WEBSITE, basename)
        else:
            url_localhost = url

        self.search = PVPSearchItem()
        self.items = self.search.items
        search_loader = ItemLoader(item=self.search)
        search_loader.add_value('basename', basename)
        search_loader.add_value('filename', filename)
        search_loader.add_value('id', os.path.splitext(basename)[0])
        search_loader.add_value('is_downloaded', False)
        search_loader.add_value('is_relative_href_fixed', False)
        search_loader.add_value('location', location)
        search_loader.add_value('number_of_results', number_of_results)
        search_loader.add_value('number_of_pages', number_of_pages)
        search_loader.add_value('number_of_results_per_page', number_of_results_per_page[page_id-1])
        search_loader.add_value('page_id', page_id)
        search_loader.add_value('response_status_code', 200)
        search_loader.add_value('spider_name', self.name)
        search_loader.add_value('url', url)
        search_loader.add_value('url_localhost', url_localhost)
        
        search_data = search_loader.load_item()
        
        try:
            search_model = PVPSearchModel(**search_data)
        except ValidationError as e:
            # Gestisci l'errore di validazione
            print(f"Errore di validazione: {e}")
        else:
            # Il dato è valido, puoi procedere con l'elaborazione
            print(search_model)
        
        yield search_data

        if self.follow_links:
            next_page = response.xpath('//li[contains(@class, "pull-right")]/a').attrib['href']
            if next_page is not None:
                yield response.follow(next_page, callback=self.parse)

    def to_html(self, filename:str, response):
        with open(filename, 'wb') as f:
            f.write(response.body)

    @staticmethod
    def get_location(s: str, prefix: str = 'localita='):
        location = None
        tokens = s.split('/')[-1].split('?')[-1].split('&')
        for token in tokens:
            if token.startswith(prefix):
                location = token[len(prefix):].lower()
                return location
        return location

    @staticmethod
    def get_page_id(s: str, prefix: str = 'frame4_item='):
        page_id = 1
        tokens = s.split('/')[-1].split('?')[-1].split('&')
        for token in tokens:
            if token.startswith(prefix):
                page_id = int(token[len(prefix):])
                return page_id
        return page_id

    @staticmethod
    def get_maximum_number_of_results_per_page(s: str, prefix: str = 'elementiPerPagina='):
        maximum_number_of_results_per_page = 50
        tokens = s.split('/')[-1].split('?')[-1].split('&')
        for token in tokens:
            if token.startswith(prefix):
                maximum_number_of_results_per_page = int(token[len(prefix):])
                return maximum_number_of_results_per_page
        return maximum_number_of_results_per_page

    @staticmethod
    def get_number_of_pages(number_of_results: int, maximum_number_of_results_per_page: int):
        number_of_pages = number_of_results // maximum_number_of_results_per_page
        if number_of_results % maximum_number_of_results_per_page > 0:
            number_of_pages += 1
        return number_of_pages

    @staticmethod
    def get_number_of_results_per_page(number_of_results: int, number_of_pages: int,
                                       maximum_number_of_results_per_page: int):
        if number_of_results == number_of_pages * maximum_number_of_results_per_page:
            number_of_results_per_page = [maximum_number_of_results_per_page] * number_of_pages
        else:
            number_of_results_per_page = [maximum_number_of_results_per_page] * (number_of_pages - 1) + [
                number_of_results % maximum_number_of_results_per_page]
        return number_of_results_per_page


if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = f'property_scraper.{PVPSearchSpider.WEBSITE}.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(PVPSearchSpider)

    # Start the crawler process    
    process.start()
