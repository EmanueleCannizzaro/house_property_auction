# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import pandas as pd
import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
#from urllib.parse import urljoin

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER #, get_unique_filename #, get_filename_from_identifier
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.io import get_worksheet
from property_scraper.prelios.items import BlinksItem

'''
def get_page_id(s:str, prefix:str='p='):
    page_id = 1
    tokens = s.split('/')[-1].split('?')[-1].split('&')
    for token in tokens:
        if token.startswith(prefix):
            page_id = int(token[len(prefix):])
            #print(page_id)
            return page_id
    return page_id

def get_maximum_number_of_results_per_page(s:str, prefix:str='elementiPerPagina='):
    maximum_number_of_results_per_page = 9
    return maximum_number_of_results_per_page

def get_number_of_pages(number_of_results:int, maximum_number_of_results_per_page:int):
    number_of_pages = number_of_results // maximum_number_of_results_per_page
    if number_of_results % maximum_number_of_results_per_page > 0:
        number_of_pages += 1
    return number_of_pages

def get_number_of_results_per_page(number_of_results:int, number_of_pages:int, maximum_number_of_results_per_page:int):
    if number_of_results == number_of_pages * maximum_number_of_results_per_page:
        number_of_results_per_page = [maximum_number_of_results_per_page] * number_of_pages
    else:
        number_of_results_per_page = [maximum_number_of_results_per_page] * (number_of_pages - 1) + [number_of_results % maximum_number_of_results_per_page]
    return number_of_results_per_page    
'''

class BlinksSearchSpider(SeleniumSearchSpider):
    name = 'blinks'
    allowed_domains = ['blinksre.prelios.com']
    start_urls = [
        'https://blinksre.prelios.com/re/tipologia-living/luogo-nazione-italia/contratto-asta/',
        'https://blinksre.prelios.com/re/tipologia-living/luogo-nazione-italia/contratto-vendita/',
    ]

    URL = 'https://blinksre.prelios.com/re/tipologia-living/luogo-nazione-italia/'
    LOGIN_URL = ''
    WEBSITE = 'blinks'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        'cookie' : '//button[@class="fc-button fc-cta-consent fc-primary-button"]/p[@class="fc-button-label"][contains(text(), "Acconsento")]',
        #'email' : '//input[@name="username"]',
        #'password' : '//input[@name="password"]',
        #'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    SEARCH_XPATH = {
        'url' : '//button[@class="fc-button fc-cta-consent fc-primary-button"]',
        'number_of_results' : '//h1[@class="font-weight-extrabold text-white w-100 f-20 f-md-24 px-15 px-sm-0 m-0"][contains(text(), " annunci: living Italia")]',
        'number_of_results_per_page' : '//article[@class="insertion pointer mb-15 mb-15 col-md-4"]',
        'scroll' : '//li[@class="list-inline-item pagination-arrow page"][contains(text(), ">")]',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }

    @staticmethod
    def get_number_of_results(element):
        return element.text.split(' ')[0]

    def parse(self, response): 
        url = response.url
        
        yield response.follow(url, callback=self.parse_selenium)
        #yield SeleniumRequest(url=url, callback=self.parse_selenium)

    def parse_selenium(self, response):
        url = response.url
        
        driver = Chrome(executable_path='/home/emanuele/bin/chromedriver/111.0.5563.64/chromedriver',
                        options=self.options)
        driver.get(url)
        #driver = response.request.meta['driver']
        
        if 'https://blinksre.prelios.com/re/tipologia-living/luogo-nazione-italia/' in url:
            WebDriverWait(driver, self.TIMEOUT).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "pagination")
                )
            )
            sleep(self.TIMEOUT)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            tokens = url.split('/')
            if tokens[-1] == '':
                tokens = tokens[:-1]
            print(len(tokens), tokens)
            if len(tokens) == 7:
                property_type = tokens[-3]
                location = tokens[-2]
                sale_type = tokens[-1]

            #<h1 class="font-weight-extrabold text-white w-100 f-20 f-md-24 px-15 px-sm-0 m-0">1.463 annunci: Italia</h1>
            #number_of_results = int(response.xpath("//h1[contains(text(), 'annunci')]/text()").get().replace('annunci in Italia', '').replace(' annunci in asta: living Italia', '').replace('.', '').strip())
            _tags = soup.find_all("h1")
            for _tag in _tags:
                if 'annunci' in _tag.get_text():
                    _text = _tag.get_text()
                    break
            number_of_results = int(_text.replace('annunci in Italia', '').replace(' annunci in asta: living Italia', '').replace(' annunci in vendita: living Italia', '').replace('.', '').strip())
            page_id = get_page_id(response.url)
            maximum_number_of_results_per_page = get_maximum_number_of_results_per_page(response.url)
            number_of_pages = get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
            number_of_results_per_page = get_number_of_results_per_page(number_of_results, number_of_pages, maximum_number_of_results_per_page)

            filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{property_type}_{sale_type}_{location}_{self.search_time}_{page_id:05}.html'            
            self.to_html(filename, driver)        
            
            for ix in range(1, number_of_pages):
                #https://blinksre.prelios.com/re/luogo-nazione-italia/?p=2
                _url = url.split('?')[0] + f"?p={ix+1}"
                driver.get(_url)
                next_page = driver.current_url
                #print(next_page)
                if next_page is not None:                    
                    page_id = get_page_id(next_page)
                    
                    tokens = url.split('/')
                    if tokens[-1] == '':
                        tokens = tokens[:-1]
                    print(len(tokens), tokens)
                    if len(tokens) == 7:
                        property_type = tokens[-3]
                        location = tokens[-2]
                        sale_type = tokens[-1]

                    filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{property_type}_{sale_type}_{location}_{self.search_time}_{page_id:05}.html'
                    self.to_html(filename, driver)        
                    
                    #yield response.follow(next_page, callback=self.parse_selenium)
                    
                    subsoup = BeautifulSoup(driver.page_source, 'html.parser')

                    urls = set()
                    for link in subsoup.find_all('a', href=True):
                        x = link['href']
                        if x.startswith('https://blinksre.prelios.com/re/'):
                            _url = x
                            urls.add(_url)
                    print('\n'.join(urls))
                    urls_to_be_downloaded = set()
                    #keys = ['IDImmobile']
                    #root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
                    for _url in urls:
                        #_filename = get_filename_from_identifier(_url, keys, root)
                        #keys = ['IDImmobile']
                        #root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
                        #_filename = get_filename_from_identifier(_url, keys, root)
                        property_id = _url.split('/')[-1]
                        _filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{property_id}.html'
                        if (not os.path.exists(_filename)) and \
                                not (_url.startswith('https://blinksre.prelios.com/re/tipologia-living/luogo-nazione-italia/')):
                            urls_to_be_downloaded.add(_url)
                    urls_to_be_downloaded = sorted(urls_to_be_downloaded)
                    print('\n'.join(urls_to_be_downloaded))
                    print(f"{len(urls_to_be_downloaded)} out of {len(urls)} must be downloaded!")
                    for _url in urls_to_be_downloaded:
                        yield response.follow(_url, callback=self.parse_selenium)
                    
                #if page_id > 4:
                #    break

        elif 'https://blinksre.prelios.com/re/' in url:
            WebDriverWait(driver, self.TIMEOUT).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "price")
                )
            )
            sleep(self.TIMEOUT)

            property_id = url.split('/')[-1]
            filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{property_id}.html'
            self.to_html(filename, driver)

        #self.to_db(filename, response)
        #basename = os.path.basename(filename)

        driver.quit()

    def to_html(self, filename:str, driver):
        with open(filename, 'wb') as f:
            f.write(driver.page_source.encode('utf-8'))
