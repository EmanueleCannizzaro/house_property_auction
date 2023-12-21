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

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER #, get_filename_from_identifier, get_unique_filename
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.io import get_worksheet
from property_scraper.guber.items import GuberItem


#def get_page_id(s:str, prefix:str='p='):
#    page_id = 1
#    tokens = s.split('/')[-1].split('?')[-1].split('&')
#    for token in tokens:
#        if token.startswith(prefix):
#            page_id = int(token[len(prefix):])
#            #print(page_id)
#            return page_id
#    return page_id

'''
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

class GuberSearchSpider(SeleniumSearchSpider):
    name = 'guber_search'
    allowed_domains = ['immobiliare.guber.it']
    start_urls = [
        'https://immobiliare.guber.it/Home'
    ]

    URL = 'https://immobiliare.guber.it/Home'
    LOGIN_URL = ''
    WEBSITE = 'guber'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        #'cookie' : '//div[@class="gx-cookie-accept"][contains(text(), "OK")]',
        #'email' : '//input[@name="username"]',
        #'password' : '//input[@name="password"]',
        #'login' : '//button[@class="form-btn submit-button"][contains(text(), "Login")]'
    }
    SEARCH_XPATH = {
        #'url' : '//div[@class="gx-motore-ricerca-submit"][contains(text(), "Cerca")]',
        'number_of_results' : '//h1[@class="page-header"][contains(text(), "Tutte le aste - ")]',
        'number_of_results_per_page' : '//div[@class="property span3"]',
        'scroll' : '//a[@class="tui-page-btn tui-next"]/span[@class="tui-ico-next"][contains(text(), "next")]',
        #'contract_type' : '//select[@class="gx-motore-ricerca-select-contratto"]'
    }

    @staticmethod
    def get_number_of_results(element):
        return element.text.replace('Tutte le aste - ', '').split(' ')[0]

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
        
        if 'https://immobiliare.guber.it/Home' in url:
            WebDriverWait(driver, self.TIMEOUT).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "page-header")
                )
            )
            sleep(self.TIMEOUT)

            soup = BeautifulSoup(driver.page_source, 'html.parser')

            #<h1 class="page-header" id="title-page-content">Ricerca con filtri - 330 immobili</h1>
            number_of_results = int(
                soup.find("h1", class_="page-header").get_text().replace('Tutte le aste - ', '').replace('Ricerca con filtri - ', '').replace(' immobili', '').strip())
            # print(number_of_results)
            #page_id = get_page_id(url)
            maximum_number_of_results_per_page = get_maximum_number_of_results_per_page(url)
            number_of_pages = get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
            number_of_results_per_page = get_number_of_results_per_page(number_of_results, number_of_pages,
                                                                        maximum_number_of_results_per_page)

            #template = f'{ROOT_FOLDER}/{self.name}/{self.name}.html'
            #filename = get_unique_filename(template, self.search_time)
            #rootname, extension = os.path.splitext(filename)
            #filename = f"{rootname}_{page_id}{extension}"
            filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{self.search_time}_{self.page_id:03}.html'
            self.to_html(filename, driver)
            self.page_id += 1

            for ix in range(1, number_of_pages):
                # https://resales.intrum.it/risultati-annunci/index.html?...#start-27
                #<a class="gx-button gx-next" href="javascript:;" onclick="gxAnnunciListaRender('A1422916-056C-47B3-8E6D-9FAB0333573A','',9,true,false)">&gt;</a>
                #element = driver.find_element(By.ID, "passwd-id")
                #element = driver.find_element(By.NAME, "passwd")
                element = driver.find_element(By.CLASS_NAME, 'tui-next')
                #element = driver.find_element(By.CSS_SELECTOR, "input#passwd-id")
                #element.click()
                #element.send_keys("\n")
                driver.execute_script("arguments[0].click();", element)                
                WebDriverWait(driver, self.TIMEOUT).until(
                    expected_conditions.presence_of_element_located(
                        (By.CLASS_NAME, "tui-next")
                    )
                )
                sleep(self.TIMEOUT)
                #print(driver.current_url)
                next_page = driver.current_url
                #next_page += f"&page_id={ix}#start-{9 * ix}"
                #next_page = self.start_urls[0] + f"&page_id={ix}#start-{9 * ix}"
                if next_page is not None:
                    filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{self.search_time}_{self.page_id:03}.html'
                    self.to_html(filename, driver)
                    self.page_id += 1

                    yield response.follow(next_page, callback=self.parse_selenium)
                    #yield scrapy.http.Request(url=next_page, callback=self.parse_selenium)

                    subsoup = BeautifulSoup(driver.page_source, 'html.parser')

                    urls = set()
                    for link in subsoup.find_all('a', href=True):
                        x = link['href']
                        if x.startswith('/Immobile/'):
                            _url = 'https://immobiliare.guber.it' + x
                            urls.add(_url)
                    print('\n'.join(urls))
                    urls_to_be_downloaded = set()
                    #keys = ['IDImmobile']
                    #root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
                    for _url in urls:
                        #_filename = get_filename_from_identifier(_url, keys, root)
                        property_id = _url.split('/')[-1]
                        _filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{property_id}.html'
                        if (not os.path.exists(_filename)) and \
                                not (_url.startswith('https://immobiliare.guber.it/Home')):
                            urls_to_be_downloaded.add(_url)
                    urls_to_be_downloaded = sorted(urls_to_be_downloaded)
                    print('\n'.join(urls_to_be_downloaded))
                    print(f"{len(urls_to_be_downloaded)} out of {len(urls)} must be downloaded!")
                    for _url in urls_to_be_downloaded:
                        yield response.follow(_url, callback=self.parse_selenium)
                #break

        elif 'https://immobiliare.guber.it/Immobile/' in url:
            WebDriverWait(driver, self.TIMEOUT).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "page-header")
                )
            )
            sleep(self.TIMEOUT)

            #keys = ['IDImmobile']
            property_id = url.split('/')[-1]
            filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{property_id}.html'
            self.to_html(filename, driver)

        #driver.execute_script('some script here')
        # and when you are done, you want to "refresh" the response
        #response = response.refresh()
        # Do some stuff with the response data
        #  e.g.,
        #print(response.request.meta['driver'].title)

        #print(filename)
        #self.to_html(filename, driver)
        #self.to_db(filename, response)
        #basename = os.path.basename(filename)

        driver.quit()


    def parse_result(self, response):

        # Finish by releasing the webdriver, so it can go back into the queue and be used by other requests        
        #response.release_driver()

        pass

        #with open('image.png', 'wb') as f:
        #    f.write(response.meta['screenshot'])

        
    def to_html(self, filename:str, driver):
        with open(filename, 'wb') as f:
            f.write(driver.page_source.encode('utf-8'))
