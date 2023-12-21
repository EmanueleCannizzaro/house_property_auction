# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
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
#from urllib.parse import urljoin
import yaml

from property_scraper import DRIVER_PATH, LOCALHOST_URL_ROOTNAME, RECROWD_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.recrowd.items import RecrowdProjectsItem, RecrowdProjectsModel
##from property_scraper.pvp.pipelines import get_location
from property_scraper.selenium.spiders.selenium import SeleniumSpider


@traced
@logged
class RecrowdProjectsSpider(SeleniumSpider):
    DRIVER_PATH = DRIVER_PATH #os.path.join(os.path.expanduser('~'), 'bin', 'chromedriver', '114.0.5735.90', 'chromedriver')
    MAXIMUM_WAITING_TIME = 20
    GENERAL_PAUSE_TIME = 2

    name = 'recrowd_projects'
    allowed_domains = ['www.recrowd.com']
    start_urls = ['https://www.recrowd.com/it/progetti']

    def __init__(self, name:str='selenium_spider'):
        self.name = name        
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
            self.projects = RecrowdProjectsItem()
            projects_loader = ItemLoader(item=self.projects, selector=card)
            for key in self.projects.items['css'].keys():
                projects_loader.add_css(key, self.projects.items['css'][key])
            for key in self.projects.items['xpath'].keys():
                projects_loader.add_xpath(key, self.projects.items['xpath'][key])
            
            projects_data = projects_loader.load_item()
            projects_model = RecrowdProjectsModel(**projects_data)
        
            yield projects_data


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
    process.crawl(RecrowdProjectsSpider)

    # Start the crawler process    
    process.start()
