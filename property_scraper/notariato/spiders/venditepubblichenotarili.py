# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, TRACE, traced
from bs4 import BeautifulSoup
from datetime import datetime
import json
import os
import pandas as pd
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy_selenium import SeleniumRequest
from selenium.webdriver import Chrome, ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
#from urllib.parse import urljoin

from property_scraper import LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier #, get_unique_filename
from property_scraper.io import get_worksheet
from property_scraper.notariato.items import NotariatoItem


#def get_page_id(s:str, prefix:str='p='):
#    page_id = 1
#    tokens = s.split('/')[-1].split('?')[-1].split('&')
#    for token in tokens:
#        if token.startswith(prefix):
#            page_id = int(token[len(prefix):])
#            #print(page_id)
#            return page_id
#    return page_id

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


class VenditePubblicheNotariliSpider(scrapy.Spider):
    name = 'venditepubblichenotarili'
    allowed_domains = ['venditepubblichenotarili.notariato.it']
    start_urls = [
        'https://www.venditepubblichenotarili.notariato.it/ricerca-aste',
        #'https://www.venditepubblichenotarili.notariato.it/risultati_ricerca',
    ]
    
    TIMEOUT = 5  # ⚠ don't forget to set a reasonable timeout

    search_time = datetime.now().strftime("%Y%m%d%H%M%S")
    page_id = 1
    
    options = ChromeOptions()
    # #options.headless = True # False

    def parse(self, response):
        url = response.url
        

        driver = Chrome(executable_path='/home/emanuele/bin/chromedriver/111.0.5563.64/chromedriver',
                        options=self.options)
        driver.get(url)

        #<button class="btn btn-link" type="button">Ricerca avanzata</button>
        element = driver.find_element(By.CLASS_NAME, "btn-link")
        #element.click()
        driver.execute_script("arguments[0].click();", element)
        WebDriverWait(driver, self.TIMEOUT).until(
            expected_conditions.presence_of_element_located(
                (By.ID, "ricercaAvanzata")
            )
        )
        sleep(self.TIMEOUT)

        element = driver.find_element(By.ID, "ricercaAvanzata")
        element.click()
        driver.execute_script("arguments[0].click();", element)
        WebDriverWait(driver, self.TIMEOUT).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "avviso-item")
            )
        )
        sleep(self.TIMEOUT)
        
        #input class="custom-control-input" id="checkScaduti" name="checkScaduti" type="checkbox" value="true">
        element = driver.find_element(By.ID, "checkScaduti")
        element.click()
        driver.execute_script("arguments[0].click();", element)
        WebDriverWait(driver, self.TIMEOUT).until(
            expected_conditions.presence_of_element_located(
                (By.CLASS_NAME, "avviso-item")
            )
        )
        sleep(self.TIMEOUT)
        
        #row class="

        soup = BeautifulSoup(driver.page_source, 'html.parser')

        # number_of_results = int(response.xpath("//div[@class, 'gx-lista')]/text()").get().strip().replace('annunci in Italia', '').strip().replace('.', ''))
        #<div class="col-12 text-right">13814 Risultati trovati</div>
        
        number_of_results = int(soup.find_all(string=re.compile(' Risultati trovati')).get_text().replace(' Risultati trovati', '')) # .replace(' Annunci immobiliari', '').strip())
        print(number_of_results)
        return 
        
        #yield response.follow(url, callback=self.parse_selenium)
        #yield SeleniumRequest(url=url, callback=self.parse_selenium)

    def parse_selenium(self, response):
        url = response.url
        
        yield response.follow(url, callback=self.parse_selenium)
        #yield SeleniumRequest(url=url, callback=self.parse_selenium)

    def parse_selenium(self, response):
        url = response.url

        driver = Chrome(executable_path='/home/emanuele/bin/chromedriver/111.0.5563.64/chromedriver',
                        options=self.options)
        driver.get(url)
        #driver = response.request.meta['driver']
        
        if 'https://www.venditepubblichenotarili.notariato.it/risultati_ricerca' in url:
            #page_id = get_page_id(url)
            maximum_number_of_results_per_page = get_maximum_number_of_results_per_page(url)
            number_of_pages = get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
            number_of_results_per_page = get_number_of_results_per_page(number_of_results, number_of_pages,
                                                                        maximum_number_of_results_per_page)

            #template = f'{ROOT_FOLDER}/{self.name}/{self.name}_{self.search_time}_{self.page_id}.html'
            #filename = get_unique_filename(template, )
            #rootname, extension = os.path.splitext(filename)
            #filename = f"{rootname}_{self.page_id}{extension}"
            filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{self.search_time}_{self.page_id:05}.html'
            self.to_html(filename, driver)
            self.page_id += 1

            for ix in range(1, number_of_pages):
                
                
                # https://resales.intrum.it/risultati-annunci/index.html?...#start-27
                #<a class="gx-button gx-next" href="javascript:;" onclick="gxAnnunciListaRender('A1422916-056C-47B3-8E6D-9FAB0333573A','',9,true,false)">&gt;</a>
                #element = driver.find_element(By.ID, "passwd-id")
                #element = driver.find_element(By.NAME, "passwd")
                element = driver.find_element(By.CLASS_NAME, 'gx-next')
                #element = driver.find_element(By.CSS_SELECTOR, "input#passwd-id")
                #element.click()
                #element.send_keys("\n")
                driver.execute_script("arguments[0].click();", element)
                WebDriverWait(driver, self.TIMEOUT).until(
                    expected_conditions.presence_of_element_located(
                        (By.CLASS_NAME, "gx-lista")
                    )
                )
                sleep(self.TIMEOUT)
                #print(driver.current_url)
                next_page = driver.current_url
                #next_page += f"&page_id={ix}#start-{9 * ix}"
                #next_page = self.start_urls[0] + f"&page_id={ix}#start-{9 * ix}"
                if next_page is not None:
                    filename = f'{ROOT_FOLDER}/{self.name}/{self.name}_{self.search_time}_{self.page_id:05}.html'
                    self.to_html(filename, driver)
                    self.page_id += 1

                    yield response.follow(next_page, callback=self.parse_selenium)
                    #yield scrapy.http.Request(url=next_page, callback=self.parse_selenium)

                    subsoup = BeautifulSoup(driver.page_source, 'html.parser')

                    urls = set()
                    for link in subsoup.find_all('a', href=True):
                        x = link['href']
                        if x.startswith('/scheda-annuncio/index.html?IDImmobile='):
                            _url = 'https://resales.intrum.it' + x
                            urls.add(_url)
                    print('\n'.join(urls))
                    urls_to_be_downloaded = set()
                    #keys = ['IDImmobile']
                    #root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
                    for _url in urls:
                        #_filename = get_filename_from_identifier(_url, keys, root)
                        keys = ['IDImmobile']
                        root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
                        _filename = get_filename_from_identifier(_url, keys, root)
                        if (not os.path.exists(_filename)) and \
                                not (_url.startswith('https://resales.intrum.it/risultati-annunci/index.html?')):
                            urls_to_be_downloaded.add(_url)
                    urls_to_be_downloaded = sorted(urls_to_be_downloaded)
                    print('\n'.join(urls_to_be_downloaded))
                    print(f"{len(urls_to_be_downloaded)} out of {len(urls)} must be downloaded!")
                    for _url in urls_to_be_downloaded:
                        yield response.follow(_url, callback=self.parse_selenium)
                #if self.page_id > 4:
                #    break

        elif 'https://resales.intrum.it/scheda-annuncio/index.html' in url:
            #sleep(self.TIMEOUT)
            WebDriverWait(driver, self.TIMEOUT).until(
                expected_conditions.presence_of_element_located(
                    (By.CLASS_NAME, "gx-risultati-content")
                )
            )
            sleep(self.TIMEOUT)

            keys = ['IDImmobile']
            root = f'{ROOT_FOLDER}/{self.name}/{self.name}'
            filename = get_filename_from_identifier(url, keys, root)
            self.to_html(filename, driver)

        #driver.execute_script('some script here')
        # and when you are done, you want to "refresh" the response
        #response = response.refresh()
        # Do some stuff with the response data
        #  e.g.,
        #print(response.request.meta['driver'].title)

        print(filename)
        #self.to_html(filename, driver)
        #self.to_db(filename, response)
        basename = os.path.basename(filename)

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
