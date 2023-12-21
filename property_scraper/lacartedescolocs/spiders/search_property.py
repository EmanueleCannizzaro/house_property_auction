# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
import os
import scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
from time import sleep
#from tqdm.auto import tqdm

from property_scraper import ROOT_FOLDER
#from property_scraper import LOCALHOST_URL_ROOTNAME, PVP_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.infoencheres.items import InfoEncheresSearchPropertyItem, InfoEncheresSearchPropertyModel


@traced
@logged
class InfoEncheresSearchPropertySpider(Spider):
    name = 'infoencheres_searchproperty'
    WEBSITE = name.split('_')[0]
    allowed_domains = ['www.info-encheres.com']
    start_urls = [
        'https://www.info-encheres.com/recherche.php?1=1&cat=1&snr=0&nbpage=100',
        #'https://www.info-encheres.com/vente-encheres-immobilieres-annonces.html'
    ]
    
    download_flag = True    
    is_first_page = True
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    def parse(self, response):
        if self.download_flag:
            response.meta['filename'] = 'download.html'
            self.to_html(response)
        
        if self.is_first_page == True:
            number_of_results = int(response.xpath('//b[contains(text(), "annonces")]/text()').extract_first().replace(' annonces', ''))
            print(f"The number of results is {number_of_results}.")
            page_id = self.get_page_id(response.url)
            print(f"The current page id is {page_id}.")
            maximum_number_of_results_per_page = self.get_maximum_number_of_results_per_page(response.url)
            print(f"The maximum number of results per page is {maximum_number_of_results_per_page}.")
            number_of_pages = self.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
            print(f"The search consists of {number_of_pages} pages.")
            number_of_results_per_page = self.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)
            print(f"The number of results per page is {number_of_results_per_page}.")
            self.is_first_page = False

            for ix in range(1, number_of_pages):
                next_page = self.get_next_page(ix)
                print(next_page)
                if next_page is not None:
                    #filename = os.path.join(ROOT_FOLDER, self.WEBSITE, f'{self.WEBSITE}_search__{ix:06}.html')
                    #yield scrapy.Request(url=next_page, callback=self.parse, meta={'filename': filename})
                    yield response.follow(next_page, callback=self.parse)
                    sleep(1)
        
        for card in response.xpath('//table[@class="liste"]/tr'):
            self.property = InfoEncheresSearchPropertyItem()
            property_loader = ItemLoader(item=self.property, selector=card)
            for key in self.property.items['css'].keys():
                property_loader.add_css(key, self.property.items['css'][key])
            for key in self.property.items['xpath'].keys():
                property_loader.add_xpath(key, self.property.items['xpath'][key])
            
            property_data = property_loader.load_item()
            
            if property_loader.get_collected_values('ref'):
                property_ref = property_data['ref']
                property_url = property_data['url'][-1]
                filename = os.path.join(ROOT_FOLDER, self.WEBSITE, f'{self.WEBSITE}_property_{property_ref}.html')
                print(property_ref, property_url, filename)
                if not os.path.exists(filename):
                    # Pass the filename as a meta argument to the save_page function
                    yield scrapy.Request(url=property_url, callback=self.to_html, meta={'filename': filename})
            
                #property_model = InfoEncheresSearchPropertyModel(**property_data)
                yield property_data
                #break

    def to_html(self, response):
        # Retrieve the filename from the meta arguments
        filename = response.meta['filename']

        # Save the response body to the specified filename
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.__log.info(f'Saved page {response.url} as {filename}.')

    def get_next_page(self, ix:int):
        _next_page = self.start_urls[0].replace('&snr=0', f'&snr={ix}')
        return _next_page

    @staticmethod
    def get_page_id(s:str, prefix:str='snr='):
        page_id = 1
        tokens = s.split('/')[-1].split('?')[-1].split('&')
        for token in tokens:
            if token.startswith(prefix):
                page_id = int(token[len(prefix):])
                return page_id
        return page_id

    @staticmethod
    def get_maximum_number_of_results_per_page(s:str, prefix:str='nbpage='):
        maximum_number_of_results_per_page = 100
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
    settings_module_path = 'property_scraper.infoencheres.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(InfoEncheresSearchPropertySpider)

    # Start the crawler process    
    process.start()
