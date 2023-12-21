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

from property_scraper import LOCALHOST_URL_ROOTNAME, RECROWD_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.recrowd.items import RecrowdMyAccountItem, RecrowdMyAccountModel
#from property_scraper.pvp.pipelines import get_location


@traced
@logged
class RecrowdMyAccountSpider(SeleniumSearchSpider):
    name = 'recrowd_account'
    allowed_domains = ['www.recrowd.com']
    start_urls = [
        'https://www.recrowd.com/it/area-privata/ricarica-o-ritira'
    ]
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    URL = 'https://www.recrowd.com/it/area-privata/ricarica-o-ritira'
    LOGIN_URL = 'https://www.recrowd.com/it/accedi'
    #NEXT_PAGE_URL = ''
    WEBSITE = name.split('_')[0]
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        'cookie' : '//a[@id="CybotCookiebotDialogBodyLevelButtonLevelOptinDeclineAll"][contains(text(), "Usa solo i cookie necessari")]',
        'email' : '//input[@name="username"]',
        'password' : '//input[@name="password"]',
        'login' : '//p[@id="login-from-submit"][contains(text(), "LOGIN")]'
    }
    SEARCH_XPATH = {
        #'url' : '//div[@class="gx-motore-ricerca-submit"][contains(text(), "Cerca")]',
        #'number_of_results' : '//span[@class="gold me-1"][position()=1]',
        #'number_of_results_per_page' : '//div[@class="col-lg-4 col-12 col-md-6 ng-star-inserted"]',
        #'scroll' : '//ul[@class="pagination"]/li/a[contains(text(), ">")]',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }
    
    SEARCH_SELECT = {
        'number_of_results_per_page' : '//ul[@class="dropdown-menu fullwidth"]/li[@class="dropdown-option ng-star-inserted"][contains(text(), "102 Per page")]',
        'sorting_criteria' : '//ul[@class="dropdown-menu fullwidth"]/li[@class="ng-star-inserted"]/a[@class="dropdown-option"][contains(text(), "Latest Acquisitions")]',
    }

    def parse(self, response):
        url = response.url
        location = self.get_location(response.url)
        number_of_results = int(response.xpath('//span[@class="font-green"]/text()').extract_first().replace(' Annunci', ''))
        page_id = self.get_page_id(response.url)
        maximum_number_of_results_per_page = self.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

        if location:
            template = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name}_{location}.html"
        else:
            template = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name}.html"
        filename = get_unique_filename(template, self.search_datetime)
        basename = os.path.basename(filename)
        if LOCALHOST_URL_ROOTNAME not in url:
            if self.download_pages:
                self.to_html(filename, response)
            url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.name.split('_')[0], basename)
        else:
            url_localhost = url

        self.search = RecrowdSearchItem()
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
            search_model = RecrowdSearchModel(**search_data)
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
    settings_module_path = 'property_scraper.recrowd.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(RecrowdMyAccountSpider)

    # Start the crawler process    
    process.start()
