# -*- coding: utf-8 -*-

import logging
import sys

from autologging import logged, traced
from datetime import datetime
import json
import os
import scrapy
from scrapy import Spider
from scrapy.loader import ItemLoader
import yaml

from property_scraper.auctionhouse.spiders.search_property import AuctionHouseSearchPropertySpider


@traced
@logged
class AuctionHousePastSearchPropertySpider(AuctionHouseSearchPropertySpider):
    '''
        Résultats des adjudications
    '''
    name = 'auctionhouse_pastsearchproperty'
    start_urls = [
        'https://www.auctionhouse.co.uk/auction/past-auctions',
        #'https://www.auctionhouse.co.uk/southwest/auction/past-auctions',
        
    ]


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
    process.crawl(InfoEncheresPastSearchPropertySpider)

    # Start the crawler process    
    process.start()
