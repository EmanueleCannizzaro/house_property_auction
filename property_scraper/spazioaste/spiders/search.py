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
#from property_scraper.io import get_worksheet
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.astalegale.items import AstaLegaleItem


@traced
@logged
class SpazioAsteSearchSpider(SeleniumSearchSpider):
    name = 'spazioaste'
    allowed_domains = ['www.astalegale.net']
    start_urls = ['https://www.spazioaste.it/Immobili/Search']

    URL = 'https://www.spazioaste.it/Immobili/Search'
    LOGIN_URL = ''
    WEBSITE = 'spazioaste'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        #'cookie' : '//a[@class="cc-btn cc-dismiss"][contains(text(), "Accetto")]',
        #'email' : '//input[@name="Email"]',
        #'password' : '//input[@name="Password"]',
        #'remember' : '//input[@name="RememberMe"]',
        #'remember' : '//label[@for="RememberMe"]',
        #'login' : '//button[@class="cc-button cc-standard-button"][@id="btnModalLogin"][contains(text(), "Accedi")]'
    }
    LOGIN_ID = {
        #'email' : 'login-email',
        #'password' : 'login-password',        
        #<input name="RememberMe" type="hidden" value="false">
    }
    SEARCH_XPATH = {
        #'url' : '//button[@class="cc-button-search cc-button-search-primary we"][@id="btnSimpleSearchImmobili"][contains(text(), "Cerca")]',
        'cookie' : '//div[@class="cc-compliance"]/a[@class="cc-btn cc-dismiss"][contains(text(), "Accetto")]',
        'number_of_results' : '//p[@class="cc-results-text"][contains(text(), " risultati")]',
        'number_of_results_per_page' : '//article[@class="cc-item-grid"]',
        'scroll' : '//a[@class="app-btnNextPage cc-arrow cc-arrow-right"]'
    }
    SEARCH_SELECT = {
        #<input type="text" class="select-dropdown" readonly="true" data-activates="select-options-85c49809-90e7-a2b5-5014-915bb3882fa7" value="12">
        'number_of_results_per_page' : '//span[contains(text(), "120")]', #'//input[@value="12"][@class="select-dropdown"]',
        #wait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, ))).click()
        #<input type="text" class="select-dropdown" readonly="true" data-activates="select-options-eee91957-f2b4-fe30-232c-45277998a1e0" value="">
        #'sorting_criteria' : '//input[@value="Pubblicazione: più recente"][@class="select-dropdown"]',
    }
    
    @staticmethod
    def get_number_of_results(element):
        return element.text.strip().split(' ')[0]

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
