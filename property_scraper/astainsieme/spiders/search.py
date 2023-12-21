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
#from urllib.parse import urljoin

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.io import get_worksheet
from property_scraper.astainsieme.items import AstaInsiemeItem


class AstaInsiemeSearchSpider(SeleniumSearchSpider):
    name = 'astainsieme'
    allowed_domains = ['www.astainsieme.it']
    start_urls = [
        'https://www.astainsieme.it/IT/Immobili?tipovendita=AST&categ=RESID'
    ]

    URL = 'https://www.astainsieme.it/IT/Immobili?tipovendita=AST&categ=RESID'
    LOGIN_URL = ''
    NEXT_PAGE_URL = 'https://www.astainsieme.it/IT/Immobili?tipovendita=AST&categ=RESID&page={}'
    WEBSITE = 'astainsieme'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        'cookie' : '//button[@class="iubenda-cs-accept-btn iubenda-cs-btn-primary"][contains(text(), "Accetta")]',
        #'email' : '//input[@name="username"]',
        #'password' : '//input[@name="password"]',
        #'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    SEARCH_XPATH = {
        #'url' : '//div[@class="gx-motore-ricerca-submit"][contains(text(), "Cerca")]',
        'number_of_results' : '//div[@class="SearchResults"]/span',
        'number_of_results_per_page' : '//div[@class="ItemPreviewBox"]',
        #'scroll' : '//div[@class="PagingArrowDx"]/a',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }
    
    SEARCH_SELECT = {
        #'sorting_criteria' : '//ul[@class="dropdown-menu fullwidth"]/li[@class="ng-star-inserted"]/a[@class="dropdown-option"][contains(text(), "Latest Acquisitions")]',
    }

    def parse(self, response):
        location = None #self.scraper.get_location(response.url)
        number_of_results = int(response.xpath('//span[@class="font-green"]/text()').extract_first().replace(' Annunci', '')) 
        page_id = self.scraper.get_page_id(response.url)
        maximum_number_of_results_per_page = self.scraper.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.scraper.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.scraper.get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

        if location:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}_{location}.html'
        else:
            template = f'{ROOT_FOLDER}/{self.name}/{self.name}.html'
        filename = get_unique_filename(template)
        basename = os.path.basename(filename)
        self.to_html(filename, response)        
        #self.to_db(filename, response)
        basename = os.path.basename(filename)
                
        for url in response.xpath("//div[@class='pure-u1']/a"):
            l = ItemLoader(item=PVPItem(), selector=urls)
            l.add_xpath('hyperlink', "//a[@class='cardlink']::attrib('href')")
            yield l.load_item()
        
        next_page = None
        current_page_id = int(response.css('div.pagination').css('a.active::text').get())
        next_page_id = current_page_id + 1
        for url in response.css('div.pagination').css('a'):
            if url.css('a::text').get() == str(next_page_id):
                print(str(next_page_id))
                next_page = url
                break
        if next_page is not None:            
            yield response.follow(next_page, callback=self.parse)

    def parse_properties(self, response, number_of_results_per_page):
        pass

    def parse_property(self, response):
        keys = ['contentId']
        root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
        filename = get_filename_from_identifier(response.url, keys, root)        
        self.to_html(filename, response)        
        self.to_db(filename, response)
