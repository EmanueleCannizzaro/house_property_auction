# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from datetime import datetime
import os
from scrapy import Spider
from scrapy.loader import ItemLoader

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.astagiudiziaria.items import PVPSearchItem


@traced
@logged
class AstaGiudiziariaSearchSpider(SeleniumSearchSpider):

    name = 'astagiudiziaria_search'
    allowed_domains = ['www.astagiudiziaria.com']
    start_urls = [
        'https://www.astagiudiziaria.com/search?_token=7xRNRdqxoeIEav82a8wyNn3sdJrCdfjNS6VVlJeN&macrocategory=527&category=528&range=0&per_page=50'
        #'https://www.astagiudiziaria.com/search?_token=0akpMluAeB0KmIHBV0lh7dXDMdPnxa5Zhg2YtQ63&macrocategory=527&category=528&microcategory%5B0%5D=529&microcategory%5B1%5D=530&microcategory%5B2%5D=531&microcategory%5B3%5D=532&microcategory%5B4%5D=533&microcategory%5B5%5D=535&microcategory%5B6%5D=536&microcategory%5B7%5D=537&microcategory%5B8%5D=538&microcategory%5B9%5D=539&microcategory%5B10%5D=540&microcategory%5B11%5D=543&range=0&aste_passate=on&per_page=50&page=1'
    ]
    follow_links = False
    download_pages = True
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    URL = 'https://www.astagiudiziaria.com/myAsta/home'
    LOGIN_URL = 'https://www.astagiudiziaria.com/myAsta/login'
    WEBSITE = 'astagiudiziaria'
    LOGIN_XPATH = {
        'advertisement': '//button[@class="remodal-close"]',
        'cookie' : '//button[@class="CybotCookiebotDialogBodyButton"][contains(text(), "Accetta selezionati")]',
        'email' : '//input[@name="username"]',
        'password' : '//input[@name="password"]',
        'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    LOGIN_ID = {
    }
    SEARCH_XPATH = {
        'url' : '//li[@class="tab-link-myasta"][contains(text(), "I tuoi risultati")]',
        'number_of_results' : '//p[@class="total-string"][contains(text(), "Numero di risultati: ")]',
        'number_of_results_per_page' : '//div[@class="pure-u-1 pure-u-md-6-24"]',
        'scroll' : '//i[@class="fa fa-angle-right"]'
    }

    #@staticmethod
    #def format_date(date):
    #    # Get the current date and format it to 'YYYY/MM/DD'
    #    today = date.strftime('%Y/%m/%d')
    #    return today
    
    @staticmethod
    def get_number_of_results(text:str):
        return text.replace('NUMERO DI RISULTATI: ', '').split(' ')[0]

    def parse(self, response):
        url = response.url
        location = 'italia' # self.get_location(response.url)
        number_of_results = int(response.xpath('//ul[@class="filter-search"]//strong/text()').get())  # .replace(' Annunci', ''))
        page_id = self.get_page_id(response.url)
        maximum_number_of_results_per_page = self.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

        if location:
            template = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}_{location}.html"
        else:
            template = f"{ROOT_FOLDER}/{self.name.split('_')[0]}/{self.name.split('_')[0]}.html"
        filename = get_unique_filename(template, self.search_datetime)
        basename = os.path.basename(filename)
        if LOCALHOST_URL_ROOTNAME not in url:
            if self.download_pages:
                self.to_html(filename, response)
            url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.name.split('_')[0], basename)
        else:
            url_localhost = url

        self.search = PVPSearchItem()
        properties = response.xpath('div[@class="pure-u-1 pure-u-md-8-24"]')
        for property in properties:
            search_loader = ItemLoader(item=self.search, response=response, selector=property)
            search_loader.add_value('filename', filename)
            search_loader.add_value('basename', basename)
            search_loader.add_value('id', os.path.splitext(basename)[0])
            search_loader.add_value('spider_name', self.name)
            search_loader.add_value('location', location)
            search_loader.add_value('page_id', page_id)
            search_loader.add_value('number_of_results', number_of_results)
            search_loader.add_value('number_of_pages', number_of_pages)
            search_loader.add_value('number_of_results_per_page', number_of_results_per_page[page_id-1])
            search_loader.add_value('url', url)
            search_loader.add_value('url_localhost', url_localhost)
            search_loader.add_value('is_downloaded', False)
            search_loader.add_value('is_relative_href_fixed', False)
            search_loader.add_value('response_status_code', 200)
            yield search_loader.load_item()

        #for url in response.xpath("//div[@class='pure-u1']/a"):
        #    l = ItemLoader(item=PVPItem(), selector=urls)
        #    l.add_xpath('hyperlink', "//a[@class='cardlink']::attrib('href')")
        #    yield l.load_item()
        
        current_page_id = int(response.xpath('//div[@class="pagination"]/a[@class="active"]/text()').get())
        next_page_id = current_page_id + 1
        xpath = f'//div[@class="pagination"]/a[contains(text(), {next_page_id})]'
        next_page = response.xpath(xpath)[0].attrib['href']
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
        # Rightmove will return a maximum of 42 results pages, hence:
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
