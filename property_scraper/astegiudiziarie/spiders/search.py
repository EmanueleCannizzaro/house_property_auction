# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
from json import dump, load
import os
import pandas as pd
import scrapy
from scrapy import Spider
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions #, Firefox, FirefoxOptions
#from selenium.webdriver.chrome.options import Options
#from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from tqdm.auto import tqdm
#import unittest
#from webdriver_manager.chrome import ChromeDriverManager
#from webdriver_manager.firefox import FirefoxDriverManager

from property_scraper import DRIVER_PATH, LOCALHOST_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.selenium.spiders.selenium import SeleniumSearchSpider
from property_scraper.astegiudiziarie.items import AsteGiudiziarieSearchPropertyItem
from property_scraper.pvp.items import PVPSearchItem
from property_scraper.pvp.spiders.search import PVPSearchSpider


GENERAL_PAUSE_TIME = 5
NUMBER_OF_SCROLLS = 100
URL_ROOTNAME = 'https://www.astegiudiziarie.it' #/User/RicercheSalvate#'

@traced
@logged
class AsteGiudiziarieSearchSpider(SeleniumSearchSpider):
    name = 'astegiudiziarie_search'
    allowed_domains = ['www.astegiudiziarie.it']
    start_urls = [
        f"{URL_ROOTNAME}/aste-giudiziarie/immobili/"
    ]
        
    URL = 'https://www.astegiudiziarie.it/Immobili/Ricerca-avanzata'
    LOGIN_URL = 'https://www.astegiudiziarie.it/User/Login?redirectUrl=/'
    WEBSITE = 'astegiudiziarie'
    LOGIN_XPATH = {
        #'advertisement': '//button[@class="remodal-close"]',
        'cookie' : '//div[@id="btn-cookie-policy"]/span[@id="btn-accept-text"][contains(text(), "Accetta")]',
        'email' : '//input[@name="txtUsername"]',
        'password' : '//input[@name="txtPassword"]',
        #'remember' : '//input[@name="RememberMe"]',
        'remember' : '//div[@class="checkbox form-group"][contains(text(), "Resta connesso")]/input[@id="rememberMe"]',
        'login' : '//button[@class="button btn-default"][contains(text(), "Accedi come utente")]'
    }
    LOGIN_ID = {
        #'email' : 'login-email',
        #'password' : 'login-password',        
        #<input name="RememberMe" type="hidden" value="false">
    }
    SEARCH_XPATH = {
        'url' : '//button[@id="btn_cerca_1"][contains(text(), "Cerca")]',
        'number_of_results' : '//span[@class="results_number"]',
        'number_of_results_per_page' : '//div[@class="listing-item"]',
        'scroll' : '//a[@class="app-btnNextPage cc-arrow cc-arrow-right"]'
    }
    SEARCH_ID = {
        'date_from' : 'venditaDal_1',
        'date_to' : 'venditaAl_1' 
    }
    SEARCH_SELECT = {
        #<input type="text" class="select-dropdown" readonly="true" data-activates="select-options-85c49809-90e7-a2b5-5014-915bb3882fa7" value="12">
        #'number_of_results_per_page' : '//input[@value="12"][@class="select-dropdown"]',
        #<input type="text" class="select-dropdown" readonly="true" data-activates="select-options-eee91957-f2b4-fe30-232c-45277998a1e0" value="">
        #'sorting_criteria' : '//input[@value="Pubblicazione: più recente"][@class="select-dropdown"]',
    }
    SEARCH_TYPE = 'single page'
    SCROLL_CONTAINER = 'fs-content'
    
    @staticmethod
    def get_number_of_results(element):
        return element.get_attribute("textContent")

    #login_url = f'{URL_ROOTNAME}/User/Login?redirectUrl=/'
    follow_links = False
    download_pages = True
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")

    """
    def __init__(self):
        def init_driver(browser:str='Chrome'):
            '''
            Note that there are few bugs in this function and it works only with human interaction.    
            The user must select the top left menu and, when the page is loaded, the button "Ricerca avanzata".
            The user must then confirm the select date and when the search is performed it must scroll down manually to start the dynamic data loading process!    
            '''
        
            '''
            <input type="text" id="txtUsername" name="txtUsername" placeholder="EMAIL" required="required" class="form-control" style="margin: 0px 0px 15px;">
            <input type="password" id="txtPassword" name="txtPassword" placeholder="PASSWORD" required="required" class="form-control" style="margin: 0px 0px 15px;">
            <input type="checkbox" id="rememberMe">
            <button type="submit" id="btnLogin" name="btnLogin" class="button btn-default">Accedi come utente</button>
            '''
            if browser == 'Chrome':
                options = ChromeOptions()
                driver = Chrome(service=webdriver.chrome.service.Service(DRIVER_PATH), options=options)
                #driver = webdriver.Chrome(service=webdriver.chrome.service.Service(DRIVER_PATH), options=options)
                #driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))            
            elif browser == 'Firefox':
                #options = webdriver.firefox.options.Options()
                #driver = Chrome(service=webdriver.firefox.service.Service(DRIVER_PATH), options=options)
                raise ValueError(f"Browser {browser} is not implemented yet!")
            else:
                raise ValueError(f"Browser {browser} is not a valid option!")
            
            
            driver.get(self.login_url)
            driver.implicitly_wait(GENERAL_PAUSE_TIME)
            
            assert('Login - Astegiudiziarie.it' in driver.title)
            driver.wait = WebDriverWait(driver, 5)
            driver.maximize_window()
            return driver      

        @staticmethod
        def login(driver):
            with open(os.path.join(os.path.expanduser('~'), 'asteimmobiliari.json'), 'r') as f:
                credentials = load(f)['astegiudiziarie']
                element_email = driver.find_element(By.ID, "txtUsername") #By.NAME
                element_email.send_keys(credentials['email'])
                element_password = driver.find_element(By.ID, "txtPassword") #By.NAME
                element_password.send_keys(credentials['password'])
            driver.find_element(By.ID, "rememberMe").send_keys(Keys.SPACE)
            driver.find_element(By.ID, "btnLogin").send_keys(Keys.ENTER) #Keys.RETURN #By.NAME, 'btnLogin').click()
            driver.implicitly_wait(GENERAL_PAUSE_TIME) #sleep(GENERAL_PAUSE_TIME)
        
            # wait for the login to complete and the dashboard page to load
            WebDriverWait(self.driver, 10).until(
                EC.url_contains("dashboard")
            )

    
        # Initialise the  driver
        driver = init_driver()
        print(driver.current_url)
        
        login(driver)
        
        self.driver = driver
    """

    def start_requests(self):
        response = self.get_response()
        #yield response.follow(response, callback=self.parse)

    @staticmethod
    def get_proxy_url():
        with open(os.path.join(os.path.expanduser('~'), 'property_scraper.json'), 'r') as f:
            credentials = load(f)['geo.iproyal.com']
            user = credentials['user']
            password = credentials['password']
            server = credentials['server']
            port = credentials['port']
            country = credentials['country']
            region = credentials['region']
            
            proxy_url = f"http://{user}:{password}_{country}_{region}@{server}:{port}"
            
            return proxy_url

    @staticmethod
    def get_filename_from_identifier(url, root):
        return f"{root}_property_{os.path.basename(url)}.html"
    
    
    def get_response(self):            
        def scroll_down(driver, container):
            """A method for scrolling the page."""
            _element = driver.find_element(By.CLASS_NAME, container)
            element = driver.find_element(By.CLASS_NAME, 'button-load-more-results')
            # Get scroll height.
            last_height = driver.execute_script(f"return document.getElementsByClassName('{container}')[0].scrollHeight")
            counter = 0
            while True:
                # Scroll down to the bottom.
                driver.execute_script("arguments[0].scrollIntoView(true);", _element)
                #driver.execute_script("document.querySelector('button-load-more-results');")
                driver.execute_script("arguments[0].click();", element)
                sleep(5)
                driver.execute_script(f"arguments[0].scrollTo(0, document.getElementsByClassName('{container}')[0].scrollHeight);", _element)
                # Wait to load the page.
                sleep(SCROLL_PAUSE_TIME)
                # Calculate new scroll height and compare with last scroll height.
                new_height = driver.execute_script(f"return document.getElementsByClassName('{container}')[0].scrollHeight")
                counter += 1
                print(counter, container, last_height, new_height)
                if new_height == last_height:
                    break
                else:
                    last_height = new_height

        #url = 'https://www.astegiudiziarie.it/Immobili/Ricerca-avanzata'
        #driver.get(url)

        driver.switch_to.window(driver.window_handles[0])
        print(driver.current_url)
        sleep(GENERAL_PAUSE_TIME)
        sleep(GENERAL_PAUSE_TIME)
        #driver.find_element(By.CLASS_NAME, 'avvia').click()#'Italy')
        #sleep(10)
        #driver.switch_to.window(driver.window_handles[0])
        #print(driver.current_url)
        
        
        '''
        #<a href="#" onclick="openEsitiVendite()">Esiti vendite</a>
        #driver.find_element(By.XPATH, "//a[contains(text(), 'Esiti vendite')]").click() #.send_keys(Keys.ENTER)
        element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Esiti vendite')]")))
        element.click()
        driver.implicitly_wait(5)
        '''

        #<a href="/">Immobili</a>
        element = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Immobili')]")))
        element.click()
        driver.implicitly_wait(GENERAL_PAUSE_TIME)
        
        ''' Selection is done manually! '''
        #<a class="button button-large btn-panoramiche" href="/Immobili/Ricerca-avanzata" title="Ricerca avanzata">Ricerca avanzata</a>
        #driver.find_element(By.XPATH, "//a[contains(text(), 'Ricerca avanzata')]").click() #.send_keys(Keys.ENTER)
        #driver.find_element(By.XPATH, "//a[contains(text(), 'Ricerca avanzata')]").send_keys(Keys.ENTER) #.click() #.send_keys(Keys.ENTER)
        #element = WebDriverWait(driver,30).until(EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Ricerca avanzata')]")))
        #element.click()    
        #driver.implicitly_wait(5)
        sleep(GENERAL_PAUSE_TIME)

        
        data_vendita_al = '01/05/2023'
        #<input type="text" class="ico-01 datepicker hasDatepicker" placeholder="Data vendita al" name="dataVenditaA" id="venditaAl_1" value="" readonly="readonly">
        element_data_vendita_al = driver.find_element(By.ID, "venditaAl_1")
        element_data_vendita_al.send_keys(data_vendita_al)
        sleep(GENERAL_PAUSE_TIME)

        #<button type="button" class="button home-bigger-elem btn-submit" id="btn_cerca_1">Cerca</button>
        driver.find_element(By.ID, "btn_cerca_1").send_keys(Keys.ENTER) #.click() #send_keys(Keys.ENTER)
        driver.implicitly_wait(GENERAL_PAUSE_TIME)

        #WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CLASS_NAME,'button-load-more-results'))).click()
        #element = driver.find_element(By.CLASS_NAME,'button-load-more-results')
        #driver.execute_script("arguments[0].scrollIntoView(true);")
        #element.click()

        _elements = driver.find_elements(By.CLASS_NAME, 'goto-detail')
        #listing-item')
        elements = {k: v.get_attribute('href') for k, v in enumerate(_elements)}
        for key in elements.keys():
            print(f"{key} -> {elements[key]}")
        filename = 'astegiudiziarie.json'
        with open(filename, 'w') as f:
            dump(elements, f, indent=4)
        sleep(60)
    
        filename = '/home/data/property_scraper/demos/downloads/astegiudiziarie/test.html'
        with open(filename, 'w') as f:
            f.write(driver.page_source)

        #driver.find_element(By.CLASS_NAME, 'fa-map-o').click()
        #sleep(2)
        #driver.find_element(By.CLASS_NAME, 'fa-th-list').click()
        #sleep(2)

        response = Selector(text=driver.page_source)
        
        listings = response.xpath('//div[@class="single_box_asta"]')
        for listing in listings:
            l = ItemLoader(item=AstegiudiziarieItem(), selector=listing)
            l.default_output_processor = TakeFirst()

            l.add_xpath('title', './/h4[@class="box_title"]/text()')
            l.add_xpath('location', './/div[@class="box_dettagli"]/p[1]/span/text()')
            l.add_xpath('price', './/div[@class="box_dettagli"]/p[2]/span/text()')
            l.add_xpath('description', './/div[@class="box_dettagli"]/p[3]/text()')

            yield l.load_item()
        
        driver.quit()

        sleep(GENERAL_PAUSE_TIME)
        
        return response
   
    def parse(self, response):       
        self.driver.get(response.url)
        sel = HtmlResponse(url=response.url, body=self.driver.page_source, encoding='utf-8')
       
        location = 'italia'  # self.get_location(response.url)
        number_of_results = int(response.xpath('//span[@class="results_number"]/text()').get())
        page_id = self.get_page_id(response.url)
        maximum_number_of_results_per_page = self.get_maximum_number_of_results_per_page(response.url)
        number_of_pages = self.get_number_of_pages(number_of_results, maximum_number_of_results_per_page)
        number_of_results_per_page = self.get_number_of_results_per_page(number_of_results, number_of_pages,
                                                                         maximum_number_of_results_per_page)

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
        search_loader = ItemLoader(item=self.search, response=response)
        search_loader.add_value('basename', basename)
        search_loader.add_value('filename', filename)
        search_loader.add_value('id', os.path.splitext(basename)[0])
        search_loader.add_value('is_downloaded', False)
        search_loader.add_value('is_relative_href_fixed', False)
        search_loader.add_value('location', location)
        search_loader.add_value('number_of_results', number_of_results)
        search_loader.add_value('number_of_pages', number_of_pages)
        search_loader.add_value('number_of_results_per_page', number_of_results_per_page[page_id - 1])
        search_loader.add_value('page_id', page_id)
        search_loader.add_value('response_status_code', 200)
        search_loader.add_value('spider_name', self.name)
        search_loader.add_value('url', url)
        search_loader.add_value('url_localhost', url_localhost)
        yield search_loader.load_item()
        
        cards = response.xpath("//div[@class='listing-item']")
        for card in cards:
            self.property = AsteGiudiziarieSearchPropertyItem()
            property_loader = ItemLoader(item=self.property, selector=card)
            for key in self.property.items['css'].keys():
                property_loader.add_css(key, self.property.items['css'][key])
            for key in self.property.items['xpath'].keys():
                property_loader.add_xpath(key, self.property.items['xpath'][key])
            filename = get_filename_from_identifier(url)#, keys, root)
            basename = os.path.basename(filename)
            if LOCALHOST_URL_ROOTNAME not in url:
                url_localhost = os.path.join(LOCALHOST_URL_ROOTNAME, self.name.split('_')[0], basename)
            else:
                url_localhost = url
            property_loader.add_value('basename', basename)
            property_loader.add_value('filename', filename)
            property_loader.add_value('id', os.path.splitext(basename)[0])
            property_loader.add_value('spider_name', self.name)
            property_loader.add_value('search_id', search_url)
            property_loader.add_value('url', url)
            property_loader.add_value('url_localhost', url_localhost)
            property_loader.add_value('is_downloaded', False)
            property_loader.add_value('is_relative_href_fixed', False)
            property_loader.add_value('response_status_code', 200)
            yield property_loader.load_item()
        
    def closed(self, reason):
        self.driver.quit()

    '''
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
    def get_number_of_results_per_page(number_of_results: int, number_of_pages: int,
                                       maximum_number_of_results_per_page: int):
        if number_of_results == number_of_pages * maximum_number_of_results_per_page:
            number_of_results_per_page = [maximum_number_of_results_per_page] * number_of_pages
        else:
            number_of_results_per_page = [maximum_number_of_results_per_page] * (number_of_pages - 1) + [
                number_of_results % maximum_number_of_results_per_page]
        return number_of_results_per_page
    '''