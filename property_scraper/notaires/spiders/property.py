# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
from glob import glob
#import json
import os
import scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
from scrapy.selector import Selector
#from time import sleep
#from tqdm.auto import tqdm

from property_scraper import ROOT_FOLDER, get_latest_file_mtime
#from property_scraper import LOCALHOST_URL_ROOTNAME, PVP_URL_ROOTNAME, ROOT_FOLDER, get_filename_from_identifier, get_unique_filename
from property_scraper.infoencheres.items import InfoEncheresPropertyItem, InfoEncheresPropertyModel


@traced
@logged
class InfoEncheresPropertySpider(Spider):
    name = 'infoencheres_property'
    WEBSITE = name.split('_')[0]
    
    allowed_domains = ['localhost:8000', 'www.info-encheres.com']
    
    ## Filter the list of files only to ones more recent than the output file
    ofilenames = glob(f'/home/data/property_scraper/demos/{name}_*.csv')
    ofilename_mtime = get_latest_file_mtime(ofilenames)
    
    filenames = glob(os.path.join(ROOT_FOLDER, WEBSITE, f'{WEBSITE}_property_*.html'))
    print(f"There are {len(filenames)} listed properties.")
    #print(filenames)
    #filenames = ['infoencheres_property_5052.html']
    #start_urls = [f'http://localhost:8000/infoencheres/{os.path.basename(x)}' for x in filenames[:1]]
    #start_urls = [f'http://localhost:8000/infoencheres/{os.path.basename(x)}' for x in filenames if (os.path.getctime(x) > ofilename_mtime)]
    start_urls = []
    for x in filenames :
        if os.path.getctime(x) > ofilename_mtime:
            start_urls.append(f'http://localhost:8000/infoencheres/{os.path.basename(x)}')
    print(f"There are {len(start_urls)} new properties to scrape.")
    
    search_datetime = datetime.now().strftime("%Y%m%d%H%M%S")
    is_first_page = True

    def parse(self, response):
        selector = Selector(response)
        self.property = InfoEncheresPropertyItem()
        property_loader = ItemLoader(item=self.property, selector=selector)
        for key in self.property.items['css'].keys():
            if isinstance(self.property.items['css'][key], list):
                for item in self.property.items['css'][key]:
                    property_loader.add_css(key, item)
            else:
                property_loader.add_css(key, self.property.items['css'][key])
        for key in self.property.items['xpath'].keys():
            if isinstance(self.property.items['xpath'][key], list):
                for item in self.property.items['xpath'][key]:
                    property_loader.add_xpath(key, item)
            else:
                property_loader.add_xpath(key, self.property.items['xpath'][key])
        
        property_data = property_loader.load_item()
        #property_model = InfoEncheresPropertyModel(**property_data)
        yield property_data


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
    process.crawl(InfoEncheresPropertySpider)

    # Start the crawler process    
    process.start()
