# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
import json
import os
import scrapy
#from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
#from scrapy.spiders import Spider # CrawlSpider, Rule
from selenium.webdriver import Chrome, ChromeOptions #, Firefox, FirefoxOptions
from selenium.webdriver.chrome.service import Service
#from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
#from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
from tqdm.auto import tqdm
from urllib.parse import urljoin
import yaml

from property_scraper import DRIVER_PATH, LOCALHOST_URL_ROOTNAME, RECROWD_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.recrowd.items import RecrowdProjectsItem, RecrowdProjectsModel, RecrowdProjectItem, RecrowdProjectModel
from property_scraper.selenium.spiders.selenium import SeleniumSpider


@traced
@logged
class RecrowdProjectSpider(SeleniumSpider):
    DRIVER_PATH = DRIVER_PATH #os.path.join(os.path.expanduser('~'), 'bin', 'chromedriver', '114.0.5735.90', 'chromedriver')
    MAXIMUM_WAITING_TIME = 20
    GENERAL_PAUSE_TIME = 2

    name = 'recrowd_project'
    allowed_domains = ['www.recrowd.com']
    start_urls = ['https://www.recrowd.com/it/progetti/dettaglio']

    def __init__(self, name:str='selenium_spider'):
        self.name = name
        self.accept_policy_flag = False #True
        self.init_driver()

    def init_driver(self):
        options = ChromeOptions()
        self.driver = Chrome(service=Service(self.DRIVER_PATH), options=options)
        self.driver.maximize_window()
        self.wait = WebDriverWait(self.driver, self.MAXIMUM_WAITING_TIME).until
    
    def sleep(self, factor:float=1.0):
        self.driver.implicitly_wait(factor * self.GENERAL_PAUSE_TIME)
        sleep(factor * self.GENERAL_PAUSE_TIME)

    def closed(self, reason):
        self.driver.quit()

    def parse(self, response):         
        self.driver.get(response.url)
        self.sleep()
        # Use Selenium to interact with the webpage
        # Extract data using Selenium
        # ...
        
        if self.accept_policy_flag:
            xpath = '//a[@class="CybotCookiebotDialogBodyButton"][contains(text(), "Usa solo i cookie necessari")]'
            button = self.wait(EC.element_to_be_clickable((By.XPATH, xpath)))
            button.click()
            self.sleep()

        # Create a new Scrapy response using the source code obtained from Selenium
        body = self.driver.page_source
        filename = 'test.txt'
        with open(filename, 'w') as f:
            f.write(body)
        #self.sleep(10)

        selector = Selector(text=body)
        cards = selector.xpath('//a[contains(@class, "project--card")]')
        print(f'There are {len(cards)} cards.')

        pbar = tqdm(cards)
        for card in pbar:
            projects = RecrowdSearchProjectsItem()
            projects_loader = ItemLoader(item=projects, selector=card)
            key = 'url'
            projects_loader.add_xpath(key, projects.items['xpath'][key])
            
            projects_data = projects_loader.load_item()
            #projects_model = RecrowdProjectsModel(**projects_data)
            
            url = urljoin(response.url, projects_data['url'])
            print(url)
            yield response.follow(url, callback=self.parse_project)
            #break

    def parse_project(self, response):         
        self.driver.get(response.url)
        self.sleep()
        # Use Selenium to interact with the webpage
        # Extract data using Selenium
        # ...

        # Create a new Scrapy response using the source code obtained from Selenium
        body = self.driver.page_source
        filename = 'test_project.txt'
        with open(filename, 'w') as f:
            f.write(body)
        #self.sleep(10)
        
        selector = Selector(text=body)
        self.project = RecrowdProjectItem()
        project_loader = ItemLoader(item=self.project, selector=selector)
        for key in self.project.items['css'].keys():
            project_loader.add_css(key, self.project.items['css'][key])
        for key in self.project.items['xpath'].keys():
            project_loader.add_xpath(key, self.project.items['xpath'][key])
        
        project_data = project_loader.load_item()
        #project_model = RecrowdProjectModel(**project_data)
    
        yield project_data


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
    process.crawl(RecrowdProjectSpider)

    # Start the crawler process    
    process.start()
