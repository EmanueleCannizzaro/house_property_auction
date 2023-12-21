# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
#import json
import os
import scrapy
from scrapy import Spider
#from scrapy.loader import ItemLoader
from urllib.parse import urljoin
#import yaml

from property_scraper import LICITOR_URL_ROOTNAME, ROOT_FOLDER
#LOCALHOST_URL_ROOTNAME, PVP_URL_ROOTNAME, get_filename_from_identifier, get_unique_filename
from property_scraper.licitor.items import LicitorSearchPropertyItem, LicitorSearchPropertyModel


@traced
@logged
class LicitorSearchPropertySpider(Spider):
    name = 'licitor_searchproperty'
    WEBSITE = name.split('_')[0]
    allowed_domains = ['www.licitor.com']
    start_urls = [
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/bretagne-grand-ouest/prochaines-ventes.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/regions-du-nord-est/prochaines-ventes.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/paris-et-ile-de-france/prochaines-ventes.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/centre-loire-limousin/prochaines-ventes.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/sud-est-mediterrannee/prochaines-ventes.html',
        'https://www.licitor.com/ventes-aux-encheres-immobilieres/sud-ouest-pyrenees/prochaines-ventes.html',
    ]
    
    follow_links = True
    download_flag = True    
    is_first_page = True
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
        
    def parse(self, response):
        if self.download_flag:
            response.meta['filename'] = 'download.html'
            self.to_html(response)
        
        #if self.is_first_page == True:
        if response.url in self.start_urls:
            self.number_of_results = int(response.xpath('//span[@class="CountTotal"]/em/text()').extract_first().split(' ')[0])
            print(self.number_of_results)
            self.number_of_pages = int(response.xpath('//span[@class="PageTotal"]/text()').extract_first())
            print(self.number_of_pages)
            #self.is_first_page = False            
            
            if self.follow_links:
                for ix in range(2, self.number_of_pages+1):
                    next_page =  f'{response.url}?p={ix}'
                    print(next_page)
                    if next_page is not None:
                        yield response.follow(next_page, callback=self.parse)
                    #"/annonce/09/56/27/vente-aux-encheres/un-immeuble/landerneau/finistere/095627.html
                    #<article id="zone-list" class="Results">
                    #//a class="Next PageNav" href="/ventes-aux-encheres-immobilieres/bretagne-grand-ouest/prochaines-ventes.html?p=5
                    #'//div[@class="Container"]/ul[@class="AdResults"]//li/a[@class="Ad First"]/href'
                    #<a class="Ad" href="/annonce/09/58/52/vente-aux-encheres/parts-sociales-de-la-sci-du-7-place-notre-dame/vannes/morbihan/095852.html" title="Parts sociales de la SCI DU 7 PLACE NOTRE DAME, Vannes, Morbihan">
                    #<a class="Ad" href="/annonce/09/57/51/vente-aux-encheres/un-immeuble-bati/guidel/morbihan/095751.html" title="Un immeuble bâti, Guidel, Morbihan">
                    #<a class="Ad" href="/annonce/09/57/52/vente-aux-encheres/un-batiment-a-usage-d-entrepot-et-d-habitation/inzinzac-lochrist/morbihan/095752.html" title="Un bâtiment à usage d'entrepôt et d'habitation, Inzinzac-Lochrist, Morbihan">
                    #<a class="Ad" href="/annonce/09/58/61/vente-aux-encheres/un-batiment/la-trinite-sur-mer/morbihan/095861.html" title="Un bâtiment, La Trinité-sur-Mer, Morbihan">
                    #for card in response.xpath('//div[@class="Container"]/ul[@class="AdResults"]/li/a[@class="Ad"]/href'):

        if self.follow_links:
            for card in response.xpath('//ul[@class="AdResults"]/li/a/@href'):
                #next_page =  #.attrib['href']
                property_url = urljoin(LICITOR_URL_ROOTNAME, card.extract())
                print(property_url)
                if property_url is not None:
                    filename = os.path.join(ROOT_FOLDER, self.WEBSITE, f'{self.WEBSITE}_property_{os.path.basename(property_url)}')
                    if not os.path.exists(filename):
                        # Pass the filename as a meta argument to the save_page function
                        yield scrapy.Request(url=property_url, callback=self.to_html, meta={'filename': filename})

        '''        
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

        self.search = LicitorSearchItem()
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
        #search_model = LicitorSearchModel(**search_data)        
        yield search_data
        '''


        '''        
        for card in response.xpath('//table[@class="liste"]/tr'):
            self.property = LicitorSearchItem()
            property_loader = ItemLoader(item=self.property, selector=card)
            for key in self.property.items['css'].keys():
                property_loader.add_css(key, self.property.items['css'][key])
            for key in self.property.items['xpath'].keys():
                property_loader.add_xpath(key, self.property.items['xpath'][key])
            
            property_data = property_loader.load_item()
            #property_model = LicitorSearchModel(**property_data)
            yield property_data
            break
        '''
        
    def to_html(self, response):
        # Retrieve the filename from the meta arguments
        filename = response.meta['filename']

        # Save the response body to the specified filename
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.__log.info(f'Saved page {response.url} as {filename}.')

    '''
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
    '''

if __name__ == '__main__':
    from scrapy.crawler import CrawlerProcess
    from scrapy.settings import Settings
    from scrapy.utils.log import configure_logging
    
    #logging.disable(logging.CRITICAL)
    configure_logging()
    
    # Load the settings file
    settings = Settings()
    settings_module_path = 'property_scraper.licitor.settings'
    # Replace with your actual settings module path
    settings.setmodule(settings_module_path)

    # Create a crawler process with the loaded settings
    process = CrawlerProcess(settings)

    # Add your spider(s) to the crawler process
    process.crawl(LicitorSearchPropertySpider)

    # Start the crawler process    
    process.start()
